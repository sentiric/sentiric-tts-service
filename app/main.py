# app/main.py
from fastapi import FastAPI, Response, HTTPException
from pydantic import BaseModel, HttpUrl
from contextlib import asynccontextmanager
import structlog
from typing import Optional

from app.services.tts_service import tts_engine
from app.core.config import settings

logger = structlog.get_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Uygulama başlıyor...")
    tts_engine.load_model()
    logger.info("Uygulama hazır ve istekleri kabul ediyor.")
    yield
    logger.info("Uygulama kapanıyor.")

app = FastAPI(title=settings.PROJECT_NAME, version="1.1.0", lifespan=lifespan)

class SynthesizeRequest(BaseModel):
    text: str
    language: str = "tr"
    # --- YENİ: Opsiyonel speaker_wav_url alanı ---
    # Bu alan, varsayılan sesi ezmek için kullanılır.
    speaker_wav_url: Optional[HttpUrl] = None

@app.post("/api/v1/synthesize", response_class=Response)
async def synthesize(request: SynthesizeRequest):
    # speaker_wav_url'i string'e çevirerek tts_engine'e gönderiyoruz. None ise None gider.
    speaker_wav_path = str(request.speaker_wav_url) if request.speaker_wav_url else None

    if not tts_engine.is_ready():
        raise HTTPException(status_code=503, detail="TTS motoru şu an kullanılamıyor.")

    try:
        wav_bytes = await tts_engine.synthesize(request.text, request.language, speaker_wav_path)
        return Response(content=wav_bytes, media_type="audio/wav")
    except Exception as e:
        logger.error("Sentezleme sırasında beklenmedik bir hata oluştu.", error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=f"Ses üretimi sırasında bir hata oluştu: {e}")

@app.get("/health")
def health_check():
    is_ready = tts_engine.is_ready()
    return {
        "status": "ok" if is_ready else "degraded",
        "details": {
            "tts_engine_loaded": is_ready
        }
    }