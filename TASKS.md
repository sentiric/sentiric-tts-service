# 🎙️ Sentiric TTS Service - Görev Listesi (Refaktör Odaklı)

Bu belge, `tts-service`'in yeni "Ses Orkestrasyon Mimarisi"ne geçiş sürecini yönetir.

---

### Faz 1: Mevcut Durum ve Hibrit Motor

Bu faz, servisin mevcut, hepsi bir arada yapısını tanımlar.

-   [x] **FastAPI Sunucusu:** `/api/v1/synthesize` ve `/health` endpoint'leri.
-   [x] **Coqui XTTS Entegrasyonu:** Yerel, yüksek kaliteli ses sentezleme.
-   [x] **ElevenLabs Entegrasyonu:** Premium, bulut tabanlı ses sentezleme.
-   [x] **Hibrit Mantık:** ElevenLabs aktifse onu, değilse veya hata verirse Coqui'yi kullanan fallback mekanizması.
-   [x] **Dinamik Ses Klonlama:** `speaker_wav_url` ile Coqui üzerinden ses klonlama.

---

### Faz 2: Mimarinin Ayrıştırılması (Sıradaki Öncelik)

Bu faz, bu monolitik servisi, daha modüler olan uzman motorlara ve bir ağ geçidine ayırmayı hedefler.

-   [ ] **Görev ID: TTS-REF-001 - Coqui Mantığını Taşıma**
    -   **Açıklama:** Bu repodaki Coqui XTTS ile ilgili tüm mantığı (`_synthesize_with_coqui`, model yükleme, `TTS` bağımlılığı vb.) yeni `sentiric-coqui-tts-service` reposuna taşı.
    -   **Durum:** ⬜ Planlandı.

-   [ ] **Görev ID: TTS-REF-002 - ElevenLabs Mantığını Taşıma**
    -   **Açıklama:** Bu repodaki ElevenLabs ile ilgili tüm mantığı (`_synthesize_with_elevenlabs`, `httpx` istemcisi vb.) yeni `sentiric-elevenlabs-tts-service` reposuna taşı.
    -   **Durum:** ⬜ Planlandı.

-   [ ] **Görev ID: TTS-REF-003 - Hibrit Mantığı Gateway'e Taşıma**
    -   **Açıklama:** "Önce ElevenLabs'i dene, olmazsa Coqui'yi dene" şeklindeki fallback mantığını `sentiric-tts-gateway-service`'in sorumluluğuna devret.
    -   **Durum:** ⬜ Planlandı.

-   [ ] **Görev ID: TTS-REF-004 - Repoyu Arşivleme**
    -   **Açıklama:** Tüm mantık başarıyla yeni servislere taşındıktan sonra, bu repoyu `ARCHIVED` olarak işaretle.
    -   **Durum:** ⬜ Planlandı.