# --- STAGE 1: Production ---
FROM python:3.11-slim-bullseye

# Build argümanlarını build aşamasında kullanılabilir yap
ARG GIT_COMMIT="unknown"
ARG BUILD_DATE="unknown"
ARG SERVICE_VERSION="0.0.0"

WORKDIR /app

ENV PIP_BREAK_SYSTEM_PACKAGES=1 \
    PIP_NO_CACHE_DIR=1

# --- Çalışma zamanı sistem bağımlılıkları ---
RUN apt-get update && apt-get install -y --no-install-recommends \
    netcat-openbsd \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Proje dosyalarını kopyala
COPY pyproject.toml .
COPY app ./app
COPY README.md .

# Projeyi ve bağımlılıklarını kur
RUN pip install .

# Güvenlik için root olmayan kullanıcı oluştur ve kullan
RUN useradd -m -u 1002 appuser
USER appuser

# DÜZELTME: Ortam değişkenini shell'in çözebilmesi için komutu "sh -c" içine alıyoruz.
# Çift tırnaklar, shell'in değişkeni genişletmesini sağlar.
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port 14020"]