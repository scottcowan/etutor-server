from fastapi import APIRouter, UploadFile, File, Header, HTTPException
from pydantic import BaseModel
import asyncio
import tempfile, os
from functools import partial

from config.settings import get_settings

router = APIRouter()

# Module-level singleton — loaded once at first use, reused across requests.
_whisper_model = None


def _get_whisper_model():
    global _whisper_model
    if _whisper_model is None:
        from faster_whisper import WhisperModel
        settings = get_settings()
        _whisper_model = WhisperModel(settings.whisper_model, device="cpu", compute_type="int8")
    return _whisper_model


class TranscriptionResponse(BaseModel):
    text: str


@router.post("/audio/transcriptions", response_model=TranscriptionResponse)
async def transcribe(
    file: UploadFile = File(...),
    x_device_id: str = Header(None),
):
    settings = get_settings()

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    try:
        if settings.stt_provider == "local":
            text = await _transcribe_local(tmp_path)
        else:
            text = await _transcribe_openai(tmp_path)
    finally:
        os.unlink(tmp_path)

    return TranscriptionResponse(text=text)


async def _transcribe_local(path: str) -> str:
    """Run faster-whisper transcription in a thread executor to avoid blocking the event loop."""
    def _sync_transcribe():
        model = _get_whisper_model()
        segments, _ = model.transcribe(path, beam_size=1)
        return " ".join(s.text.strip() for s in segments)

    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _sync_transcribe)


async def _transcribe_openai(path: str) -> str:
    import openai
    settings = get_settings()
    client = openai.AsyncOpenAI(api_key=settings.openai_api_key)
    with open(path, "rb") as f:
        result = await client.audio.transcriptions.create(model="whisper-1", file=f)
    return result.text
