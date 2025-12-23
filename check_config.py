"""Script simple para verificar el estado de SMS_MODO_SIMULADO"""
from backend.config.settings import settings

print("=" * 60)
print("🔍 ESTADO ACTUAL DE LA CONFIGURACIÓN")
print("=" * 60)
print(f"\nSMS_MODO_SIMULADO: {settings.SMS_MODO_SIMULADO}")
print(f"Tipo: {type(settings.SMS_MODO_SIMULADO)}")
print(f"SMS_API_KEY existe: {settings.SMS_API_KEY is not None}")
print(f"SMS_API_URL: {settings.SMS_API_URL}")

if settings.SMS_MODO_SIMULADO:
    print("\n🟡 MODO ACTUAL: SIMULADO (TEST)")
    print("   Los SMS NO se enviarán realmente")
else:
    print("\n🟢 MODO ACTUAL: PRODUCCIÓN (REAL)")
    print("   Los SMS SÍ se enviarán realmente")

print("=" * 60)
