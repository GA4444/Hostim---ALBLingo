#!/usr/bin/env python3
"""
Script për të krijuar admin user dhe usera test në database
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app import models
from passlib.context import CryptContext
from datetime import datetime

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_users():
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
            print(f"   ID: {admin_user.id}")
            print(f"   Email: {admin_email}")
            print(f"   Password: {admin_password}")
        
        # Test Users
        test_users = [
            {
                "username": "testuser1",
                "email": "testuser1@example.com",
                "password": "test123",
                "age": 10
            },
            {
                "username": "testuser2",
                "email": "testuser2@example.com",
                "password": "test123",
                "age": 12
            },
            {
                "username": "student1",
                "email": "student1@example.com",
                "password": "student123",
                "age": 8
            }
        ]
        
        for user_data in test_users:
            existing = db.query(models.User).filter(
                models.User.username == user_data["username"]
            ).first()
            
            if existing:
                print(f"⚠️  User '{user_data['username']}' tashmë ekziston!")
            else:
                user = models.User(
                    username=user_data["username"],
                    email=user_data["email"],
                    password_hash=pwd_context.hash(user_data["password"]),
                    age=user_data["age"],
                    is_admin=False,
                    is_active=True,
                    created_at=datetime.utcnow()
                )
                db.add(user)
                db.commit()
                db.refresh(user)
                print(f"✅ User '{user_data['username']}' u krijua me sukses!")
                print(f"   ID: {user.id}")
                print(f"   Email: {user_data['email']}")
                print(f"   Password: {user_data['password']}")
        
        print("\n" + "="*50)
        print("📋 PËRMBLEDHJE E USERAVE:")
        print("="*50)
        print("\n🛡️  ADMIN USER:")
        print(f"   Username: {admin_username}")
        print(f"   Email: {admin_email}")
        print(f"   Password: {admin_password}")
        print("\n👤 TEST USERS:")
        for user_data in test_users:
            print(f"   Username: {user_data['username']}")
            print(f"   Email: {user_data['email']}")
            print(f"   Password: {user_data['password']}")
            print()
        
        print("="*50)
        print("✅ Të gjithë userat janë gati për login!")
        print("="*50)
        
    except Exception as e:
        print(f"❌ Gabim: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    print("🚀 Duke krijuar userat...")
    print()
    create_users()

