#!/usr/bin/env python3
"""
Script to check and fix existing image paths in the database.
"""
import sqlite3
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

db_path = os.getenv("DATABASE_URL", "../data/izypizy.db")
image_dir = Path(os.getenv("IMAGE_STORAGE_DIR", "../data/images"))

print(f"Database: {db_path}")
print(f"Image directory: {image_dir}")
print()

conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# Get all stories with images
cursor.execute("SELECT id, image_path FROM stories WHERE image_path IS NOT NULL")
rows = cursor.fetchall()

if not rows:
    print("No stories with images found.")
    conn.close()
    exit(0)

print(f"Found {len(rows)} stories with images:\n")

needs_fix = []
files_exist = []
files_missing = []

for row in rows:
    story_id = row['id']
    image_path = row['image_path']
    
    # Check if path has old format
    has_prefix = image_path.startswith("images/")
    
    # Check if file exists
    if has_prefix:
        # Old format: images/filename.png
        relative_path = image_path
        full_path = image_dir / image_path
    else:
        # New format: filename.png
        relative_path = image_path
        full_path = image_dir / image_path
    
    exists = full_path.exists()
    
    print(f"Story {story_id}:")
    print(f"  DB path: {image_path}")
    print(f"  Full path: {full_path}")
    print(f"  Has 'images/' prefix: {has_prefix}")
    print(f"  File exists: {exists}")
    
    if has_prefix:
        needs_fix.append((story_id, image_path))
    
    if exists:
        files_exist.append((story_id, image_path))
    else:
        files_missing.append((story_id, image_path))
    
    print()

print("=" * 60)
print(f"Stories needing path fix (have 'images/' prefix): {len(needs_fix)}")
print(f"Files that exist on disk: {len(files_exist)}")
print(f"Files missing from disk: {len(files_missing)}")
print("=" * 60)

# Ask if user wants to fix
if needs_fix:
    print("\nDo you want to fix the paths in the database (remove 'images/' prefix)?")
    print("This will update the database but NOT move any files.")
    print("Type 'yes' to fix:")
    response = input().strip().lower()
    
    if response == 'yes':
        print("\nFixing paths...")
        for story_id, old_path in needs_fix:
            new_path = old_path.replace("images/", "")
            cursor.execute(
                "UPDATE stories SET image_path = ? WHERE id = ?",
                (new_path, story_id)
            )
            print(f"  Story {story_id}: {old_path} -> {new_path}")
        conn.commit()
        print("\nPaths fixed in database!")
    else:
        print("No changes made.")

conn.close()
