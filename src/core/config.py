"""
Configuration module using pydantic-settings.
Priority: 1. .env, 2. config.yaml, 3. defaults
"""

from pathlib import Path

import yaml
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
CONFIG_FILE = PROJECT_ROOT / "config" / "config.yaml"


def load_yaml_settings():
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, "r") as f:
            return yaml.safe_load(f) or {}
    return {}


class Settings(BaseSettings):
    project_name: str = "FintechProject1"
    project_version: str = "0.1.0"

    # Database (secrets from .env)
    db_driver: str = "postgresql+psycopg2"
    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str = "fintech_db"
    db_user: str = "admin"
    db_password: str = "secret"

    # SQLite overrides
    use_sqlite: bool = False
    sqlite_path: str = "sqlite:///./fintech.db"

    log_level: str = "INFO"
    log_file: str = "logs/pipeline.log"

    # Dataset Intelligence Engine
    max_safe_rows: int = 500000
    medium_dataset_threshold: int = 100000
    default_sample_size: int = 250000
    dataset_mode: str = "interactive" # "interactive" or "automatic"
    model_target_column: str = "loan_status"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @property
    def database_url(self) -> str:
        """Returns the appropriate database URL based on configuration."""
        if self.use_sqlite:
            return self.sqlite_path
        return f"{self.db_driver}://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"

    @classmethod
    def load_all_settings(cls):
        load_yaml_settings()
        # Environment variables will automatically override any default instantiated here
        return cls()


settings = Settings.load_all_settings()
