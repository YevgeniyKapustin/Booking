from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    app_name: str = "Booking"
    app_timezone: str = "UTC"
    booking_max_days_ahead: int = 30
    booking_slot_minutes: int = 15
    booking_duration_minutes: int = 120
    booking_open_time: str = "12:00"
    booking_close_time: str = "22:00"
    database_url: str = ""
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "tablereservations"
    postgres_user: str = "tablereservations"
    postgres_password: str = "tablereservations"
    jwt_secret: str = ""
    jwt_algorithm: str = "HS256"
    jwt_expires_minutes: int = 60
    redis_url: str = "redis://localhost:6379/0"
    log_level: str = "INFO"
    log_dir: str = "logs"
    log_file: str = "app.log"
    log_rotation_when: str = "midnight"
    log_backup_count: int = 7
    log_color: bool = True
    smtp_host: str = "localhost"
    smtp_port: int = 1025
    smtp_user: str = ""
    smtp_password: str = ""
    smtp_from: str = "noreply@example.com"
    smtp_tls: bool = False


settings = Settings()


def build_database_url(settings_obj: Settings) -> str:
    if settings_obj.database_url:
        return settings_obj.database_url
    return (
        "postgresql+asyncpg://"
        f"{settings_obj.postgres_user}:{settings_obj.postgres_password}"
        f"@{settings_obj.postgres_host}:{settings_obj.postgres_port}/{settings_obj.postgres_db}"
    )
