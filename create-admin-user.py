"""
Script to create an admin user in the auth service database.
Run this script to create an admin user for testing the admin UI.
"""
import sys
import os

# Add auth-service to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'auth-service'))

from app.database import SessionLocal, engine, Base
from app.models.user import User, UserRole
from app.utils.security import get_password_hash
from uuid import uuid4

def create_admin_user(email: str = "admin@example.com", password: str = "admin123", name: str = "Admin User", reset_password: bool = True):
    """Create an admin user in the database."""
    # Create tables if they don't exist
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # Check if admin user already exists
        existing_user = db.query(User).filter(User.email == email).first()
        if existing_user:
            print(f"⚠️  User with email {email} already exists!")
            
            # Update role to admin if needed
            if existing_user.role != UserRole.ADMIN.value:
                print(f"   Updating role to admin...")
                existing_user.role = UserRole.ADMIN.value
            
            # Reset password if requested
            if reset_password:
                print(f"   Resetting password...")
                existing_user.password_hash = get_password_hash(password)
                existing_user.is_active = True
                existing_user.is_verified = True
                db.commit()
                print(f"✅ Admin user updated successfully!")
                print(f"\n📧 Login Credentials:")
                print(f"   Email: {email}")
                print(f"   Password: {password}")
                print(f"\n🌐 Access the admin UI at:")
                print(f"   http://localhost:3000/admin")
                print(f"   (If port 3000 is in use, check terminal for actual port)")
            else:
                print(f"✅ User is already an admin.")
                print(f"   Email: {email}")
                print(f"   Password: (unchanged - use your existing password)")
                print(f"\n💡 To reset the password, run:")
                print(f"   python create-admin-user.py --email {email} --password <new_password>")
            return
        
        # Create new admin user
        admin_user = User(
            id=uuid4(),
            email=email,
            name=name,
            password_hash=get_password_hash(password),
            role=UserRole.ADMIN.value,
            is_active=True,
            is_verified=True,
        )
        
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        
        print("✅ Admin user created successfully!")
        print(f"\n📧 Login Credentials:")
        print(f"   Email: {email}")
        print(f"   Password: {password}")
        print(f"\n🌐 Access the admin UI at:")
        print(f"   http://localhost:3000/admin")
        print(f"   (If port 3000 is in use, check terminal for actual port)")
        print(f"\n⚠️  Remember to change the password after first login!")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error creating admin user: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Create an admin user for the platform')
    parser.add_argument('--email', default='admin@example.com', help='Admin email (default: admin@example.com)')
    parser.add_argument('--password', default='admin123', help='Admin password (default: admin123)')
    parser.add_argument('--name', default='Admin User', help='Admin name (default: Admin User)')
    parser.add_argument('--no-reset', action='store_true', help='Do not reset password for existing users')
    
    args = parser.parse_args()
    
    create_admin_user(args.email, args.password, args.name, reset_password=not args.no_reset)


