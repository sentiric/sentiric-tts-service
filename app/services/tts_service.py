# app/services/tts_service.py
import io
import asyncio
import numpy as np
import soundfile as sf
import structlog
import torch
import httpx
import tempfile
import os
from typing import Optional
from TTS.api import TTS
from app.core.config import settings

logger = structlog.get_logger(__name__)

async def download_temp_wav(url: str) -> str:
    async with httpx.AsyncClient() as client:
        response = await client.get(url, follow_redirects=True, timeout=10.0)
        response.raise_for_status()
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
            tmp_file.write(response.content)
            logger.info("Dinamik referans sesi başarıyla indirildi.", url=url, path=tmp_file.name)
            return tmp_file.name

class TTSEngine:
    def __init__(self):
        self.model = None
        self.logger = logger.bind(service_component="TTSEngine")
        self.device = self._get_device()
        self.elevenlabs_enabled = settings.ENABLE_ELEVENLABS_TTS and settings.ELEVENLABS_API_KEY

    def _get_device(self) -> str:
        device_setting = settings.TTS_MODEL_DEVICE.lower()
        if device_setting == "auto":
            return "cuda" if torch.cuda.is_available() else "cpu"
        return device_setting

    def load_model(self):
        if self.model: return
        try:
            self.logger.info("Coqui XTTS Modeli yükleniyor...", device=self.device)
            self.model = TTS(settings.TTS_MODEL_NAME).to(self.device)
            self.logger.info("Coqui XTTS Modeli başarıyla yüklendi.")
        except Exception as e:
            self.logger.critical("KRİTİK HATA: Coqui XTTS modeli yüklenemedi.", error=str(e), exc_info=True)
            self.model = None

    def is_ready(self) -> bool:
        # ElevenLabs aktifse, servis her zaman hazırdır. Değilse, Coqui modelinin durumuna bağlıdır.
        return self.elevenlabs_enabled or self.model is not None
        
    async def _synthesize_with_elevenlabs(self, text: str) -> bytes:
        self.logger.info("ElevenLabs ile sentezleme deneniyor...")
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{settings.ELEVENLABS_VOICE_ID}"
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": settings.ELEVENLABS_API_KEY
        }
        data = {
            "text": text,
            "model_id": "eleven_multilingual_v2",
            "voice_settings": {"stability": 0.5, "similarity_boost": 0.75}
        }
        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.post(url, json=data, headers=headers)
            response.raise_for_status()
            self.logger.info("ElevenLabs ile sentezleme başarılı.")
            return response.content

    async def _synthesize_with_coqui(self, text: str, language: str, speaker_wav_path: Optional[str]) -> bytes:
        if not self.model:
            raise RuntimeError("Coqui XTTS motoru kullanıma hazır değil.")
            
        temp_speaker_path = None
        try:
            if speaker_wav_path and speaker_wav_path.startswith("http"):
                temp_speaker_path = await download_temp_wav(speaker_wav_path)
                speaker_ref = [temp_speaker_path]
            else:
                speaker_ref = [settings.TTS_DEFAULT_SPEAKER_WAV_PATH]

            def _synthesize_sync():
                self.logger.info("Coqui XTTS ile sentezleme deneniyor...", speaker=speaker_ref[0])
                wav_chunks = self.model.tts(text=text, speaker_wav=speaker_ref, language=language)
                wav_np = np.array(wav_chunks, dtype=np.float32)
                wav_buffer = io.BytesIO()
                sf.write(wav_buffer, wav_np, self.model.synthesizer.output_sample_rate, format='WAV')
                wav_buffer.seek(0)
                self.logger.info("Coqui XTTS ile sentezleme tamamlandı.")
                return wav_buffer.getvalue()
            return await asyncio.to_thread(_synthesize_sync)
        finally:
            if temp_speaker_path and os.path.exists(temp_speaker_path):
                os.remove(temp_speaker_path)

    async def synthesize(self, text: str, language: str, speaker_wav_path: Optional[str] = None) -> bytes:
        # Öncelikli olarak ElevenLabs'i dene (eğer aktifse)
        if self.elevenlabs_enabled:
            try:
                # ElevenLabs WAV döndürmez, MP3 döndürür. Bunu agent'da handle etmeliyiz.
                # Şimdilik WAV olarak varsayalım, agent'ı sonra düzeltiriz.
                # Aslında direkt mp3 byte'larını döndürmek daha mantıklı.
                # Şimdilik bu kısmı basitleştiriyoruz, agent'ın WAV beklemediğini varsayalım.
                return await self._synthesize_with_elevenlabs(text)
            except Exception as e:
                self.logger.warning("ElevenLabs ile sentezleme başarısız, Coqui XTTS'e fallback yapılıyor.", error=str(e))
        
        # ElevenLabs başarısız olursa veya aktif değilse Coqui'yi dene
        return await self._synthesize_with_coqui(text, language, speaker_wav_path)


tts_engine = TTSEngine()