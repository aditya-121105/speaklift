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

    # ---------------------------------------------------------------------------
    # LLM Infrastructure Configuration
    # ---------------------------------------------------------------------------
    # General LLM defaults
    LLM_DEFAULT_PROVIDER: str = "ollama"
    LLM_DEFAULT_MODEL: str = "llama3.1:8b"
    LLM_REQUEST_TIMEOUT: int = 60
    LLM_RETRY_COUNT: int = 3
    LLM_TEMPERATURE: float = 0.7
    LLM_MAX_OUTPUT_TOKENS: int = 2048
    LLM_ROUTING_STRATEGY: str = "prefer_local"  # prefer_local, prefer_cloud, local_only, cloud_only

    # Gemini specific
    # Gemini specific
    GEMINI_API_KEY: str | None = None
    GEMINI_DEFAULT_MODEL: str = "gemini-3.5-flash"

    # Ollama specific
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_DEFAULT_MODEL: str = "llama3.1:8b"

    # ---------------------------------------------------------------------------
    # Security & Operational Settings
    # ---------------------------------------------------------------------------
    ALLOWED_HOSTS: list[str] = ["*"]
    CORS_ORIGINS: list[str] = ["*"]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: list[str] = ["*"]
    CORS_ALLOW_HEADERS: list[str] = ["*"]
    RATE_LIMIT_PER_MINUTE: int = 60
    MAX_REQUEST_SIZE_BYTES: int = 15_000_000  # 15MB

    def validate_configuration(self):
        """Perform deeper cross-field validation at startup."""
        if self.LLM_ROUTING_STRATEGY in ("prefer_cloud", "cloud_only") and not self.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is required for cloud routing strategies.")
        if self.ACCESS_TOKEN_EXPIRE_MINUTES <= 0:
            raise ValueError("ACCESS_TOKEN_EXPIRE_MINUTES must be positive.")

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
    )


settings = Settings()