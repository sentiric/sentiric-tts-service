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
from typing import Optional # <-- EKSİK OLAN IMPORT BU SATIR
from TTS.api import TTS
from app.core.config import settings

logger = structlog.get_logger(__name__)

# --- YENİ: URL'den dosya indiren yardımcı fonksiyon ---
async def download_temp_wav(url: str) -> str:
    """Verilen URL'den bir ses dosyasını indirir ve geçici bir dosyanın yolunu döndürür."""
    async with httpx.AsyncClient() as client:
        response = await client.get(url, follow_redirects=True, timeout=10.0)
        response.raise_for_status() # Hata varsa (404, 500 vb.) istisna fırlat
        
        # Geçici bir dosya oluştur
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
            tmp_file.write(response.content)
            logger.info("Dinamik referans sesi başarıyla indirildi.", url=url, path=tmp_file.name)
            return tmp_file.name

class TTSEngine:

    def __init__(self):
        self.model = None
        self.logger = logger.bind(service_component="TTSEngine")
        self.device = self._get_device()

    def _get_device(self) -> str:
        device_setting = settings.TTS_MODEL_DEVICE.lower()
        if device_setting == "auto":
            return "cuda" if torch.cuda.is_available() else "cpu"
        return device_setting

    def load_model(self):
        if self.model: return
        try:
            self.logger.info("TTS Modeli yükleniyor...", device=self.device)
            self.model = TTS(settings.TTS_MODEL_NAME).to(self.device)
            self.logger.info("TTS Modeli başarıyla yüklendi.")
        except Exception as e:
            self.logger.critical("KRİTİK HATA: TTS modeli yüklenemedi.", error=str(e), exc_info=True)
            self.model = None

    def is_ready(self) -> bool:
        return self.model is not None
        
    async def synthesize(self, text: str, language: str, speaker_wav_path: Optional[str] = None) -> bytes:
        if not self.is_ready():
            raise RuntimeError("TTS motoru kullanıma hazır değil.")
            
        temp_speaker_path = None
        try:
            # --- YENİ: Hibrit mantık ---
            if speaker_wav_path and speaker_wav_path.startswith("http"):
                # Eğer bir URL verildiyse, indir ve geçici dosya yolunu kullan
                temp_speaker_path = await download_temp_wav(speaker_wav_path)
                speaker_ref = [temp_speaker_path]
            else:
                # URL verilmediyse, .env'deki varsayılan dosyayı kullan
                speaker_ref = [settings.TTS_DEFAULT_SPEAKER_WAV_PATH]

            def _synthesize_sync():
                self.logger.info("Sentezleme işlemi başlıyor...", speaker=speaker_ref[0])
                wav_chunks = self.model.tts(text=text, speaker_wav=speaker_ref, language=language)
                wav_np = np.array(wav_chunks, dtype=np.float32)
                wav_buffer = io.BytesIO()
                sf.write(wav_buffer, wav_np, self.model.synthesizer.output_sample_rate, format='WAV')
                wav_buffer.seek(0)
                self.logger.info("Sentezleme işlemi tamamlandı.")
                return wav_buffer.getvalue()

            return await asyncio.to_thread(_synthesize_sync)
        finally:
            # --- YENİ: Geçici dosyayı temizle ---
            if temp_speaker_path and os.path.exists(temp_speaker_path):
                os.remove(temp_speaker_path)
                logger.info("Geçici referans sesi silindi.", path=temp_speaker_path)


tts_engine = TTSEngine()