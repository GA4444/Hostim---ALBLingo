#!/usr/bin/env python3
"""
Script për të parë të dhënat në databazë
"""
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "dev.db"

def view_database():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    print("=" * 60)
    print("DATABASE VIEWER - Shqipto")
    print("=" * 60)
    
    # 1. Users
    print("\n📊 USERS (Përdoruesit):")
    print("-" * 60)
    users = cursor.execute("SELECT id, username, email, age, created_at FROM users").fetchall()
    if users:
        print(f"Total: {len(users)} përdorues")
        for user in users[:10]:  # Show first 10
            print(f"  • {user['username']} ({user['email']}) - Moshë: {user['age']}")
        if len(users) > 10:
            print(f"  ... dhe {len(users) - 10} të tjerë")
    else:
        print("  Nuk ka përdorues")
    
    # 2. Classes (Klasat)
    print("\n📚 CLASSES (Klasat):")
    print("-" * 60)
    classes = cursor.execute("""
        SELECT id, name, order_index 
        FROM courses 
        WHERE parent_class_id IS NULL 
        ORDER BY order_index
    """).fetchall()
    if classes:
        for cls in classes:
            # Count courses in each class
            course_count = cursor.execute("""
                SELECT COUNT(*) FROM courses 
                WHERE parent_class_id = ?
            """, (cls['id'],)).fetchone()[0]
            print(f"  • {cls['name']} (ID: {cls['id']}) - {course_count} nivele")
    else:
        print("  Nuk ka klasa")
    
    # 3. Courses per class
    print("\n📖 COURSES (Nivelet) për klasë:")
    print("-" * 60)
    for cls in classes[:4]:  # Show first 4 classes
        courses = cursor.execute("""
            SELECT id, name, order_index 
            FROM courses 
            WHERE parent_class_id = ? 
            ORDER BY order_index
        """, (cls['id'],)).fetchall()
        print(f"\n  {cls['name']}:")
        for course in courses[:5]:  # Show first 5 courses
            print(f"    - {course['name']} (Niveli {course['order_index']})")
        if len(courses) > 5:
            print(f"    ... dhe {len(courses) - 5} nivele të tjera")
    
    # 4. Exercises
    print("\n✏️  EXERCISES (Ushtrimet):")
    print("-" * 60)
    total_exercises = cursor.execute("SELECT COUNT(*) FROM exercises").fetchone()[0]
    print(f"  Total ushtrime: {total_exercises}")
    
    # Exercises per class
    for cls in classes[:4]:
        ex_count = cursor.execute("""
            SELECT COUNT(*) FROM exercises e
            JOIN courses c ON e.course_id = c.id
            WHERE c.parent_class_id = ?
        """, (cls['id'],)).fetchone()[0]
        print(f"  • {cls['name']}: {ex_count} ushtrime")
    
    # 5. Progress
    print("\n📈 PROGRESS (Progresi):")
    print("-" * 60)
    progress_count = cursor.execute("SELECT COUNT(*) FROM course_progress").fetchone()[0]
    completed_count = cursor.execute("SELECT COUNT(*) FROM course_progress WHERE is_completed = 1").fetchone()[0]
    print(f"  Total progrese: {progress_count}")
    print(f"  Nivele të përfunduara: {completed_count}")
    
    # 6. Attempts
    print("\n🎯 ATTEMPTS (Përpjekjet):")
    print("-" * 60)
    attempts_count = cursor.execute("SELECT COUNT(*) FROM attempts").fetchone()[0]
    correct_count = cursor.execute("SELECT COUNT(*) FROM attempts WHERE is_correct = 1").fetchone()[0]
    print(f"  Total përpjekje: {attempts_count}")
    print(f"  Përgjigje të sakta: {correct_count}")
    if attempts_count > 0:
        accuracy = (correct_count / attempts_count) * 100
        print(f"  Saktësi: {accuracy:.1f}%")
    
    print("\n" + "=" * 60)
    print("Për më shumë detaje, përdor DB Browser for SQLite ose SQLite CLI")
    print("=" * 60)
    
    conn.close()

if __name__ == "__main__":
    view_database()

