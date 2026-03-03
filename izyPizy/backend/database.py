import os
import aiosqlite
from pathlib import Path

from config import DATABASE_URL

SCHEMA_PATH = Path(__file__).parent / "schema.sql"


async def init_db() -> None:
    """Create tables and seed dictionary_numbers (00–99)."""
    # Ensure the data directory exists
    db_path = Path(DATABASE_URL)
    db_path.parent.mkdir(parents=True, exist_ok=True)

    async with aiosqlite.connect(DATABASE_URL) as db:
        # Enable foreign key support
        await db.execute("PRAGMA foreign_keys = ON")

        # Execute schema
        schema = SCHEMA_PATH.read_text(encoding="utf-8")
        await db.executescript(schema)

        # Seed all 100 two-digit pairs
        await db.executemany(
            "INSERT OR IGNORE INTO dictionary_numbers (number) VALUES (?)",
            [(f"{i:02d}",) for i in range(100)],
        )
        await db.commit()


async def get_db():
    """FastAPI dependency: yields an aiosqlite connection."""
    async with aiosqlite.connect(DATABASE_URL) as db:
        await db.execute("PRAGMA foreign_keys = ON")
        db.row_factory = aiosqlite.Row
        yield db
