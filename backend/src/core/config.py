"""应用配置模块."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """应用配置."""

    # API配置
    API_V1_PREFIX: str = "/v1"

    # OpenDota API配置
    OPENDOTA_API_BASE_URL: str = "https://api.opendota.com/api"

    # 服务器配置
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = False
    
    # CORS配置（生产环境需要设置前端域名）
    CORS_ORIGINS: str = "*"  # 生产环境应改为具体域名，如 "https://your-app.vercel.app"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()

