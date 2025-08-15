# app/main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI, Response, HTTPException
from pydantic import BaseModel
import edge_tts
import asyncio
import structlog
import sys

# Windows'ta asyncio için gerekli politika ayarı
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# Temel loglama yapılandırması
structlog.configure(
    processors=[
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.dev.ConsoleRenderer(),
    ],
    logger_factory=structlog.PrintLoggerFactory(),
)
logger = structlog.get_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Edge-TTS Service başlıyor...")
    yield
    logger.info("Edge-TTS Service kapanıyor.")

app = FastAPI(title="Sentiric Edge TTS Service", lifespan=lifespan)

class SynthesizeRequest(BaseModel):
    text: str
    voice: str = "tr-TR-AhmetNeural"

@app.post("/api/v1/synthesize", response_class=Response)
async def synthesize(request: SynthesizeRequest):
    try:
        logger.info("Sentezleme isteği alındı", text=request.text, voice=request.voice)
        
        communicate = edge_tts.Communicate(request.text, request.voice)
        
        audio_buffer = bytearray()
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_buffer.extend(chunk["data"])

        if not audio_buffer:
            logger.error("Ses verisi üretilemedi.", request=request.dict())
            raise ValueError("Ses verisi üretilemedi.")
            
        logger.info("Sentezleme başarılı.", voice=request.voice, audio_size=len(audio_buffer))
        return Response(content=bytes(audio_buffer), media_type="audio/mpeg")

    except Exception as e:
        logger.error("Edge-TTS sentezleme sırasında hata", error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=f"Ses üretilirken hata oluştu: {e}")

@app.get("/health")
async def health_check():
    return {"status": "ok"}