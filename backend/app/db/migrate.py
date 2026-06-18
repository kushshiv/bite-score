"""Run Alembic migrations programmatically."""

from pathlib import Path

from alembic import command
from alembic.config import Config


def alembic_config() -> Config:
    backend_root = Path(__file__).resolve().parents[2]
    config = Config(str(backend_root / "alembic.ini"))
    return config


def run_migrations(revision: str = "head") -> None:
    command.upgrade(alembic_config(), revision)


def main() -> None:
    run_migrations()
    print("Database migrations applied.")
