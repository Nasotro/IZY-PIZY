#!/usr/bin/env python3
import sqlite3
import os

# Get the database path from environment or default
from dotenv import load_dotenv
load_dotenv()

db_path = os.getenv("DATABASE_URL", "../data/izypizy.db")

if not os.path.exists(db_path):
    print(f"Database not found at: {db_path}")
    exit(1)

print(f"Checking database: {db_path}")

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Check if stories table exists
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print(f"\nTables: {[t[0] for t in tables]}")

# Check stories with images
cursor.execute("SELECT id, image_path FROM stories WHERE image_path IS NOT NULL")
rows = cursor.fetchall()

if rows:
    print(f"\nStories with images ({len(rows)}):")
    for row in rows:
        story_id, image_path = row
        print(f"  Story {story_id}: image_path = '{image_path}'")
        
        # Check if the path has the old format
        if image_path and image_path.startswith("images/"):
            print(f"    WARNING: This path has the old 'images/' prefix!")
            print(f"    It should be: '{image_path.replace('images/', '')}'")
else:
    print("\nNo stories with images found.")

conn.close()
