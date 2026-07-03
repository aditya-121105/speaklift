from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str
    APP_VERSION: str

    DATABASE_URL: str

    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    # ---------------------------------------------------------------------------
    # Storage
    # ---------------------------------------------------------------------------
    # STORAGE_BACKEND selects the active storage driver.
    # Supported: "local" | future: "s3"
    STORAGE_BACKEND: str = "local"

    # Root directory for local file storage (relative to backend/ or absolute).
    STORAGE_LOCAL_ROOT: str = "./uploads"

    # Maximum allowed resume file size in megabytes.
    MAX_RESUME_SIZE_MB: int = 10

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
    )


settings = Settings()