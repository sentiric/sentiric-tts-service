import os
import time
import structlog
from fastapi import FastAPI, Request, Response
from pydantic import BaseModel
from dotenv import load_dotenv
import logging
from structlog.contextvars import bind_contextvars, clear_contextvars

# --- Konfigürasyon ve Loglama Kurulumu ---
load_dotenv()

ENV = os.getenv("ENV", "production")
LOG_LEVEL = logging.INFO

structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.StackInfoRenderer(),
        structlog.dev.set_exc_info,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.dev.ConsoleRenderer() if ENV == "development" else structlog.processors.JSONRenderer(),
    ],
    wrapper_class=structlog.make_filtering_bound_logger(LOG_LEVEL),
    context_class=dict,
    logger_factory=structlog.PrintLoggerFactory(),
    cache_logger_on_first_use=True,
)

log = structlog.get_logger(service="tts-service")

app = FastAPI()

# --- Middleware: Her istek için otomatik loglama ---
@app.middleware("http")
async def logging_middleware(request: Request, call_next) -> Response:
    clear_contextvars()
    start_time = time.perf_counter()
    
    call_id = request.headers.get("X-Call-ID", "N/A")
    trace_id = request.headers.get("X-Trace-ID", "N/A")
    bind_contextvars(call_id=call_id, trace_id=trace_id)

    response = await call_next(request)
    process_time = (time.perf_counter() - start_time) * 1000
    
    log.info(
        "http.request.completed",
        http_method=request.method,
        http_path=request.url.path,
        http_status_code=response.status_code,
        duration_ms=f"{process_time:.2f}",
    )
    return response

# --- API Modelleri ---
class SynthesizeRequest(BaseModel):
    text: str

class SynthesizeResponse(BaseModel):
    audio_path: str

# --- API Endpoint'leri ---
@app.post("/synthesize", response_model=SynthesizeResponse)
async def synthesize_speech(request: SynthesizeRequest):
    log.info("tts_service.synthesize.request_received", text=request.text, text_length=len(request.text))
    
    # ŞİMDİLİK, her zaman aynı "sistem hatası" ses dosyasını döndürerek
    # boru hattını test edeceğiz. Bu, gerçek TTS motoru entegre edilene kadar
    # agent-service'in doğru çalıştığını doğrulamamızı sağlar.
    mock_audio_path = "audio/tr/system_error.wav"
    
    log.info("tts_service.synthesize.mock_response_sent", audio_path=mock_audio_path)
    return SynthesizeResponse(audio_path=mock_audio_path)

@app.get("/health")
async def health_check():
    health_status = {"status": "ok"}
    log.info("health_check.performed", **health_status)
    return {"status": "ok"}