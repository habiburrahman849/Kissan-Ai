from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


ENV_PATH = Path(__file__).resolve().parents[1] / ".env"
# backend/ is parents[1] of config.py (app/config.py → backend)
BACKEND_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = BACKEND_DIR.parent


class Settings(BaseSettings):
    app_name: str = "Kissan AI MemoryAgent"
    environment: str = "development"
    database_url: str = "sqlite:///./kissan_ai_v2.db"
    # Relative to backend/ — default is ../static (repo static/ folder)
    frontend_dir: str = "../static"
    # Also accept absolute path via FRONTEND_DIR env if needed
    port: int = 8000

    qwen_api_base: str | None = "https://dashscope-intl.aliyuncs.com/compatible-mode/v1"
    qwen_api_key: str | None = None
    qwen_model: str = "qwen-plus"
    mem0_api_key: str | None = None
    mem0_api_base: str = "https://api.mem0.ai"
    openweather_api_key: str | None = None
    vector_db_url: str | None = None

    # Legacy Clerk keys (unused — guest + email/password auth)
    clerk_publishable_key: str | None = None
    clerk_secret_key: str | None = None

    # Auth
    google_client_id: str | None = None
    jwt_secret: str = "kissan-ai-dev-secret-change-me-32b+"
    jwt_expire_hours: int = 168  # 7 days
    allow_guest_login: bool = True
    # Dev-only: accept fake Google tokens when client id not configured
    auth_dev_bypass: bool = True

    model_config = SettingsConfigDict(
        env_file=ENV_PATH,
        env_file_encoding="utf-8",
        extra="ignore",
    )

    def model_post_init(self, __context) -> None:
        # Harden production defaults without requiring every env var
        if (self.environment or "").lower() in {"production", "prod", "render"}:
            self.auth_dev_bypass = False

    @property
    def frontend_path(self) -> Path:
        """Resolve static frontend directory (HTML/CSS/JS)."""
        raw = (self.frontend_dir or "../static").strip()
        path = Path(raw)
        if path.is_absolute():
            return path
        # Relative paths are from backend/
        return (BACKEND_DIR / path).resolve()

    @property
    def database_url_resolved(self) -> str:
        if self.database_url.startswith("sqlite:///./"):
            db_name = self.database_url.replace("sqlite:///./", "")
            abs_path = (BACKEND_DIR / db_name).resolve().as_posix()
            return f"sqlite:///{abs_path}"
        if self.database_url.startswith("sqlite:///"):
            db_path = self.database_url.replace("sqlite:///", "")
            path_obj = Path(db_path)
            if not path_obj.is_absolute():
                abs_path = (BACKEND_DIR / path_obj).resolve().as_posix()
                return f"sqlite:///{abs_path}"
        return self.database_url


@lru_cache
def get_settings() -> Settings:
    return Settings()
