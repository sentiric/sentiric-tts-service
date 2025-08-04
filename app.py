# DOSYA: sentiric-tts-service/app.py
import structlog
from fastapi import FastAPI
from pydantic import BaseModel

log = structlog.get_logger()
app = FastAPI()

class SynthesizeRequest(BaseModel):
    text: str

class SynthesizeResponse(BaseModel):
    audio_path: str

@app.post("/synthesize", response_model=SynthesizeResponse)
async def synthesize_speech(request: SynthesizeRequest):
    log.info("tts_request_received", text=request.text)
    
    # ŞİMDİLİK, her zaman aynı "sistem hatası" ses dosyasını döndürerek
    # boru hattını test edeceğiz. Bu, gerçek TTS motoru entegre edilene kadar
    # agent-service'in doğru çalıştığını doğrulamamızı sağlar.
    mock_audio_path = "audio/tr/system_error.wav"
    
    log.info("tts_mock_response_sent", audio_path=mock_audio_path)
    return SynthesizeResponse(audio_path=mock_audio_path)

@app.get("/health")
async def health_check():
    return {"status": "ok"}