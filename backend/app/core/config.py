from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 1  # 1 ngày
    
    DATABASE_URL: str
    
    MQTT_BROKER: str
    MQTT_PORT: int
    MQTT_USER: Optional[str] = None
    MQTT_PASSWORD: Optional[str] = None

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()