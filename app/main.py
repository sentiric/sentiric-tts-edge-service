from contextlib import asynccontextmanager
from fastapi import FastAPI, Response, HTTPException
from pydantic import BaseModel
import edge_tts
import asyncio
import structlog

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
        communicate = edge_tts.Communicate(request.text, request.voice)
        
        # edge-tts'den gelen veriyi byte olarak toplamak için bir buffer
        audio_buffer = bytearray()
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_buffer.extend(chunk["data"])

        if not audio_buffer:
            raise ValueError("Ses verisi üretilemedi.")
            
        # edge-tts mp3 formatında verir, bunu gateway'de handle edebiliriz veya WAV'a çevirebiliriz.
        # Şimdilik mp3 olarak dönüyoruz.
        return Response(content=bytes(audio_buffer), media_type="audio/mpeg")

    except Exception as e:
        logger.error("Edge-TTS sentezleme sırasında hata", error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=f"Ses üretilirken hata oluştu: {e}")

@app.get("/health")
def health_check():
    return {"status": "ok"}