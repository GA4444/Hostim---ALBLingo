#!/usr/bin/env python3
"""
Migration script to add profile fields (date_of_birth, address, phone_number) to users table
"""
import sqlite3
import os

DB_PATH = "dev.db"

def migrate():
    """Add profile columns to users table"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("🔄 Starting database migration for user profile fields...")
    
    # Check if columns already exist
    cursor.execute("PRAGMA table_info(users)")
    columns = [row[1] for row in cursor.fetchall()]
    
    migrations = [
        ("date_of_birth", "DATETIME"),
        ("address", "VARCHAR(255)"),
        ("phone_number", "VARCHAR(20)"),
    ]
    
    for column_name, column_def in migrations:
        if column_name not in columns:
            try:
                cursor.execute(f"ALTER TABLE users ADD COLUMN {column_name} {column_def}")
                print(f"✅ Added column: {column_name}")
            except sqlite3.OperationalError as e:
                print(f"⚠️  Column {column_name} might already exist or error: {e}")
        else:
            print(f"⏭️  Column {column_name} already exists, skipping.")
    
    conn.commit()
    conn.close()
    
    print("\n✅ Migration completed successfully!")


if __name__ == "__main__":
    if not os.path.exists(DB_PATH):
        print(f"❌ Database file '{DB_PATH}' not found!")
        print("Make sure you're running this from the backend/ directory.")
        exit(1)
    
    migrate()
