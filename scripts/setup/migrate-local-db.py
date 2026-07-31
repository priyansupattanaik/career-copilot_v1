"""Create or update the local SQLite database from the checked-in schema."""

import sqlite3
from pathlib import Path

from app.core.config import get_settings


def main() -> None:
    settings = get_settings()
    database_path = Path(settings.database_path).resolve()
    database_path.parent.mkdir(parents=True, exist_ok=True)
    storage_root = Path(settings.local_storage_dir).resolve()
    for bucket in (settings.document_bucket, settings.avatar_bucket, settings.interview_bucket):
        (storage_root / bucket).mkdir(parents=True, exist_ok=True)
    schema_path = Path(__file__).resolve().parents[2] / "db" / "schema.sql"
    with sqlite3.connect(database_path) as connection:
        connection.execute("PRAGMA foreign_keys = ON")
        connection.execute("PRAGMA busy_timeout = 10000")
        connection.execute("PRAGMA journal_mode = WAL")
        connection.execute("PRAGMA synchronous = NORMAL")
        connection.executescript(schema_path.read_text(encoding="utf-8"))
    print(f"Applied SQLite schema to {database_path}")


if __name__ == "__main__":
    main()
