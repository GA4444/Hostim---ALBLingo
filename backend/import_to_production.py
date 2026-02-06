#!/usr/bin/env python3
"""
Import JSON data to PostgreSQL production database.
Run this after export_local_data.py
"""
import json
import os
import psycopg2
from psycopg2.extras import execute_values

# Production PostgreSQL URL
PRODUCTION_DATABASE_URL = "postgresql://alblingo_yzes_user:9aJ8fnKKlIGAaIbeWhnln9uqydrXutMu@dpg-d5ubcja4d50c73d1amt0-a.frankfurt-postgres.render.com/alblingo_yzes"

EXPORT_DIR = "migration_export"

# Tables in order of dependencies
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
]

def load_json(table_name):
    """Load JSON data for a table"""
    filepath = os.path.join(EXPORT_DIR, f"{table_name}.json")
    if not os.path.exists(filepath):
        return []
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def import_table(conn, table_name, data):
    """Import data into a PostgreSQL table"""
    if not data:
        print(f"   ⏭️  No data for {table_name}, skipping")
        return 0
    
    cursor = conn.cursor()
    
    # Get columns from first record
    columns = list(data[0].keys())
    
    # Clear existing data
    try:
        cursor.execute(f"TRUNCATE TABLE {table_name} CASCADE")
        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"   ⚠️  Could not truncate: {e}")
    
    # Prepare INSERT statement
    columns_str = ", ".join(columns)
    placeholders = ", ".join(["%s"] * len(columns))
    insert_sql = f"INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders})"
    
    # Insert records one by one (more reliable)
    inserted = 0
    errors = 0
    
    for record in data:
        values = [record.get(col) for col in columns]
        try:
            cursor.execute(insert_sql, values)
            inserted += 1
        except Exception as e:
            conn.rollback()
            errors += 1
            if errors <= 2:
                print(f"   ⚠️  Error: {e}")
    
    conn.commit()
    
    # Reset sequence
    try:
        cursor.execute(f"""
            SELECT setval(pg_get_serial_sequence('{table_name}', 'id'), 
                   COALESCE((SELECT MAX(id) FROM {table_name}), 1))
        """)
        conn.commit()
    except:
        pass
    
    if errors > 0:
        print(f"   ⚠️  {errors} errors occurred")
    
    return inserted

def main():
    print("=" * 60)
    print("🚀 Importing Data to Production PostgreSQL")
    print("=" * 60)
    print()
    
    # Connect to PostgreSQL
    print("🌐 Connecting to production database...")
    try:
        conn = psycopg2.connect(PRODUCTION_DATABASE_URL, connect_timeout=10)
        print("   ✅ Connected!")
    except Exception as e:
        print(f"   ❌ Connection failed: {e}")
        return
    
    print()
    total = 0
    
    for table in TABLES:
        print(f"📋 Importing: {table}")
        data = load_json(table)
        count = import_table(conn, table, data)
        if count > 0:
            print(f"   ✅ Imported {count} records")
            total += count
    
    conn.close()
    
    print()
    print("=" * 60)
    print(f"✅ Import complete! Total: {total} records")
    print("=" * 60)
    print()
    print("🎉 Your data is now in production!")
    print("   Test at: https://hostim-alb-lingo.vercel.app")

if __name__ == "__main__":
    main()
