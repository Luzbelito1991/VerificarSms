"""Script para verificar el estado del modo simulado de SMS"""
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

print("=" * 60)
print("🔍 VERIFICACIÓN DEL MODO SMS")
print("=" * 60)

# Leer directamente del .env
with open('.env', 'r') as f:
    for line in f:
        if 'SMS_MODO_SIMULADO' in line:
            print(f"\n📄 Línea en .env: {line.strip()}")

# Leer desde os.getenv
raw_value = os.getenv('SMS_MODO_SIMULADO', 'not_found')
print(f"\n🔧 Valor crudo de os.getenv: '{raw_value}' (tipo: {type(raw_value).__name__})")

# Importar settings de Pydantic
from backend.config.settings import settings

print(f"\n⚙️  Valor en settings.SMS_MODO_SIMULADO: {settings.SMS_MODO_SIMULADO} (tipo: {type(settings.SMS_MODO_SIMULADO).__name__})")

# Determinar el comportamiento esperado
if settings.SMS_MODO_SIMULADO:
    print("\n🟡 MODO ACTUAL: SIMULADO (TEST)")
    print("   → Los SMS NO se enviarán de forma real")
    print("   → Estado en DB: 'test'")
    print("   → Badge amarillo en admin")
else:
    print("\n🟢 MODO ACTUAL: PRODUCCIÓN (REAL)")
    print("   → Los SMS SÍ se enviarán de forma real")
    print("   → Estado en DB: 'enviado' o 'fallido'")
    print("   → Badge verde/rojo en admin")
    print("   → ⚠️ CONSUMIRÁ SMS REALES de SMS Masivos")

print("\n" + "=" * 60)
