import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    """应用配置类"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # 数据库配置
    database_url: str = os.getenv(
        "DATABASE_URL",
        "mysql+pymysql://root:59591468@127.0.0.1:3306/anime?charset=utf8mb4"
    )

    # AniList API
    anilist_api_url: str = "https://graphql.anilist.co"
    anilist_timeout: int = 10
    anilist_per_page: int = 5

    # CORS配置
    cors_origins: list[str] = ["*"]
    cors_credentials: bool = True
    cors_methods: list[str] = ["*"]
    cors_headers: list[str] = ["*"]

    # 应用配置
    app_name: str = "AnimeShow API"
    debug: bool = False


@lru_cache()
def get_settings() -> Settings:
    """获取配置单例"""
    return Settings()


settings = get_settings()
