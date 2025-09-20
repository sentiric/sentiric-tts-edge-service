# sentiric-tts-edge-service/app/main.py
import asyncio
import sys
import uuid
from contextlib import asynccontextmanager

import edge_tts
import structlog
from fastapi import FastAPI, Response, HTTPException, status, Request
from pydantic import BaseModel, Field
from structlog.contextvars import bind_contextvars, clear_contextvars

from app.core.config import settings
from app.core.logging import setup_logging

# Windows'ta asyncio için gerekli politika ayarı
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# --- Servis Katmanı ve Özel Hatalar ---
class AudioGenerationError(Exception):
    """Ses üretimi sırasında oluşan hatalar için özel istisna sınıfı."""
    pass

async def generate_audio_from_text(text: str, voice: str) -> bytes:
    logger = structlog.get_logger(__name__)
    logger.debug("edge_tts.Communicate başlatılıyor", text=text, voice=voice)
    try:
        communicate = edge_tts.Communicate(text, voice)
        
        audio_buffer = bytearray()
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_buffer.extend(chunk["data"])

        if not audio_buffer:
            logger.error("Edge-TTS'ten boş ses verisi döndü.", text=text, voice=voice)
            raise AudioGenerationError("Ses verisi üretilemedi (boş yanıt).")
            
        return bytes(audio_buffer)

    except Exception as e:
        logger.error("Edge-TTS stream sırasında beklenmedik hata", exc_info=True)
        raise AudioGenerationError(f"Edge-TTS hatası: {e}") from e

# --- FastAPI Uygulaması ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    # DEĞİŞİKLİK: Loglamayı config değerleriyle başlatıyoruz.
    log = setup_logging(log_level=settings.LOG_LEVEL, env=settings.ENV)
    log.info(
        "Uygulama başlıyor...", 
        project=settings.PROJECT_NAME,
        version=settings.SERVICE_VERSION,
        commit=settings.GIT_COMMIT,
        build_date=settings.BUILD_DATE,
        env=settings.ENV, 
        log_level=settings.LOG_LEVEL
    )
    yield
    log.info("Uygulama başarıyla kapatıldı.")

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Metni sese dönüştürmek için Microsoft Edge'in TTS motorunu kullanan bir API.",
    version=settings.SERVICE_VERSION,
    lifespan=lifespan
)

# Middleware
@app.middleware("http")
async def logging_middleware(request: Request, call_next) -> Response:
    log = structlog.get_logger(__name__) # Middleware için logger'ı al
    clear_contextvars()
    
    if request.url.path in ["/health", "/healthz"]:
        return await call_next(request)
    
    trace_id = request.headers.get("X-Trace-ID") or f"tts-edge-trace-{uuid.uuid4()}"
    bind_contextvars(trace_id=trace_id)

    log.info("Request received", http_method=request.method, http_path=request.url.path)
    response = await call_next(request)
    log.info("Request completed", http_status_code=response.status_code)
    return response

class SynthesizeRequest(BaseModel):
    text: str = Field(..., min_length=1, description="Sese dönüştürülecek metin.")
    voice: str = Field("tr-TR-AhmetNeural", description="Kullanılacak ses modeli.")

@app.post(
    "/api/v1/synthesize",
    response_class=Response,
    tags=["TTS"],
    summary="Metni sese dönüştürür",
    responses={
        200: {"content": {"audio/mpeg": {}}},
        400: {"description": "Geçersiz istek (örn: metin boş)."},
        500: {"description": "Sunucu tarafında ses üretilirken bir hata oluştu."},
    },
)
async def synthesize(payload: SynthesizeRequest):
    log = structlog.get_logger(__name__)
    try:
        log.info("Sentezleme isteği alındı", text=payload.text, voice=payload.voice)
        audio_bytes = await generate_audio_from_text(payload.text, payload.voice)
        log.info("Sentezleme başarılı.", voice=payload.voice, audio_size=len(audio_bytes))
        return Response(content=audio_bytes, media_type="audio/mpeg")

    except AudioGenerationError as e:
        log.error("Ses üretimi hatası", error=str(e), request_data=payload.dict())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Ses üretilirken bir hata oluştu: {e}"
        )
    except Exception as e:
        log.error("Endpoint'te beklenmedik genel hata", error=str(e), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Beklenmedik bir sunucu hatası oluştu."
        )

@app.get("/healthz", include_in_schema=False, tags=["Health"])
async def healthz_check():
    return Response(status_code=status.HTTP_200_OK)

@app.get("/health", tags=["Health"], summary="Servis sağlık durumunu kontrol eder")
@app.head("/health")
async def health_check():
    return {"status": "ok"}