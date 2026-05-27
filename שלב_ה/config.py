"""Centralized database and application configuration."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

_BASE_DIR = Path(__file__).resolve().parent
load_dotenv(_BASE_DIR / ".env")
load_dotenv(_BASE_DIR.parent / ".env")


@dataclass(frozen=True)
class DatabaseConfig:
    host: str
    port: int
    name: str
    user: str
    password: str
    schema: str
    min_pool: int
    max_pool: int

    @property
    def dsn(self) -> str:
        return (
            f"host={self.host} port={self.port} dbname={self.name} "
            f"user={self.user} password={self.password}"
        )


@dataclass(frozen=True)
class AppConfig:
    title: str
    appearance_mode: str
    color_theme: str


def load_database_config() -> DatabaseConfig:
    return DatabaseConfig(
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", "5432")),
        name=os.getenv("DB_NAME", os.getenv("DB_NAME_SECRET", "postgres")),
        user=os.getenv("DB_USER", os.getenv("DB_USER_SECRET", "postgres")),
        password=os.getenv("DB_PASSWORD", os.getenv("DB_PASSWORD_SECRET", "")),
        schema=os.getenv("DB_SCHEMA", "labs"),
        min_pool=int(os.getenv("DB_POOL_MIN", "1")),
        max_pool=int(os.getenv("DB_POOL_MAX", "10")),
    )


def load_app_config() -> AppConfig:
    return AppConfig(
        title=os.getenv("APP_TITLE", "Medical Laboratory Management System"),
        appearance_mode=os.getenv("APP_APPEARANCE", "dark"),
        color_theme=os.getenv("APP_COLOR_THEME", "blue"),
    )
