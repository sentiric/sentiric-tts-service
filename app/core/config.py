# app/core/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from typing import Optional
# torch import'u artık gerekli değil
# import torch 

class Settings(BaseSettings):
    PROJECT_NAME: str = "Sentiric TTS Service"
    API_V1_STR: str = "/api/v1"
    ENV: str = Field("production", validation_alias="ENV")
    LOG_LEVEL: str = Field("INFO", validation_alias="LOG_LEVEL")

    TTS_SERVICE_PORT: int = Field(5002, validation_alias="TTS_SERVICE_PORT")

    TTS_MODEL_NAME: str = Field(
        "tts_models/multilingual/multi-dataset/xtts_v2", 
        validation_alias="TTS_SERVICE_MODEL_NAME"
    )
    TTS_MODEL_DEVICE: str = Field("auto", validation_alias="TTS_SERVICE_MODEL_DEVICE")
    TTS_DEFAULT_SPEAKER_WAV_PATH: str = Field(
        "/app/docs/audio/speakers/tr/default_male.wav", 
        validation_alias="TTS_DEFAULT_SPEAKER_WAV_PATH"
    )
    
    # device property'si buradan kaldırıldı.

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding='utf-8', 
        extra='ignore', case_sensitive=False
    )

settings = Settings()