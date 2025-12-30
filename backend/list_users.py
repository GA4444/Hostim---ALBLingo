#!/usr/bin/env python3
"""
Script për të shfaqur të gjithë userat dhe adminat ekzistues në database
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app import models

def list_users():
    db = SessionLocal()
    
    try:
        # Get all users
        users = db.query(models.User).all()
        
        if not users:
            print("❌ Nuk ka usera në database!")
            return
        
        print("="*70)
        print("📋 LISTA E TË GJITHË USERAVE DHE ADMINAVE")
        print("="*70)
        print()
        
        admins = []
        regular_users = []
        
        for user in users:
            # Check if is_admin column exists
            is_admin = getattr(user, 'is_admin', False)
            
            if is_admin:
                admins.append(user)
            else:
                regular_users.append(user)
        
        if admins:
            print("🛡️  ADMIN USERS:")
            print("-"*70)
            for admin in admins:
                print(f"   ID: {admin.id}")
                print(f"   Username: {admin.username}")
                print(f"   Email: {admin.email}")
                print(f"   Age: {admin.age if admin.age else 'N/A'}")
                print(f"   Status: {'✅ Aktiv' if admin.is_active else '❌ Jo aktiv'}")
                print(f"   Created: {admin.created_at}")
                print(f"   Last Login: {admin.last_login if admin.last_login else 'Asnjëherë'}")
                print()
        else:
            print("⚠️  Nuk ka admin users në database!")
            print()
        
        if regular_users:
            print("👤 REGULAR USERS:")
            print("-"*70)
            for user in regular_users:
                print(f"   ID: {user.id}")
                print(f"   Username: {user.username}")
                print(f"   Email: {user.email}")
                print(f"   Age: {user.age if user.age else 'N/A'}")
                print(f"   Status: {'✅ Aktiv' if user.is_active else '❌ Jo aktiv'}")
                print(f"   Created: {user.created_at}")
                print(f"   Last Login: {user.last_login if user.last_login else 'Asnjëherë'}")
                print()
        else:
            print("⚠️  Nuk ka regular users në database!")
            print()
        
        print("="*70)
        print(f"📊 TOTAL: {len(users)} usera ({len(admins)} admin, {len(regular_users)} regular)")
        print("="*70)
        
        # Print login credentials summary
        print()
        print("="*70)
        print("🔑 CREDENTIALS PËR LOGIN:")
        print("="*70)
        print()
        
        if admins:
            print("🛡️  ADMIN:")
            for admin in admins:
                print(f"   Username: {admin.username}")
                print(f"   Email: {admin.email}")
                print(f"   (Password: Kontaktoni administratorin për password)")
                print()
        
        if regular_users:
            print("👤 USERS:")
            for user in regular_users:
                print(f"   Username: {user.username}")
                print(f"   Email: {user.email}")
                print(f"   (Password: Kontaktoni administratorin për password)")
                print()
        
    except Exception as e:
        print(f"❌ Gabim: {e}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    list_users()

