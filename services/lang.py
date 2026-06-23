import re
from langdetect import detect, DetectorFactory
DetectorFactory.seed = 0

_TAMIL_RE = re.compile(r"[\u0B80-\u0BFF]")  # Tamil unicode range
_DEVANAGARI_RE = re.compile(r"[\u0900-\u097F]")

def detect_lang(text: str) -> str:
    t = text.strip()
    if _TAMIL_RE.search(t):
        return "ta"
    if _DEVANAGARI_RE.search(t):
        return "hi"
    try:
        lang = detect(t)
        if lang in ["ta", "en", "hi", "ml", "te", "kn", "id", "ms"]:
            return lang
        return "en"
    except Exception:
        return "en"
