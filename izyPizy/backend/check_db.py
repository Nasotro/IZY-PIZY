#!/usr/bin/env python3
import sqlite3
import os

# Try both possible locations
db_paths = [
    os.path.abspath('../data/izypizy.db'),
    os.path.abspath('C:/Users/lorra/Documents/Projets/data/izypizy.db'),
]

for db_path in db_paths:
    if os.path.exists(db_path):
        print(f"Found DB at: {db_path}")
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            print(f"Tables: {tables}")
            
            cursor.execute("SELECT id, image_path FROM stories WHERE image_path IS NOT NULL")
            images = cursor.fetchall()
            print(f"\nStories with images ({len(images)}):")
            for story_id, image_path in images:
                print(f"  Story {story_id}: {image_path}")
            conn.close()
            break
        except Exception as e:
            print(f"Error: {e}")
else:
    print("Database not found in expected locations")
