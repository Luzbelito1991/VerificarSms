"""Script para probar la nueva estructura"""
import sys
sys.path.insert(0, ".")

# Probar imports
try:
    print("🔍 Probando imports...")
    
    from backend.config import settings, get_db
    print("✅ backend.config")
    
    from backend.models import Usuario, Verificacion
    print("✅ backend.models")
    
    from backend.core import get_current_user
    print("✅ backend.core")
    
    from backend.services import AuthService, UserService, SMSService
    print("✅ backend.services")
    
    from backend.middleware import LoggingMiddleware
    print("✅ backend.middleware")
    
    print("\n🎉 ¡Todos los imports funcionan correctamente!")
    print(f"\n📊 Configuración:")
    print(f"   - DEBUG: {settings.DEBUG}")
    print(f"   - DATABASE: {settings.DATABASE_URL}")
    print(f"   - SMS_MODO_SIMULADO: {settings.SMS_MODO_SIMULADO}")
    print(f"   - SUCURSALES: {len(settings.SUCURSALES)} configuradas")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
