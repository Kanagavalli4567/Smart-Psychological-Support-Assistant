# Optional: requires `pip install faster-whisper`
# If not installed, server will gracefully fallback.

def transcribe_audio(filepath: str, model_size: str = "small") -> str:
    try:
        from faster_whisper import WhisperModel
    except Exception as e:
        raise RuntimeError("faster-whisper not installed. Run: pip install faster-whisper") from e

    model = WhisperModel(model_size, device="cpu", compute_type="int8")
    segments, info = model.transcribe(filepath, beam_size=5)
    text = " ".join(seg.text.strip() for seg in segments).strip()
    return text
