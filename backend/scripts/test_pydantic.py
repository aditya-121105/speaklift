import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from app.core.config import Settings

try:
    s = Settings(
        APP_NAME="TestApp",
        APP_VERSION="1.0.0",
        DATABASE_URL="sqlite:///:memory:",
        JWT_SECRET_KEY="secret",
        JWT_ALGORITHM="HS256",
        ACCESS_TOKEN_EXPIRE_MINUTES=30,
        _env_file=None
    )
    print("API_KEY:", s.GEMINI_API_KEY)
    print("MODEL:", s.GEMINI_DEFAULT_MODEL)
    print("SUCCESS")
except Exception as e:
    print("ERROR:", e)
