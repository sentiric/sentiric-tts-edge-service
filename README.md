# ⚡ Sentiric Edge TTS Service (Expert TTS Engine)

[![Status](https://img.shields.io/badge/status-active-success.svg)]()
[![Python Version](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/)

**Sentiric Edge TTS Service**, `sentiric-tts-gateway-service` tarafından yönetilen **uzman ses motorlarından** biridir. Temel amacı, Microsoft Edge'in bulut tabanlı TTS motorunu kullanarak **hızlı, yüksek kaliteli ve ücretsiz** ses sentezi sağlamaktır.

Bu servis, platformun varsayılan, genel amaçlı ses üretme iş atıdır.

## 🎯 Temel Sorumluluklar

*   **Hızlı Sentezleme:** `edge-tts` kütüphanesini kullanarak, metni çok düşük gecikmeyle sese dönüştürür.
*   **Çoklu Ses Desteği:** Microsoft Edge tarafından sunulan farklı dillerdeki ve cinsiyetlerdeki sesleri (`voice`) destekler.
*   **API Sunucusu:** `tts-gateway`'den gelen ses sentezleme isteklerini işleyen bir API sunucusu barındırır.

## 🛠️ Teknoloji Yığını

*   **Dil:** Python
*   **Web Çerçevesi:** FastAPI (planlanan)
*   **AI Motoru:** `edge-tts` kütüphanesi

## 🔌 API Etkileşimleri

*   **Gelen (Sunucu):**
    *   `sentiric-tts-gateway-service` (REST/JSON veya gRPC): Ses sentezleme isteklerini alır.

## 🚀 Yerel Geliştirme

1.  **Bağımlılıkları Yükleyin:** `pip install -r requirements.txt`
2.  **Servisi Başlatın:** `uvicorn app.main:app --reload`

## 🤝 Katkıda Bulunma

Katkılarınızı bekliyoruz! Lütfen projenin ana [Sentiric Governance](https://github.com/sentiric/sentiric-governance) reposundaki kodlama standartlarına ve katkıda bulunma rehberine göz atın.

---
## 🏛️ Anayasal Konum

Bu servis, [Sentiric Anayasası'nın (v11.0)](https://github.com/sentiric/sentiric-governance/blob/main/docs/blueprint/Architecture-Overview.md) **Zeka & Orkestrasyon Katmanı**'nda yer alan merkezi bir bileşendir.