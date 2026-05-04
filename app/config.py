from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql://portfolio:portfolio@db:5432/portfolio"
    secret_key: str = "change-me-in-production-use-long-random-string"
    admin_username: str = "admin"
    admin_password: str = "change-me"
    upload_dir: str = "/uploads"

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
