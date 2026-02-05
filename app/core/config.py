
from pydantic import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    APP_NAME: str = "PAY CREST API"
    API_PREFIX: str = "/api"
    MONGODB_URI: str = "mongodb://localhost:27017"
    MONGODB_DB: str = "pay_crest"

    JWT_SECRET: str = "CHANGE_ME"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 60 * 24

    DEFAULT_IFSC: str = "PCIN0000"

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
