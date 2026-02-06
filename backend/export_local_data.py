#!/usr/bin/env python3
"""
Export local SQLite data to JSON files for migration.
"""
import sqlite3
import json
import os

LOCAL_DB_PATH = "dev.db"
EXPORT_DIR = "migration_export"

TABLES = [
    "users",
    "courses", 
    "levels",
    "exercises",
    "achievements",
    "daily_challenges",
    "attempts",
    "progress",
    "course_progress",
    "user_achievements",
    "user_daily_progress",
    "srs_cards",
    "chat_sessions",
    "chat_messages",
]

def export_table(conn, table_name):
    """Export a table to JSON"""
    cursor = conn.cursor()
    
    # Check if table exists
    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
        (table_name,)
    )
    if not cursor.fetchone():
        print(f"   ⏭️  Table {table_name} doesn't exist, skipping")
        return 0
    
    # Get column names
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = [row[1] for row in cursor.fetchall()]
    
    # Get data
    cursor.execute(f"SELECT * FROM {table_name}")
    rows = cursor.fetchall()
    
    if not rows:
        print(f"   ⏭️  Table {table_name} is empty, skipping")
        return 0
    
    # Convert to list of dicts
    data = []
    for row in rows:
        record = {}
        for i, col in enumerate(columns):
            val = row[i]
            # Convert SQLite integer booleans to actual booleans
            if col in ['enabled', 'is_correct', 'completed', 'is_completed', 
                       'is_unlocked', 'is_active', 'is_admin']:
                val = bool(val) if val is not None else None
            record[col] = val
        data.append(record)
    
    # Save to JSON
    filepath = os.path.join(EXPORT_DIR, f"{table_name}.json")
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, default=str, ensure_ascii=False)
    
    return len(data)

def main():
    print("=" * 60)
    print("📦 Exporting Local Database to JSON")
    print("=" * 60)
    
    # Create export directory
    os.makedirs(EXPORT_DIR, exist_ok=True)
    
    # Connect to SQLite
    conn = sqlite3.connect(LOCAL_DB_PATH)
    print(f"✅ Connected to {LOCAL_DB_PATH}")
    print()
    
    total = 0
    for table in TABLES:
        print(f"📋 Exporting: {table}")
        count = export_table(conn, table)
        if count > 0:
            print(f"   ✅ Exported {count} records")
            total += count
    
    conn.close()
    
    print()
    print("=" * 60)
    print(f"✅ Export complete! Total: {total} records")
    print(f"📁 Files saved in: {EXPORT_DIR}/")
    print("=" * 60)

if __name__ == "__main__":
    main()
