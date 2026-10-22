import os
import aiosqlite
from pathlib import Path

from config import DATABASE_URL

SCHEMA_PATH = Path(__file__).parent / "schema.sql"

# Columns the code expects. Existing databases are upgraded in place by
# init_db(): CREATE TABLE IF NOT EXISTS never touches a table that already
# exists, so an old volume (schema from a previous deploy) used to keep
# missing columns forever and every query on it returned HTTP 500.
EXPECTED_COLUMNS = {
    "stories": {
        "user_id": "TEXT NOT NULL DEFAULT ''",
        "position": "INTEGER NOT NULL DEFAULT 0",
        "sentence": "TEXT",
        "word_0": "TEXT NOT NULL DEFAULT ''",
        "word_1": "TEXT NOT NULL DEFAULT ''",
        "word_2": "TEXT NOT NULL DEFAULT ''",
        "word_3": "TEXT NOT NULL DEFAULT ''",
        "word_4": "TEXT NOT NULL DEFAULT ''",
        "image_path": "TEXT",
    },
    "dictionary_words": {
        "user_id": "TEXT NOT NULL DEFAULT ''",
        "number": "TEXT NOT NULL DEFAULT ''",
        "word": "TEXT NOT NULL DEFAULT ''",
    },
}


async def _migrate_schema(db: aiosqlite.Connection) -> list[str]:
    """Add any missing columns to existing tables. Returns a log of changes."""
    changes: list[str] = []
    for table, columns in EXPECTED_COLUMNS.items():
        async with db.execute(f"PRAGMA table_info({table})") as cursor:
            rows = await cursor.fetchall()
        existing = {row[1] for row in rows}
        if not existing:
            continue  # table does not exist yet: schema.sql just created it
        for name, ddl in columns.items():
            if name not in existing:
                await db.execute(f"ALTER TABLE {table} ADD COLUMN {name} {ddl}")
                changes.append(f"{table}.{name}")
    return changes


async def init_db() -> None:
    """Create tables, upgrade old databases and seed dictionary_numbers (00–99)."""
    # Ensure the data directory exists
    db_path = Path(DATABASE_URL)
    db_path.parent.mkdir(parents=True, exist_ok=True)

    async with aiosqlite.connect(DATABASE_URL) as db:
        # Enable foreign key support
        await db.execute("PRAGMA foreign_keys = ON")

        # Execute schema
        schema = SCHEMA_PATH.read_text(encoding="utf-8")
        await db.executescript(schema)

        # Bring pre-existing tables up to date (idempotent)
        changes = await _migrate_schema(db)
        if changes:
            print(f"[db] migrated columns: {', '.join(changes)}")

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
