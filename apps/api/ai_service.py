"""
Ollama-based receipt extraction.

The vision model may be unavailable, slow, or hallucinate. This module
keeps extraction best-effort and reports what failed so the caller can
prompt the user for manual entry on the missing fields.
"""
from __future__ import annotations

import base64
import json
import os
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

import requests


# Defaults match the spec; can be overridden via env or by mutating the
# module-level constants before calling extract_receipt_data.
OLLAMA_URL = os.environ.get("PLUTO_OLLAMA_URL", "http://localhost:11434")
OLLAMA_ENDPOINT = f"{OLLAMA_URL.rstrip('/')}/api/generate"
MODEL = os.environ.get("PLUTO_OLLAMA_MODEL", "llama3.2-vision")
REQUEST_TIMEOUT = float(os.environ.get("PLUTO_OLLAMA_TIMEOUT", "30"))

# Per the spec — keep the model focused on the few fields we actually need.
PROMPT = """You are a receipt analyzer. Extract expense information from this receipt image.

Return ONLY valid JSON with these fields:
- date: The purchase date (YYYY-MM-DD format)
- amount: The total amount spent (just the number)
- currency: The currency code (e.g., USD, EUR)
- merchant: The store or merchant name
- confidence: How confident you are (high/medium/low)

If you cannot read something, use null and explain why.
"""


@dataclass
class ExtractionResult:
    """Result of an extraction attempt — partial data is acceptable."""

    data: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    raw_response: str = ""

    @property
    def ok(self) -> bool:
        return not self.errors

    def to_dict(self) -> Dict[str, Any]:
        return {
            "data": self.data,
            "errors": self.errors,
            "raw_response": self.raw_response,
        }


def encode_image(image_path: str) -> str:
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


# Some Ollama models wrap the JSON in ```json fences or add a trailing
# sentence. Be permissive in what we accept.
_JSON_FENCE = re.compile(r"^```(?:json)?\s*|\s*```$", re.IGNORECASE)
_JSON_OBJECT = re.compile(r"\{.*\}", re.DOTALL)


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


def _coerce_value(value: Any, cast):
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return cast(value)
    try:
        return cast(value)
    except (TypeError, ValueError):
        return None


def _normalize(parsed: Dict[str, Any]) -> Dict[str, Any]:
    """Apply spec-shaped defaults and cast amounts/dates where possible."""
    return {
        "date": parsed.get("date"),
        "amount": _coerce_value(parsed.get("amount"), float),
        "currency": parsed.get("currency") or "USD",
        "merchant": parsed.get("merchant"),
        "confidence": parsed.get("confidence"),
    }


def _ollama_alive() -> bool:
    """Cheap health check — Ollama serves a 200 on /api/tags when up."""
    try:
        resp = requests.get(f"{OLLAMA_URL.rstrip('/')}/api/tags", timeout=2)
        return resp.ok
    except requests.RequestException:
        return False


def extract_receipt_data(
    image_path: str,
    *,
    model: Optional[str] = None,
    timeout: Optional[float] = None,
) -> ExtractionResult:
    """
    Send `image_path` to Ollama and return a structured result.

    Never raises — partial data is preferred to no data so the UI can
    fall back to manual entry on the missing fields, per the spec.
    """
    result = ExtractionResult()

    if not os.path.exists(image_path):
        result.errors.append(f"Image not found: {image_path}")
        return result

    if not _ollama_alive():
        result.errors.append(
            f"Ollama is not reachable at {OLLAMA_URL}. "
            "Start it with `ollama serve` or set PLUTO_OLLAMA_URL."
        )
        # Fall through: we still try the request below, in case the
        # health check lost a race with a freshly-started server.

    try:
        base64_image = encode_image(image_path)
    except OSError as exc:
        result.errors.append(f"Could not read image: {exc}")
        return result

    payload = {
        "model": model or MODEL,
        "prompt": PROMPT,
        "images": [base64_image],
        "format": "json",
        "stream": False,
    }

    try:
        response = requests.post(
            OLLAMA_ENDPOINT,
            json=payload,
            timeout=timeout or REQUEST_TIMEOUT,
        )
        response.raise_for_status()
    except requests.Timeout:
        result.errors.append("Ollama request timed out.")
        return result
    except requests.ConnectionError as exc:
        result.errors.append(f"Could not reach Ollama: {exc}")
        return result
    except requests.HTTPError as exc:
        result.errors.append(f"Ollama returned an error: {exc}")
        return result
    except requests.RequestException as exc:
        result.errors.append(f"Ollama request failed: {exc}")
        return result

    try:
        body = response.json()
    except ValueError:
        result.errors.append("Ollama returned a non-JSON envelope.")
        result.raw_response = response.text[:500]
        return result

    raw = body.get("response", "")
    result.raw_response = raw

    parsed = _parse_json_response(raw)
    if parsed is None:
        result.errors.append(
            "Ollama response could not be parsed as JSON. "
            "The model may have refused or hallucinated."
        )
        return result

    normalized = _normalize(parsed)
    if normalized.get("amount") is None:
        result.errors.append("AI did not return a usable amount.")
    if not normalized.get("merchant"):
        result.errors.append("AI did not return a merchant name.")
    if not normalized.get("date"):
        result.errors.append("AI did not return a date.")

    result.data = normalized
    return result
