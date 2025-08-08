# 🤖 Sentiric TTS Service - API Kullanım ve Demo Rehberi

Bu belge, çalışan `sentiric-tts-service`'in API'ını nasıl kullanacağınızı ve yeteneklerini nasıl test edeceğinizi gösterir.

## Önkoşullar

Servisin `docker-compose` ile veya yerel `uvicorn` komutuyla çalışır durumda olması gerekmektedir.

---

## Canlı Test Senaryoları (`curl`)

### Senaryo 1: Varsayılan Sesle Sentezleme

Bu komut, servisin içine gömülü olan varsayılan referans sesini (`docs/audio/speakers/tr/default_male.wav`) kullanarak bir `.wav` dosyası oluşturur.

```bash
# Windows cmd.exe için:
curl -X POST "http://localhost:5002/api/v1/synthesize" -H "Content-Type: application/json" -d "{\"text\": \"Merhaba, bu standart Sentirik sesidir.\"}" --output default_voice.wav

# Linux/macOS/WSL için:
curl -X POST 'http://localhost:5002/api/v1/synthesize' -H 'Content-Type: application/json' -d '{"text": "Merhaba, bu standart Sentirik sesidir."}' --output default_voice.wav
```
Oluşturulan `default_voice.wav` dosyasını dinleyerek sonucu kontrol edebilirsiniz.

### Senaryo 2: Dinamik Referans Sesiyle Sentezleme (Hibrit Yetenek)

Bu komut, servise internet üzerinden bir referans ses URL'si vererek, sesi o sese benzeterek üretmesini sağlar. **Bu, `sentiric-assets` ile entegrasyonun gücünü gösterir.**

*Önce `sentiric-assets` reponuzda `docs/audio/speakers/en/` altına bir İngilizce `.wav` dosyası (örn: `default_female.wav`) eklediğinizden ve GitHub Pages'in güncellendiğinden emin olun.*

```bash
# Windows cmd.exe için:
curl -X POST "http://localhost:5002/api/v1/synthesize" -H "Content-Type: application/json" -d "{\"text\": \"This is a dynamically cloned voice.\", \"language\": \"en\", \"speaker_wav_url\": \"https://sentiric.github.io/sentiric-assets/audio/speakers/tr/default_male.wav\"}" --output dynamic_voice.wav

# Linux/macOS/WSL için:
curl -X POST 'http://localhost:5002/api/v1/synthesize' -H 'Content-Type: application/json' -d '{"text": "This is a dynamically cloned voice.", "language": "en", "speaker_wav_url": "https://sentiric.github.io/sentiric-assets/audio/speakers/tr/default_male.wav"}' --output dynamic_voice.wav
```
Oluşturulan `dynamic_voice.wav` dosyasının sesinin, `default_voice.wav`'dan farklı ve verdiğiniz URL'deki sese benzediğini duyacaksınız.

### Senaryo 3: Sağlık Durumunu Kontrol Etme

Servisin ve içindeki TTS motorunun hazır olup olmadığını kontrol eder.

```bash
curl http://localhost:5002/health
```
**Beklenen Yanıt:** `{"status":"ok","details":{"tts_engine_loaded":true}}`
```
