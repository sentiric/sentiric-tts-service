# --- STAGE 1: Builder ---
# Ağır bağımlılıkları ve modelleri bu aşamada kuruyoruz.
FROM python:3.11-slim-bullseye AS builder

WORKDIR /app

# C/C++ derleyicilerini ve build araçlarını ekliyoruz
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

ENV PIP_BREAK_SYSTEM_PACKAGES=1 \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=true

RUN pip install poetry

COPY pyproject.toml poetry.lock* ./

RUN poetry install --no-root --without dev --sync

# Lisans onayı için ortam değişkenlerini ekliyoruz
# Bu komut, modeli /root/.local/share/tts altına indirecektir.
RUN export COQUI_TOS_AGREED=1 && \
    poetry run python -c "from TTS.api import TTS; TTS(model_name='tts_models/multilingual/multi-dataset/xtts_v2')"


# --- STAGE 2: Production ---
FROM python:3.11-slim-bullseye

WORKDIR /app

ENV HF_HOME=/app/cache/huggingface

RUN apt-get update && apt-get install -y --no-install-recommends \
    libsndfile1 ffmpeg \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /root/.local/share/tts /root/.local/share/tts

# poetry'nin sanal ortamını PATH'e ekle
ENV PATH="/app/.venv/bin:$PATH"

#  organize varlık klasörünü kopyala ---
COPY ./docs /app/docs

# Uygulama kodunu kopyala
COPY ./app ./app

EXPOSE 5002
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "5002"]