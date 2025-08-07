# 🎙️ Sentiric TTS Service

**Açıklama:** Sentiric platformu için yüksek kaliteli, çok dilli metin-konuşma (Text-to-Speech) sentezi sağlayan, üretim kalitesinde bir mikroservis.

**Temel Yetenekler:**
*   **Yüksek Kaliteli Ses:** Coqui `XTTS-v2` modelini kullanarak doğal ve klonlanabilir sesler üretir.
*   **Çok Dilli:** Türkçe, İngilizce dahil olmak üzere birçok dili destekler.
*   **Optimize Edilmiş:** "Sıfır bütçe" hedefine uygun olarak, CPU üzerinde verimli çalışacak şekilde tasarlanmış ve Docker imaj boyutu optimize edilmiştir.
*   **Üretime Hazır:** Uygulama başlarken modeli belleğe yükler, `/health` endpoint'i ile durumu hakkında bilgi verir ve `governance` standartlarına uygun loglama yapar.

---

## 🚀 Hızlı Başlangıç (Docker ile)

Bu servis, `sentiric-infrastructure` reposundaki merkezi `docker-compose` ile platformun bir parçası olarak çalışmak üzere tasarlanmıştır. Tek başına çalıştırmak ve test etmek için:

1.  **`.env` Dosyası Oluşturun:**
    `.env.example` dosyasını `.env` olarak kopyalayın. Genellikle varsayılan ayarlar yerel testler için yeterlidir.

2.  **Referans Ses Dosyası Ekleyin:**
    Proje kök dizininde bir `audio` klasörü oluşturun ve içine `reference_tr.wav` adında yüksek kaliteli bir referans ses dosyası koyun.

3.  **Servisi Başlatın:**
    ```bash
    docker compose -f docker-compose.service.yml up --build
    ```
    Modelin ilk kez yüklenmesi birkaç dakika sürebilir. Loglarda `Uygulama hazır ve istekleri kabul ediyor.` mesajını gördüğünüzde servis hazır demektir.

---

## 🤖 API Kullanımı ve Demo

Servisin API'ını test etmek ve canlı bir demo görmek için lütfen aşağıdaki rehberi inceleyin:

➡️ **[API Kullanım ve Demo Rehberi (DEMO.md)](DEMO.md)**

---

## 🧪 Otomatize Testleri Çalıştırma

Kodda değişiklik yapmadan önce veya yaptıktan sonra, sistemin bütünlüğünü doğrulamak için otomatize testleri çalıştırın:

```bash
# Geliştirme bağımlılıklarını kur
poetry install --with dev

# Testleri çalıştır
poetry run pytest -v