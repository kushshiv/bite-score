from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    database_url: str = "postgresql+psycopg2://bitescore:bitescore@localhost:5432/bitescore"
    jwt_secret: str = "change-me-to-a-long-random-secret-key"
    jwt_expire_minutes: int = 10080
    cors_origins: str = "http://localhost:3000"
    upload_dir: str = "./uploads"
    api_base_url: str = "http://localhost:8000"

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


settings = Settings()
