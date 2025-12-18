"""
Script to check users in the auth service database and test login.
This helps diagnose 401 Unauthorized errors.
"""
import sys
import os

# Add auth-service to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'auth-service'))

from app.database import SessionLocal, engine, Base
from app.models.user import User
from app.services.auth_service import AuthService
from app.utils.security import verify_password

def list_all_users():
    """List all users in the database."""
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        users = db.query(User).all()
        
        if not users:
            print("❌ No users found in the database!")
            print("\n💡 To create a user, you can:")
            print("   1. Register via the UI at http://localhost:3000/register")
            print("   2. Create an admin user: python create-admin-user.py")
            return
        
        print(f"✅ Found {len(users)} user(s) in the database:\n")
        
        for user in users:
            print(f"📧 Email: {user.email}")
            print(f"   Name: {user.name}")
            print(f"   Role: {user.role}")
            print(f"   Active: {user.is_active}")
            print(f"   Verified: {user.is_verified}")
            print(f"   Created: {user.created_at}")
            print(f"   Last Login: {user.last_login_at or 'Never'}")
            print()
        
    except Exception as e:
        print(f"❌ Error reading users: {e}")
        raise
    finally:
        db.close()

def test_login(email: str, password: str):
    """Test login with given credentials."""
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        print(f"\n🔍 Testing login for: {email}")
        
        # Check if user exists
        user = AuthService.get_user_by_email(db, email)
        if not user:
            print(f"❌ User with email '{email}' not found in database!")
            print("\n💡 Available users:")
            list_all_users()
            return False
        
        print(f"✅ User found: {user.name} (Role: {user.role})")
        print(f"   Active: {user.is_active}")
        print(f"   Verified: {user.is_verified}")
        
        if not user.is_active:
            print("❌ User account is INACTIVE - this will cause 401 error!")
            print("   The user exists but is_active=False")
            return False
        
        # Test password
        print(f"\n🔐 Testing password...")
        if verify_password(password, user.password_hash):
            print("✅ Password is CORRECT!")
            print("✅ Login should work!")
            return True
        else:
            print("❌ Password is INCORRECT!")
            print("   This will cause 401 Unauthorized error")
            return False
        
    except Exception as e:
        print(f"❌ Error testing login: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Check users in auth database and test login')
    parser.add_argument('--list', action='store_true', help='List all users in database')
    parser.add_argument('--test', nargs=2, metavar=('EMAIL', 'PASSWORD'), help='Test login with email and password')
    
    args = parser.parse_args()
    
    if args.test:
        email, password = args.test
        test_login(email, password)
    else:
        list_all_users()
        print("\n💡 To test login, use:")
        print("   python check-auth-users.py --test email@example.com password123")
