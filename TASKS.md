# ⚡ Sentiric Edge TTS Service - Geliştirme Yol Haritası (v4.0)

Bu belge, `edge-tts-service`'in geliştirme görevlerini projenin genel fazlarına uygun olarak listeler.

---

### **FAZ 1: Fonksiyonel API Servisi (ACİL ÖNCELİK)**

**Amaç:** Servisin, `tts-gateway` tarafından güvenilir bir şekilde kullanılabilen, fonksiyonel bir API sunucusu haline getirilmesi.

-   [ ] **Görev ID: TTS-EDGE-001 - FastAPI Sunucusu Kurulumu**
    -   **Açıklama:** `/api/v1/synthesize` ve `/health` endpoint'lerini içeren temel bir FastAPI uygulaması oluştur.
    -   **Kabul Kriterleri:**
        -   [ ] Proje `pyproject.toml` ile yapılandırılmalı ve `uvicorn` ile çalıştırılabilmelidir.
        -   [ ] `/health` endpoint'i `{"status": "ok"}` JSON yanıtı dönmelidir.
        -   [ ] `/api/v1/synthesize` endpoint'i, `SynthesizeRequest` Pydantic modelini kabul etmelidir.

-   [ ] **Görev ID: TTS-EDGE-002 - `edge-tts` Entegrasyonu**
    -   **Açıklama:** Gelen metni `edge-tts` kütüphanesini kullanarak sese çeviren ve ham ses verisi olarak yanıt dönen mantığı implemente et.
    -   **Kabul Kriterleri:**
        -   [ ] Geçerli bir metinle yapılan POST isteğine, `200 OK` durum koduyla ve `Content-Type: audio/mpeg` başlığıyla yanıt verilmelidir.
        -   [ ] Yanıtın gövdesi (body), geçerli MP3 ses verisi içermelidir.
        -   [ ] Boş veya geçersiz bir metin gönderildiğinde `400 Bad Request` hatası dönülmelidir.

-   [ ] **Görev ID: TTS-EDGE-003 - Dinamik Ses Seçimi (Voice Selection)**
    -   **Açıklama:** API isteğindeki `voice` parametresini kullanarak, `tr-TR-AhmetNeural` veya `en-US-JennyNeural` gibi farklı seslerin seçilebilmesini sağla.
    -   **Kabul Kriterleri:**
        -   [ ] `SynthesizeRequest` modeli, `voice` adında varsayılan bir değere (`tr-TR-AhmetNeural`) sahip opsiyonel bir alan içermelidir.
        -   [ ] `voice` parametresi `en-US-JennyNeural` olarak gönderildiğinde, üretilen sesin İngilizce ve kadın sesi olduğu doğrulanmalıdır.
        -   [ ] Geçersiz bir `voice` adı gönderildiğinde, servis `400 Bad Request` hatası vermelidir.

-   [ ] **Görev ID: TTS-EDGE-004 - Dockerfile Oluşturma**
    -   **Açıklama:** Servisi konteyner içinde çalıştırabilmek için optimize edilmiş, standartlara uygun bir `Dockerfile` oluştur.
    -   **Kabul Kriterleri:**
        -   [ ] `Dockerfile`, multi-stage build kullanarak son imaj boyutunu minimumda tutmalıdır.
        -   [ ] İmaj, root olmayan bir kullanıcı (`appuser`) ile çalışmalıdır.
        -   [ ] `docker build` komutuyla başarıyla inşa edilebilmeli ve `docker run` ile başlatıldığında servis erişilebilir olmalıdır.

---

### **FAZ 2: Platform Standartlarına Uyum**

**Amaç:** Servisi, Sentiric ekosisteminin genel gözlemlenebilirlik ve dayanıklılık standartlarıyla uyumlu hale getirmek.

-   [ ] **Görev ID: TTS-EDGE-005 - Prometheus Metrikleri**
    -   **Açıklama:** `prometheus-fastapi-instrumentator` kütüphanesini kullanarak standart RED (Rate, Errors, Duration) metriklerini `/metrics` endpoint'inde sun.
    -   **Kabul Kriterleri:**
        -   [ ] `/metrics` endpoint'i aktif olmalı.
        -   [ ] Yapılan her `/api/v1/synthesize` isteği, `http_requests_total` ve `http_requests_duration_seconds` gibi metrikleri doğru etiketlerle (method, status_code) artırmalıdır.

-   [ ] **Görev ID: TTS-EDGE-006 - Yapılandırılmış Loglama**
    -   **Açıklama:** `structlog` kütüphanesini kullanarak, `OBSERVABILITY_STANDARD.md`'ye tam uyumlu, ortama duyarlı (JSON/Console) loglama altyapısı kur.
    -   **Kabul Kriterleri:**
        -   [ ] `ENV=production` ayarıyla çalışırken loglar JSON formatında olmalıdır.
        -   [ ] Her log, `trace_id`'yi (HTTP başlığından gelen) içermelidir.