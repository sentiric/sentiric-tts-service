# 🎙️ Sentiric TTS Service (Legacy/Hybrid Engine)

[![Status](https://img.shields.io/badge/status-refactoring-yellow.svg)]()
[![Python Version](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/)

**Sentiric TTS Service**, Sentiric platformunun orijinal, hepsi bir arada ses sentezleme motorudur. Hem yerel **Coqui XTTS** modelini hem de bulut tabanlı **ElevenLabs** API'sini tek bir servis altında birleştirir.

**NOT:** Bu servis, platformun "Ses Orkestrasyon Katmanı" vizyonu doğrultusunda yeniden yapılandırılmaktadır. İçindeki mantık, `sentiric-coqui-tts-service` ve `sentiric-elevenlabs-tts-service` gibi **uzman motorlara** ve bu motorları yönetecek olan `sentiric-tts-gateway-service`'e taşınmaktadır. **Bu repo, geçiş tamamlandığında arşivlenecektir.**

## 🎯 Temel Sorumluluklar (Mevcut Durum)

*   **Hibrit Sentezleme:** Gelen bir isteği, öncelikli olarak ElevenLabs (eğer aktifse) ile sentezlemeye çalışır. Başarısız olursa veya aktif değilse, Coqui XTTS modelini kullanarak sentezleme yapar.
*   **Dinamik Ses Klonlama:** `speaker_wav_url` parametresi ile gelen bir referans ses dosyasını indirip, Coqui XTTS motorunu kullanarak sesi o sese benzeterek üretir.
*   **API Sunucusu:** `/api/v1/synthesize` endpoint'i üzerinden ses sentezleme isteklerini kabul eder.

## 🛠️ Teknoloji Yığını

*   **Dil:** Python
*   **Web Çerçevesi:** FastAPI
*   **AI Motorları:** `TTS` (Coqui XTTS-v2), `httpx` (ElevenLabs API için)
*   **Paketleme:** `pyproject.toml` (setuptools)

## 🔌 API Etkileşimleri

*   **Gelen (Sunucu):**
    *   `sentiric-agent-service` (REST/JSON)
*   **Giden (İstemci):**
    *   `api.elevenlabs.io` (REST/JSON)
    *   Harici URL'ler (HTTP): Dinamik `speaker_wav_url`'leri indirmek için.

## 🚀 Yerel Geliştirme

1.  **Bağımlılıkları Kurun:** `pip install -e ".[dev]"`
2.  **`.env` Dosyasını Oluşturun:** `.env.docker`'ı kopyalayın ve API anahtarlarınızı girin.
3.  **Servisi Başlatın:** `uvicorn app.main:app --reload --port 5002`

## 🤝 Katkıda Bulunma

Bu repo yeniden yapılandırma sürecinde olduğu için, yeni özellik eklemek yerine mevcut mantığın yeni `tts-gateway` mimarisine taşınmasına yardımcı olacak katkılar önceliklidir.

---
## 🏛️ Anayasal Konum

Bu servis, [Sentiric Anayasası'nın (v11.0)](https://github.com/sentiric/sentiric-governance/blob/main/docs/blueprint/Architecture-Overview.md) **Zeka & Orkestrasyon Katmanı**'nda yer alan merkezi bir bileşendir.