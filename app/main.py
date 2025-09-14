# app/main.py
import asyncio
import sys
from contextlib import asynccontextmanager

import edge_tts
import structlog
from fastapi import FastAPI, Response, HTTPException, status
from pydantic import BaseModel, Field

# --- 1. Geliştirilmiş Logging Yapılandırması ---
def setup_logging():
    """Uygulama için standartlaştırılmış JSON loglamayı yapılandırır."""
    structlog.configure(
        processors=[
            structlog.stdlib.add_log_level,
            structlog.stdlib.add_logger_name,
            structlog.processors.TimeStamper(fmt="iso", utc=True),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            # Geliştirme için: structlog.dev.ConsoleRenderer()
            # Üretim için: JSON formatı logların parse edilmesini kolaylaştırır
            structlog.processors.JSONRenderer(),
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

setup_logging()
logger = structlog.get_logger(__name__)

# Windows'ta asyncio için gerekli politika ayarı
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# --- 2. Servis Katmanı ve Özel Hatalar ---
class AudioGenerationError(Exception):
    """Ses üretimi sırasında oluşan hatalar için özel istisna sınıfı."""
    pass

async def generate_audio_from_text(text: str, voice: str) -> bytes:
    """
    Verilen metin ve ses modelini kullanarak Edge-TTS ile ses verisi üretir.

    Args:
        text: Sese dönüştürülecek metin.
        voice: Kullanılacak ses modeli (örn. "tr-TR-AhmetNeural").

    Returns:
        MP3 formatında ses verisi içeren bytes.

    Raises:
        AudioGenerationError: Ses verisi üretilemezse veya bir hata oluşursa.
    """
    logger.info("edge_tts.Communicate başlatılıyor", text=text, voice=voice)
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
        # Orijinal hatayı zincirleyerek daha iyi hata takibi sağlıyoruz
        raise AudioGenerationError(f"Edge-TTS hatası: {e}") from e


# --- FastAPI Uygulaması ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Uygulama yaşam döngüsü yöneticisi."""
    logger.info("Edge-TTS Service başlıyor...")
    yield
    logger.info("Edge-TTS Service kapanıyor.")

app = FastAPI(
    title="Sentiric Edge TTS Service",
    description="Metni sese dönüştürmek için Microsoft Edge'in TTS motorunu kullanan bir API.",
    version="1.0.0",
    lifespan=lifespan
)

class SynthesizeRequest(BaseModel):
    """/synthesize endpoint'i için istek modeli."""
    text: str = Field(..., min_length=1, description="Sese dönüştürülecek metin.")
    voice: str = Field("tr-TR-AhmetNeural", description="Kullanılacak ses modeli.")


@app.post(
    "/api/v1/synthesize",
    response_class=Response,
    tags=["TTS"],
    summary="Metni sese dönüştürür",
    responses={
        200: {
            "content": {"audio/mpeg": {}},
            "description": "Başarılı. MP3 formatında ses verisi döner.",
        },
        400: {"description": "Geçersiz istek (örn: metin boş)."},
        500: {"description": "Sunucu tarafında ses üretilirken bir hata oluştu."},
    },
)
async def synthesize(payload: SynthesizeRequest):
    """
    Verilen metni (`text`) ve ses modelini (`voice`) kullanarak bir ses dosyası oluşturur.
    """
    try:
        logger.info("Sentezleme isteği alındı", text=payload.text, voice=payload.voice)
        
        # Mantığı servis fonksiyonuna devrediyoruz
        audio_bytes = await generate_audio_from_text(payload.text, payload.voice)
        
        logger.info("Sentezleme başarılı.", voice=payload.voice, audio_size=len(audio_bytes))
        return Response(content=audio_bytes, media_type="audio/mpeg")

    except AudioGenerationError as e:
        logger.error("Ses üretimi hatası", error=str(e), request_data=payload.dict())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Ses üretilirken bir hata oluştu: {e}"
        )
    except Exception as e:
        # Beklenmedik diğer tüm hatalar için genel bir yakalayıcı
        logger.error("Endpoint'te beklenmedik genel hata", error=str(e), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Beklenmedik bir sunucu hatası oluştu."
        )


@app.get("/health", tags=["Health"], summary="Servis sağlık durumunu kontrol eder")
@app.head("/health")
async def health_check():
    """Servisin ayakta olup olmadığını kontrol etmek için kullanılır."""
    return {"status": "ok"}