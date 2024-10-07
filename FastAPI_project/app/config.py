from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://postgres:123456@localhost/student"

    class Config:
        env_file = ".env"

settings = Settings()
