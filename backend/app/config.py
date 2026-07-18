from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


ENV_PATH = Path(__file__).resolve().parents[1] / ".env"


class Settings(BaseSettings):
    app_name: str = "Kissan AI MemoryAgent"
    environment: str = "development"
    database_url: str = "sqlite:///./kissan_ai.db"
    frontend_dir: str = ".."
    qwen_api_base: str | None = "https://dashscope-intl.aliyuncs.com/compatible-mode/v1"
    qwen_api_key: str | None = None
    qwen_model: str = "qwen-plus"
    mem0_api_key: str | None = None
    mem0_api_base: str = "https://api.mem0.ai"
    openweather_api_key: str | None = None
    vector_db_url: str | None = None

    model_config = SettingsConfigDict(
        env_file=ENV_PATH,
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def frontend_path(self) -> Path:
        return Path(__file__).resolve().parents[1] / self.frontend_dir

    @property
    def database_url_resolved(self) -> str:
        if self.database_url.startswith("sqlite:///./"):
            db_name = self.database_url.replace("sqlite:///./", "")
            abs_path = (Path(__file__).resolve().parents[1] / db_name).resolve().as_posix()
            return f"sqlite:///{abs_path}"
        elif self.database_url.startswith("sqlite:///"):
            db_path = self.database_url.replace("sqlite:///", "")
            path_obj = Path(db_path)
            if not path_obj.is_absolute():
                abs_path = (Path(__file__).resolve().parents[1] / path_obj).resolve().as_posix()
                return f"sqlite:///{abs_path}"
        return self.database_url


@lru_cache
def get_settings() -> Settings:
    return Settings()

