"""Test manual de login"""
print('Testing login flow...')

from backend.config import get_db
from backend.services import AuthService
from backend.services.session_service import session_store

# 1. Test DB connection
db = next(get_db())
print('✅ DB connection OK')

# 2. Test authentication
user = AuthService.authenticate_user(db, 'admin', 'admin123')
if user:
    print(f'✅ User authenticated: {user.usuario} ({user.rol})')
else:
    print('❌ Authentication failed')
    exit(1)

# 3. Test session creation
session_id = session_store.create_session({
    "usuario": user.usuario,
    "rol": user.rol,
    "id": user.id,
    "email": user.email
})
print(f'✅ Session created: {session_id}')

# 4. Test session retrieval
session_data = session_store.get_session(session_id)
print(f'✅ Session retrieved: {session_data}')

# Cleanup
session_store.delete_session(session_id)
print('✅ Session deleted')
print('\n🎉 All tests passed!')
