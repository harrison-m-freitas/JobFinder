from __future__ import annotations

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # ===== Somente snake_case como CAMPOS =====
    app_env: str = Field(default="dev", alias="APP_ENV")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    postgres_host: str = Field(default="db", alias="POSTGRES_HOST")
    postgres_port: int = Field(default=5432, alias="POSTGRES_PORT")
    postgres_db: str = Field(default="jobhunter", alias="POSTGRES_DB")
    postgres_user: str = Field(default="app", alias="POSTGRES_USER")
    postgres_password: str = Field(default="app", alias="POSTGRES_PASSWORD")
    database_url: str | None = Field(default=None, alias="DATABASE_URL")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # App/servidor
    app_host: str = Field(default="127.0.0.1", alias="APP_HOST")
    app_port: int = Field(default=8000, alias="APP_PORT")

    @property
    def sqlalchemy_url(self) -> str:
        if self.database_url:
            return self.database_url
        return (
            f"postgresql+psycopg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    # ===== Propriedades de compatibilidade (UPPER_CASE) =====
    @property
    def APP_ENV(self) -> str:
        return self.app_env

    @property
    def LOG_LEVEL(self) -> str:
        return self.log_level

    @property
    def POSTGRES_HOST(self) -> str:
        return self.postgres_host

    @property
    def POSTGRES_PORT(self) -> int:
        return self.postgres_port

    @property
    def POSTGRES_DB(self) -> str:
        return self.postgres_db

    @property
    def POSTGRES_USER(self) -> str:
        return self.postgres_user

    @property
    def POSTGRES_PASSWORD(self) -> str:
        return self.postgres_password

    @property
    def DATABASE_URL(self) -> str | None:
        return self.database_url


settings = Settings()
