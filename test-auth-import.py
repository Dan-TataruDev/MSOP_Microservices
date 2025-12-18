"""
Quick test script to verify auth router can be imported.
Run this from the guest-interaction-service directory.
"""
import sys
import os

# Add the service directory to path
service_dir = os.path.join(os.path.dirname(__file__), 'guest-interaction-service')
sys.path.insert(0, service_dir)

try:
    from app.api.v1 import auth
    print(f"✓ Auth router imported successfully")
    print(f"✓ Router prefix: {auth.router.prefix}")
    print(f"✓ Number of routes: {len(auth.router.routes)}")
    print(f"✓ Routes:")
    for route in auth.router.routes:
        if hasattr(route, 'path') and hasattr(route, 'methods'):
            methods = ', '.join(route.methods) if route.methods else 'N/A'
            print(f"  - {methods} {route.path}")
except Exception as e:
    print(f"✗ Error importing auth router: {e}")
    import traceback
    traceback.print_exc()

