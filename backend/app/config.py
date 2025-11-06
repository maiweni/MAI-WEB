from functools import lru_cache
from typing import List

from pydantic import field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = (
        "mysql+aiomysql://mai_user:mai_password@localhost:3306/mai_db"
    )
    backend_cors_origins: str | List[str] = "http://localhost:5173"

    @field_validator("backend_cors_origins", mode="before")
    @classmethod
    def split_origins(cls, value):
        if isinstance(value, str):
            return [
                origin.strip() for origin in value.split(",") if origin.strip()
            ]
        return value

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
