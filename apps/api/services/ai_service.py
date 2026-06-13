"""
Pluto extraction service — Ollama / OpenAI-compatible backends.

Sends a base64-encoded receipt image to a local vision model
(default: llama3.2-vision via Ollama) and returns a strict JSON extraction.

Supports:
- Ollama native API (/api/generate)
- OpenAI-compatible API (/v1/chat/completions, e.g. 9router)

Returns an `ExtractionResult` dataclass with `data`, `errors`, `raw_response`,
and `backend` fields. Never raises — partial data is preferred so the UI
can prompt for missing fields manually.
"""
from __future__ import annotations

import base64
import json
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

import requests

from core.config import OLLAMA_MODEL, OLLAMA_URL

OLLAMA_TIMEOUT = 30

def _backend_type(url: str) -> str:
    u = url.rstrip("/")
    if "/v1" in u or "/chat/completions" in u:
        return "openai"
    return "ollama"

_BACKEND = _backend_type(OLLAMA_URL)

if _BACKEND == "openai":
    _ENDPOINT = f"{OLLAMA_URL.rstrip('/')}/chat/completions"
    if "/v1" not in _ENDPOINT:
        _ENDPOINT = f"{OLLAMA_URL.rstrip('/')}/v1/chat/completions"
else:
    _ENDPOINT = f"{OLLAMA_URL.rstrip('/')}/api/generate"

OLLAMA_PROMPT = """You are a receipt analyzer. Extract expense information from this receipt image.

Return ONLY valid JSON with these fields:
- date: The purchase date (YYYY-MM-DD format)
- amount: The total amount spent (just the number)
- currency: The currency code (e.g., USD, EUR, VND, JPY)
- merchant: The store or merchant name
- address: The store's street address, if visible (else null)
- phone: The store's phone number, if visible (else null)
- category: Best guess at expense category (Food & Dining, Shopping, Transportation, Housing, Health, Entertainment, Utilities, Other)
- items: Array of {name, price} for each line item on the receipt (empty array if not visible)
- confidence: How confident you are (high/medium/low)

If you cannot read something, use null and explain why.
"""

_JSON_FENCE = re.compile(r"^```(?:json)?\s*|\s*```$", re.IGNORECASE)
_JSON_OBJECT = re.compile(r"\{.*\}", re.DOTALL)


@dataclass
class ExtractionResult:
    data: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    raw_response: str = ""
    backend: str = ""

    @property
    def ok(self) -> bool:
        return not self.errors

    def to_dict(self) -> Dict[str, Any]:
        return {
            "data": self.data,
            "errors": self.errors,
            "raw_response": self.raw_response,
            "backend": self.backend,
        }


def _encode_image(image_path: str) -> str:
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


def _parse_json_response(raw: str) -> Optional[Dict[str, Any]]:
    if not raw:
        return None
    cleaned = _JSON_FENCE.sub("", raw.strip())
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        match = _JSON_OBJECT.search(cleaned)
        if match:
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError:
                return None
        return None


def _coerce(value: Any, cast):
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return cast(value)
    try:
        return cast(value)
    except (TypeError, ValueError):
        return None


def _backend_alive() -> bool:
    if _BACKEND == "openai":
        try:
            resp = requests.get(f"{OLLAMA_URL.rstrip('/')}/v1/models", timeout=2)
            return resp.ok
        except requests.RequestException:
            return False
    try:
        resp = requests.get(f"{OLLAMA_URL.rstrip('/')}/api/tags", timeout=2)
        return resp.ok
    except requests.RequestException:
        return False


def extract_receipt_data(image_path: str) -> ExtractionResult:
    """
    Public entry point. Reads the image, calls Ollama, and returns the
    parsed extraction. Returns an error result on any failure — never raises.
    """
    result = ExtractionResult(backend=_BACKEND)

    if not _backend_alive():
        result.errors.append(
            f"AI backend is not reachable at {OLLAMA_URL}."
        )
        return result

    try:
        base64_image = _encode_image(image_path)
    except OSError as exc:
        result.errors.append(f"Could not read image: {exc}")
        return result

    if _BACKEND == "openai":
        b64_data_url = f"data:image/jpeg;base64,{base64_image}"
        payload = {
            "model": OLLAMA_MODEL,
            "messages": [{
                "role": "user",
                "content": [
                    {"type": "text", "text": OLLAMA_PROMPT},
                    {"type": "image_url", "image_url": {"url": b64_data_url}},
                ],
            }],
            "temperature": 0,
            "max_tokens": 1024,
            "stream": False,
        }
    else:
        payload = {
            "model": OLLAMA_MODEL,
            "prompt": OLLAMA_PROMPT,
            "images": [base64_image],
            "format": "json",
            "stream": False,
        }

    try:
        response = requests.post(_ENDPOINT, json=payload, timeout=OLLAMA_TIMEOUT)
        response.raise_for_status()
    except requests.Timeout:
        result.errors.append("AI request timed out.")
        return result
    except requests.ConnectionError as exc:
        result.errors.append(f"Could not reach AI backend: {exc}")
        return result
    except requests.HTTPError as exc:
        result.errors.append(f"AI backend returned an error: {exc}")
        return result
    except requests.RequestException as exc:
        result.errors.append(f"AI request failed: {exc}")
        return result

    try:
        body = response.json()
    except ValueError:
        result.errors.append("AI backend returned a non-JSON envelope.")
        result.raw_response = response.text[:500]
        return result

    if _BACKEND == "openai":
        raw = body.get("choices", [{}])[0].get("message", {}).get("content", "")
    else:
        raw = body.get("response", "")
    result.raw_response = raw

    parsed = _parse_json_response(raw)
    if parsed is None:
        result.errors.append("Ollama response could not be parsed as JSON.")
        return result

    items_raw = parsed.get("items") or []
    items = []
    for it in items_raw:
        if not isinstance(it, dict):
            continue
        name = it.get("name")
        price = _coerce(it.get("price"), float)
        if name and price is not None:
            items.append({"name": str(name), "price": price})

    result.data = {
        "date": parsed.get("date"),
        "amount": _coerce(parsed.get("amount"), float),
        "currency": parsed.get("currency") or "USD",
        "merchant": parsed.get("merchant"),
        "address": parsed.get("address"),
        "phone": parsed.get("phone"),
        "category": parsed.get("category") or "Other",
        "items": items,
        "confidence": parsed.get("confidence"),
    }

    if result.data["amount"] is None:
        result.errors.append("AI did not return a usable amount.")
    if not result.data["merchant"]:
        result.errors.append("AI did not return a merchant name.")
    if not result.data["date"]:
        result.errors.append("AI did not return a date.")

    return result
