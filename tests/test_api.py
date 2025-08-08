# tests/test_api.py
import pytest
from httpx import AsyncClient
from app.main import app
from app.services.tts_service import tts_engine

# Pytest'i asenkron testler için yapılandır
pytestmark = pytest.mark.asyncio

@pytest.fixture(scope="module")
async def client():
    # Testler için FastAPI uygulamasını bir AsyncClient ile sarmala
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

# --- Health Endpoint Testleri ---

async def test_health_check_when_ready(client: AsyncClient, mocker):
    """
    Motor hazır olduğunda /health endpoint'inin 'ok' dönmesi gerektiğini test eder.
    """
    # tts_engine'in durumunu 'hazır' olarak taklit et (mock)
    mocker.patch.object(tts_engine, 'is_ready', return_value=True)
    
    response = await client.get("/health")
    assert response.status_code == 200
    json_response = response.json()
    assert json_response["status"] == "ok"
    assert json_response["details"]["tts_engine_loaded"] is True

async def test_health_check_when_not_ready(client: AsyncClient, mocker):
    """
    Motor hazır olmadığında /health endpoint'inin 'degraded' dönmesi gerektiğini test eder.
    """
    mocker.patch.object(tts_engine, 'is_ready', return_value=False)
    
    response = await client.get("/health")
    assert response.status_code == 200 # Health check kendisi hata vermemeli
    json_response = response.json()
    assert json_response["status"] == "degraded"
    assert json_response["details"]["tts_engine_loaded"] is False

# --- Synthesize Endpoint Testleri ---

async def test_synthesize_success(client: AsyncClient, mocker):
    """
    Başarılı bir sentezleme isteğinin 200 OK ve WAV verisi döndürmesi gerektiğini test eder.
    """
    mock_wav_bytes = b"fake_wav_data_123"
    # Gerçek, yavaş sentezleme işlemini taklit ederek testi hızlandırıyoruz
    mocker.patch.object(tts_engine, 'synthesize', return_value=mock_wav_bytes)
    # Motorun hazır olduğunu da varsayıyoruz
    mocker.patch.object(tts_engine, 'is_ready', return_value=True)

    response = await client.post("/api/v1/synthesize", json={"text": "bu bir testtir", "language": "tr"})
    
    assert response.status_code == 200
    assert response.headers["content-type"] == "audio/wav"
    assert response.content == mock_wav_bytes

async def test_synthesize_when_engine_not_ready(client: AsyncClient, mocker):
    """
    Motor hazır değilken yapılan bir sentezleme isteğinin 503 Service Unavailable hatası vermesi gerektiğini test eder.
    """
    mocker.patch.object(tts_engine, 'is_ready', return_value=False)
    
    response = await client.post("/api/v1/synthesize", json={"text": "bu istek başarısız olmalı", "language": "tr"})
    
    assert response.status_code == 503
    assert "TTS motoru şu an kullanılamıyor" in response.json()["detail"]

async def test_synthesize_with_dynamic_speaker_url(client: AsyncClient, mocker):
    """
    API'nin dinamik speaker_wav_url parametresini kabul ettiğini test eder.
    """
    mock_synthesize = mocker.patch.object(tts_engine, 'synthesize', return_value=b"dynamic_voice_data")
    mocker.patch.object(tts_engine, 'is_ready', return_value=True)
    
    speaker_url = "https://sentiric.github.io/sentiric-assets/audio/speakers/tr/default_male.wav"
    
    response = await client.post(
        "/api/v1/synthesize", 
        json={
            "text": "dynamic voice test", 
            "language": "en",
            "speaker_wav_url": speaker_url
        }
    )
    
    assert response.status_code == 200
    # synthesize metodunun doğru parametrelerle çağrıldığını doğrula
    mock_synthesize.assert_called_once_with("dynamic voice test", "en", speaker_url)

async def test_synthesize_missing_text_parameter(client: AsyncClient):
    """
    'text' parametresi eksik olduğunda 422 Unprocessable Entity hatası alınması gerektiğini test eder.
    """
    response = await client.post("/api/v1/synthesize", json={"language": "tr"})
    assert response.status_code == 422 # FastAPI'nin varsayılan validasyon hatası