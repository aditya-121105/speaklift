import os
import pytest
from app.core.config import Settings

def test_default_configuration():
    # We must construct a Settings instance without environment overrides
    # if .env is present, it might override defaults.
    # By omitting parameters and unsetting env vars if needed, we can test defaults.
    
    # Temporarily remove any env vars that might interfere during the test
    original_env = {}
    env_keys_to_clear = [
        "LLM_DEFAULT_PROVIDER",
        "LLM_DEFAULT_MODEL",
        "GEMINI_API_KEY",
        "OLLAMA_BASE_URL"
    ]
    for k in env_keys_to_clear:
        if k in os.environ:
            original_env[k] = os.environ.pop(k)
            
    # Need to supply the required fields for the app to not crash when instantiating Settings
    try:
        # Pass required fields explicitly to ignore .env requirements for this instance
        settings = Settings(
            APP_NAME="TestApp",
            APP_VERSION="1.0.0",
            DATABASE_URL="sqlite:///:memory:",
            JWT_SECRET_KEY="secret",
            JWT_ALGORITHM="HS256",
            ACCESS_TOKEN_EXPIRE_MINUTES=30,
            _env_file=None
        )
        
        # Verify defaults
        assert settings.LLM_DEFAULT_PROVIDER == "ollama"
        assert settings.LLM_DEFAULT_MODEL == "llama3.1:8b"
        assert settings.LLM_REQUEST_TIMEOUT == 60
        assert settings.LLM_RETRY_COUNT == 3
        assert settings.LLM_TEMPERATURE == 0.7
        assert settings.LLM_MAX_OUTPUT_TOKENS == 2048
        
        # GEMINI_API_KEY may be loaded from .env, so we only verify its type
        assert isinstance(settings.GEMINI_API_KEY, (str, type(None)))
        assert settings.GEMINI_DEFAULT_MODEL == "gemini-3.5-flash"
        
        assert settings.OLLAMA_BASE_URL == "http://localhost:11434"
        assert settings.OLLAMA_DEFAULT_MODEL == "llama3.1:8b"
    finally:
        for k, v in original_env.items():
            os.environ[k] = v

def test_environment_variable_overrides(monkeypatch):
    monkeypatch.setenv("LLM_DEFAULT_PROVIDER", "gemini")
    monkeypatch.setenv("LLM_TEMPERATURE", "0.2")
    monkeypatch.setenv("GEMINI_API_KEY", "super-secret-key")
    
    settings = Settings(
        APP_NAME="TestApp",
        APP_VERSION="1.0.0",
        DATABASE_URL="sqlite:///:memory:",
        JWT_SECRET_KEY="secret",
        JWT_ALGORITHM="HS256",
        ACCESS_TOKEN_EXPIRE_MINUTES=30
    )
    
    assert settings.LLM_DEFAULT_PROVIDER == "gemini"
    assert settings.LLM_TEMPERATURE == 0.2
    assert settings.GEMINI_API_KEY == "super-secret-key"

def test_optional_api_keys():
    settings = Settings(
        APP_NAME="TestApp",
        APP_VERSION="1.0.0",
        DATABASE_URL="sqlite:///:memory:",
        JWT_SECRET_KEY="secret",
        JWT_ALGORITHM="HS256",
        ACCESS_TOKEN_EXPIRE_MINUTES=30,
        _env_file=None,
        GEMINI_API_KEY=None  # Explicit override behavior
    )
    # The default behavior ensures sensitive values don't crash when missing
    assert settings.GEMINI_API_KEY is None

def test_model_configuration(monkeypatch):
    monkeypatch.setenv("GEMINI_DEFAULT_MODEL", "gemini-1.5-pro")
    
    settings = Settings(
        APP_NAME="TestApp",
        APP_VERSION="1.0.0",
        DATABASE_URL="sqlite:///:memory:",
        JWT_SECRET_KEY="secret",
        JWT_ALGORITHM="HS256",
        ACCESS_TOKEN_EXPIRE_MINUTES=30
    )
    
    assert settings.GEMINI_DEFAULT_MODEL == "gemini-1.5-pro"
