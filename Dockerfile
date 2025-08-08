# --- STAGE 1: Builder ---
# Bu aşama, tüm bağımlılıkları ve modeli kurar.
FROM python:3.11-slim-bullseye AS builder

WORKDIR /app

# Ortam değişkenleri
ENV PIP_BREAK_SYSTEM_PACKAGES=1 \
    PIP_NO_CACHE_DIR=1 \
    # Coqui TTS lisansını otomatik kabul et
    COQUI_TOS_AGREED=1

# Gerekli sistem bağımlılıkları (derleme ve Coqui için git)
RUN apt-get update && apt-get install -y --no-install-recommends build-essential ffmpeg git && rm -rf /var/lib/apt/lists/*

# Kurulum tanımını kopyala
COPY pyproject.toml .

# Uygulama kodunu ve gerekli diğer dosyaları kopyala
COPY app ./app
COPY README.md .
COPY docs ./docs

# --- HATA DÜZELTMESİ: --extra-index-url KULLANIMI ---
# Bağımlılıkları kur. Torch'u CPU için özel index'ten alıyoruz, diğerlerini standart PyPI'dan.
RUN pip install . --extra-index-url https://download.pytorch.org/whl/cpu

# Modeli build sırasında indirerek çalışma zamanı gecikmesini önle
RUN python -c "from TTS.api import TTS; TTS(model_name='tts_models/multilingual/multi-dataset/xtts_v2')"


# --- STAGE 2: Production ---
# Bu aşama, builder'dan sadece gerekli dosyaları alarak son, hafif imajı oluşturur.
FROM python:3.11-slim-bullseye

WORKDIR /app

# Sadece çalışma zamanı için gerekli sistem bağımlılıkları
RUN apt-get update && apt-get install -y --no-install-recommends libsndfile1 ffmpeg curl && rm -rf /var/lib/apt/lists/*

# Builder'dan kurulu kütüphaneleri, komutları ve modeli kopyala
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY --from=builder /root/.local/share/tts /root/.local/share/tts

# Uygulama kodunu ve referans ses dosyasını kopyala
COPY ./app ./app
COPY ./docs /app/docs

EXPOSE 5002
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "5002"]