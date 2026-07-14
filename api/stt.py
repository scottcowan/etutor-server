from fastapi import APIRouter, UploadFile, File, Header, HTTPException
from pydantic import BaseModel
import tempfile, os

from config.settings import get_settings

router = APIRouter()


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
    from faster_whisper import WhisperModel
    settings = get_settings()
    model = WhisperModel(settings.whisper_model, device="cpu", compute_type="int8")
    segments, _ = model.transcribe(path, beam_size=1)
    return " ".join(s.text.strip() for s in segments)


async def _transcribe_openai(path: str) -> str:
    import openai
    settings = get_settings()
    client = openai.AsyncOpenAI(api_key=settings.openai_api_key)
    with open(path, "rb") as f:
        result = await client.audio.transcriptions.create(model="whisper-1", file=f)
    return result.text
