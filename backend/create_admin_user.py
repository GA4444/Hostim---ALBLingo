#!/usr/bin/env python3
"""
Script për të krijuar admin user
"""
import sys
import os
import sqlite3

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app import models
from passlib.context import CryptContext
from datetime import datetime

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

def ensure_admin_column():
    """Ensure is_admin column exists"""
    try:
        conn = sqlite3.connect('dev.db')
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(users)")
        columns = [column[1] for column in cursor.fetchall()]
        if 'is_admin' not in columns:
            cursor.execute("ALTER TABLE users ADD COLUMN is_admin BOOLEAN DEFAULT 0")
            conn.commit()
        conn.close()
    except Exception as e:
        print(f"Gabim në shtimin e kolonës: {e}")

def create_admin_user():
    ensure_admin_column()
    
    db = SessionLocal()
    
    try:
        # Admin User
        admin_username = "andigjikolli"
        admin_email = "andigjikollo@gmail.com"
        admin_password = "andi123"
        
        # Check if admin already exists
        existing_admin = db.query(models.User).filter(
            models.User.username == admin_username
        ).first()
        
        if existing_admin:
            print(f"✅ Admin user '{admin_username}' tashmë ekziston!")
            existing_admin.is_admin = True
            existing_admin.password_hash = pwd_context.hash(admin_password)
            existing_admin.email = admin_email
            db.commit()
            print(f"✅ Admin user '{admin_username}' u përditësua!")
        else:
            admin_user = models.User(
                username=admin_username,
                email=admin_email,
                password_hash=pwd_context.hash(admin_password),
                is_admin=True,
                is_active=True,
                created_at=datetime.utcnow()
            )
            db.add(admin_user)
            db.commit()
            db.refresh(admin_user)
            print(f"✅ Admin user '{admin_username}' u krijua me sukses!")
        
        print()
        print("="*70)
        print("🛡️  ADMIN USER I KRIJUAR:")
        print("="*70)
        print(f"   Username: {admin_username}")
        print(f"   Email: {admin_email}")
        print(f"   Password: {admin_password}")
        print("="*70)
        
    except Exception as e:
        print(f"❌ Gabim: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    print("🚀 Duke krijuar admin user...")
    print()
    create_admin_user()

