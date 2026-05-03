import asyncio
import aiosqlite
from pathlib import Path


async def migrate():
    """Add user_id column to stories and dictionary_words tables."""
    db_path = Path(__file__).parent.parent / "data" / "izypizy.db"
    
    async with aiosqlite.connect(str(db_path)) as db:
        await db.execute("PRAGMA foreign_keys = ON")
        db.row_factory = aiosqlite.Row
        
        # Migrate stories table
        async with db.execute("PRAGMA table_info(stories)") as cursor:
            columns = await cursor.fetchall()
            column_names = [col["name"] for col in columns]
        
        if "user_id" not in column_names:
            print("Adding user_id column to stories table...")
            await db.execute("ALTER TABLE stories ADD COLUMN user_id TEXT NOT NULL DEFAULT ''")
            await db.commit()
            print("Migration complete: user_id column added to stories")
        else:
            print("stories.user_id already exists")
        
        # Migrate dictionary_words table
        async with db.execute("PRAGMA table_info(dictionary_words)") as cursor:
            columns = await cursor.fetchall()
            column_names = [col["name"] for col in columns]
        
        if "user_id" not in column_names:
            print("Adding user_id column to dictionary_words table...")
            await db.execute("ALTER TABLE dictionary_words ADD COLUMN user_id TEXT NOT NULL DEFAULT ''")
            await db.commit()
            print("Migration complete: user_id column added to dictionary_words")
        else:
            print("dictionary_words.user_id already exists")


if __name__ == "__main__":
    asyncio.run(migrate())