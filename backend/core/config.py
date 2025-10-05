from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env.example", env_file_encoding="utf-8", extra='ignore')
    NASA_API_KEY: str = "DEMO_KEY"

settings = Settings()