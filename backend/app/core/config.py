from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=('.env', 'backend/.env'),
        env_file_encoding='utf-8',
    )

    APP_NAME: str = 'PK SKDK'
    ENV: str = 'local'
    DATABASE_URL: str
    JWT_SECRET: str = 'change-me'
    JWT_ALGORITHM: str = 'HS256'
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

settings = Settings()
