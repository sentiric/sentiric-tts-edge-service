# ⚡ Sentiric Edge TTS Service - Görev Listesi

Bu belge, `edge-tts-service`'in geliştirme yol haritasını ve önceliklerini tanımlar.

---

### Faz 1: Temel Servis İskeleti (Sıradaki Öncelik)

Bu faz, servisin fonksiyonel bir API sunucusu haline getirilmesini hedefler.

-   [ ] **Görev ID: TTS-EDGE-001 - FastAPI Sunucusu Kurulumu**
    -   **Açıklama:** `/api/v1/synthesize` ve `/health` endpoint'lerini içeren temel bir FastAPI uygulaması oluştur.
    -   **Durum:** ⬜ Planlandı.

-   [ ] **Görev ID: TTS-EDGE-002 - `edge-tts` Entegrasyonu**
    -   **Açıklama:** Gelen metni `edge-tts` kütüphanesini kullanarak sese çeviren ve `.wav` formatında yanıt dönen mantığı implemente et.
    -   **Durum:** ⬜ Planlandı.

-   [ ] **Görev ID: TTS-EDGE-003 - Ses Seçimi (Voice Selection)**
    -   **Açıklama:** API isteğine `voice` parametresi ekleyerek, `tr-TR-AhmetNeural` gibi farklı seslerin seçilebilmesini sağla.
    -   **Durum:** ⬜ Planlandı.

-   [ ] **Görev ID: TTS-EDGE-004 - Dockerfile Oluşturma**
    -   **Açıklama:** Servisi konteyner içinde çalıştırabilmek için optimize edilmiş bir `Dockerfile` oluştur.
    -   **Durum:** ⬜ Planlandı.

### **FAZ 2: Platform Standartlarına Uyum**
-   [ ] **Görev ID: TTS-EDGE-005 - Prometheus Metrikleri**
    -   **Açıklama:** `prometheus-fastapi-instrumentator` kütüphanesini kullanarak standart RED (Rate, Errors, Duration) metriklerini `/metrics` endpoint'inde sun.
    -   **Kabul Kriterleri:**
        -   [ ] `/metrics` endpoint'i aktif olmalı.
        -   [ ] Yapılan her `/synthesize` isteği, `http_requests_total` ve `http_requests_duration_seconds` gibi metrikleri artırmalı.    