#!/usr/bin/env python3
"""
Migration script to fix image paths in the database.
Removes the 'images/' prefix from all image_path values in the stories table.

This should be run once after deploying the fixed code.
"""
import sqlite3
import os
from pathlib import Path
from dotenv import load_dotenv

# Load configuration
load_dotenv()

def get_db_path():
    """Get the absolute path to the database."""
    db_url = os.getenv("DATABASE_URL", "../data/izypizy.db")
    # If it's a relative path, resolve it relative to the backend directory
    backend_dir = Path(__file__).parent.parent
    if not os.path.isabs(db_url):
        return (backend_dir / db_url).resolve()
    return Path(db_url)

def main():
    db_path = get_db_path()
    print(f"Database path: {db_path}")
    
    if not db_path.exists():
        print("Database does not exist yet. No migration needed.")
        return
    
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    # Check if stories table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='stories'")
    if not cursor.fetchone():
        print("Stories table does not exist yet. No migration needed.")
        conn.close()
        return
    
    # Find all stories with the old path format
    cursor.execute("SELECT id, image_path FROM stories WHERE image_path LIKE 'images/%' ESCAPE '\\'")
    old_paths = cursor.fetchall()
    
    if not old_paths:
        print("No old image paths found. Database is already migrated.")
        conn.close()
        return
    
    print(f"\nFound {len(old_paths)} stories with old image path format (images/ prefix):")
    for story_id, image_path in old_paths:
        print(f"  Story {story_id}: {image_path}")
    
    print("\nMigrating paths (removing 'images/' prefix)...")
    for story_id, old_path in old_paths:
        new_path = old_path.replace("images/", "", 1)  # Only replace first occurrence
        cursor.execute(
            "UPDATE stories SET image_path = ? WHERE id = ?",
            (new_path, story_id)
        )
        print(f"  Story {story_id}: {old_path} -> {new_path}")
    
    conn.commit()
    print(f"\n✓ Migrated {len(old_paths)} image paths.")
    
    # Verify
    cursor.execute("SELECT id, image_path FROM stories WHERE image_path LIKE 'images/%' ESCAPE '\\'")
    remaining = cursor.fetchall()
    if remaining:
        print(f"\n⚠ WARNING: {len(remaining)} paths still have 'images/' prefix:")
        for story_id, image_path in remaining:
            print(f"  Story {story_id}: {image_path}")
    else:
        print("\n✓ All image paths have been migrated successfully.")
    
    conn.close()

if __name__ == "__main__":
    main()
