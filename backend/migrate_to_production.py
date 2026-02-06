#!/usr/bin/env python3
"""
Migration Script: SQLite (local) → PostgreSQL (Render production)

This script exports all data from your local dev.db and imports it
into the production PostgreSQL database on Render.

Usage:
    python migrate_to_production.py

Make sure to set the PRODUCTION_DATABASE_URL environment variable
or edit the URL directly in this script.
"""

import os
import sqlite3
from datetime import datetime

# Production PostgreSQL URL - PASTE YOUR RENDER DATABASE URL HERE
PRODUCTION_DATABASE_URL = os.getenv(
    "PRODUCTION_DATABASE_URL",
    "postgresql://alblingo_yzes_user:9aJ8fnKKlIGAaIbeWhnln9uqydrXutMu@dpg-d5ubcja4d50c73d1amt0-a.frankfurt-postgres.render.com/alblingo_yzes"
)

# Local SQLite database
LOCAL_DB_PATH = "dev.db"

# Tables to migrate in order (respecting foreign key dependencies)
TABLES_TO_MIGRATE = [
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


def get_sqlite_connection():
    """Connect to local SQLite database"""
    if not os.path.exists(LOCAL_DB_PATH):
        print(f"❌ Local database not found: {LOCAL_DB_PATH}")
        print("   Make sure you're running this from the backend directory")
        exit(1)
    return sqlite3.connect(LOCAL_DB_PATH)


def get_postgres_connection():
    """Connect to production PostgreSQL database"""
    try:
        import psycopg2
    except ImportError:
        print("❌ psycopg2 not installed. Run: pip install psycopg2-binary")
        exit(1)
    
    return psycopg2.connect(PRODUCTION_DATABASE_URL)


def get_table_columns(sqlite_conn, table_name):
    """Get column names for a table"""
    cursor = sqlite_conn.cursor()
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = [row[1] for row in cursor.fetchall()]
    return columns


def get_table_data(sqlite_conn, table_name):
    """Get all data from a SQLite table"""
    cursor = sqlite_conn.cursor()
    cursor.execute(f"SELECT * FROM {table_name}")
    return cursor.fetchall()


def table_exists_sqlite(sqlite_conn, table_name):
    """Check if table exists in SQLite"""
    cursor = sqlite_conn.cursor()
    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
        (table_name,)
    )
    return cursor.fetchone() is not None


def table_exists_postgres(pg_conn, table_name):
    """Check if table exists in PostgreSQL"""
    cursor = pg_conn.cursor()
    cursor.execute(
        "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = %s)",
        (table_name,)
    )
    return cursor.fetchone()[0]


def clear_postgres_table(pg_conn, table_name):
    """Clear all data from a PostgreSQL table"""
    cursor = pg_conn.cursor()
    try:
        cursor.execute(f"TRUNCATE TABLE {table_name} CASCADE")
        pg_conn.commit()
    except Exception as e:
        pg_conn.rollback()
        print(f"   ⚠️  Could not truncate {table_name}: {e}")


def get_postgres_column_types(pg_conn, table_name):
    """Get column types for a PostgreSQL table"""
    cursor = pg_conn.cursor()
    cursor.execute("""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_name = %s
        ORDER BY ordinal_position
    """, (table_name,))
    return {row[0]: row[1] for row in cursor.fetchall()}


def migrate_table(sqlite_conn, pg_conn, table_name):
    """Migrate a single table from SQLite to PostgreSQL"""
    
    # Check if table exists in SQLite
    if not table_exists_sqlite(sqlite_conn, table_name):
        print(f"   ⏭️  Table {table_name} doesn't exist in SQLite, skipping")
        return 0
    
    # Check if table exists in PostgreSQL
    if not table_exists_postgres(pg_conn, table_name):
        print(f"   ⏭️  Table {table_name} doesn't exist in PostgreSQL, skipping")
        return 0
    
    # Get columns and data
    columns = get_table_columns(sqlite_conn, table_name)
    data = get_table_data(sqlite_conn, table_name)
    
    if not data:
        print(f"   ⏭️  Table {table_name} is empty, skipping")
        return 0
    
    # Get PostgreSQL column types for type conversion
    pg_column_types = get_postgres_column_types(pg_conn, table_name)
    
    # Clear existing data in PostgreSQL
    clear_postgres_table(pg_conn, table_name)
    
    # Build INSERT query
    placeholders = ", ".join(["%s"] * len(columns))
    columns_str = ", ".join(columns)
    insert_query = f"INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders})"
    
    # Insert data
    pg_cursor = pg_conn.cursor()
    inserted = 0
    errors = 0
    
    for row in data:
        try:
            # Convert values based on PostgreSQL column types
            converted_row = []
            for i, val in enumerate(row):
                col_name = columns[i]
                pg_type = pg_column_types.get(col_name, 'text')
                
                if val is None:
                    converted_row.append(None)
                elif isinstance(val, str) and val == '':
                    converted_row.append(None)
                elif pg_type == 'boolean':
                    # Convert SQLite integer to PostgreSQL boolean
                    converted_row.append(bool(val) if val is not None else None)
                else:
                    converted_row.append(val)
            
            pg_cursor.execute(insert_query, tuple(converted_row))
            inserted += 1
        except Exception as e:
            errors += 1
            pg_conn.rollback()  # Rollback the failed transaction
            if errors <= 3:  # Only show first 3 errors
                print(f"   ⚠️  Error inserting row: {e}")
    
    pg_conn.commit()
    
    # Reset sequence for auto-increment columns
    try:
        pg_cursor.execute(f"""
            SELECT setval(pg_get_serial_sequence('{table_name}', 'id'), 
                   COALESCE((SELECT MAX(id) FROM {table_name}), 0) + 1, false)
        """)
        pg_conn.commit()
    except:
        pass  # Table might not have 'id' column
    
    return inserted


def main():
    print("=" * 60)
    print("🚀 AlbLingo Database Migration: SQLite → PostgreSQL")
    print("=" * 60)
    print()
    
    # Connect to databases
    print("📁 Connecting to local SQLite database...")
    sqlite_conn = get_sqlite_connection()
    print("   ✅ Connected to dev.db")
    
    print()
    print("🌐 Connecting to production PostgreSQL...")
    pg_conn = get_postgres_connection()
    print("   ✅ Connected to Render PostgreSQL")
    
    print()
    print("=" * 60)
    print("📊 Migrating tables...")
    print("=" * 60)
    
    total_records = 0
    
    for table in TABLES_TO_MIGRATE:
        print(f"\n📋 Migrating: {table}")
        count = migrate_table(sqlite_conn, pg_conn, table)
        if count > 0:
            print(f"   ✅ Migrated {count} records")
            total_records += count
    
    print()
    print("=" * 60)
    print(f"✅ Migration complete! Total records migrated: {total_records}")
    print("=" * 60)
    
    # Close connections
    sqlite_conn.close()
    pg_conn.close()
    
    print()
    print("🎉 Your data is now in production!")
    print("   Test your app at: https://hostim-alb-lingo.vercel.app")


if __name__ == "__main__":
    main()
