import os

OLLAMA_URL = os.environ.get("PLUTO_OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.environ.get("PLUTO_OLLAMA_MODEL", "llama3.2-vision")

RECEIPTS_DIR = os.environ.get("PLUTO_RECEIPTS_DIR", "receipts")

ALLOWED_IMAGE_EXT = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp"}
