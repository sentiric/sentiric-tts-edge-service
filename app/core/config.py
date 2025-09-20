# sentiric-tts-edge-service/app/core/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    PROJECT_NAME: str = "Sentiric Edge TTS Service"
    API_V1_STR: str = "/api/v1"
    ENV: str = Field("production", validation_alias="ENV")
    # DEĞİŞİKLİK: LOG_LEVEL'i config'e ekliyoruz.
    LOG_LEVEL: str = Field("INFO", validation_alias="LOG_LEVEL")

    # Build-time bilgilerini de ekleyelim
    SERVICE_VERSION: str = Field("0.0.0", validation_alias="SERVICE_VERSION")
    GIT_COMMIT: str = Field("unknown", validation_alias="GIT_COMMIT")
    BUILD_DATE: str = Field("unknown", validation_alias="BUILD_DATE")
    
    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding='utf-8', 
        extra='ignore', 
        case_sensitive=False
    )

settings = Settings()