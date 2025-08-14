# --- STAGE 1: Production ---
FROM python:3.11-slim-bullseye

WORKDIR /app

# Ortam değişkenleri
ENV PIP_BREAK_SYSTEM_PACKAGES=1 \
    PIP_NO_CACHE_DIR=1

# Gerekli sistem bağımlılıkları
RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*

# Proje dosyalarını kopyala
COPY pyproject.toml .
COPY app ./app
COPY README.md .

# Projeyi ve bağımlılıklarını kur
RUN pip install .

# Güvenlik için root olmayan kullanıcı oluştur ve kullan
RUN useradd -m -u 1002 appuser
USER appuser

EXPOSE 5002
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "5002"]