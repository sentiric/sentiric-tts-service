# --- STAGE 1: Builder ---
FROM python:3.11-slim-bullseye AS builder

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

ENV PIP_BREAK_SYSTEM_PACKAGES=1 \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=true

RUN pip install poetry

# --- DEĞİŞİKLİK BURADA: Artık poetry.lock'ı da kopyalıyoruz ---
COPY pyproject.toml poetry.lock ./

# --- DEĞİŞİKLİK BURADA: Poetry'ye "lock dosyasını kullan, çözümleme yapma" diyoruz ---
# Bu, kurulumu hem hızlandırır hem de tekrarlanabilir kılar.
RUN poetry install --no-root --without dev --sync --no-ansi

# Lisans onayı ve model indirme
RUN export COQUI_TOS_AGREED=1 && \
    poetry run python -c "from TTS.api import TTS; TTS(model_name='tts_models/multilingual/multi-dataset/xtts_v2')"


# --- STAGE 2: Production ---
FROM python:3.11-slim-bullseye

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libsndfile1 ffmpeg \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /root/.local/share/tts /root/.local/share/tts

ENV PATH="/app/.venv/bin:$PATH"

COPY ./app ./app
COPY ./docs /app/docs

EXPOSE 5002
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "5002"]