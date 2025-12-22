"""
🧪 Script para probar el modo simulado de SMS
"""
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("SMS_API_KEY")
MODO_SIMULADO = os.getenv("SMS_MODO_SIMULADO", "false").strip("'\"").lower() == "true"

print("=" * 60)
print("🧪 PRUEBA DE CONFIGURACIÓN SMS")
print("=" * 60)
print(f"\n📌 API_KEY configurada: {'✅ Sí' if API_KEY else '❌ No'}")
print(f"📌 MODO_SIMULADO: {MODO_SIMULADO}")
print(f"   └─ Tipo: {type(MODO_SIMULADO)}")

print(f"\n🔍 Valor crudo del .env: '{os.getenv('SMS_MODO_SIMULADO', 'false')}'")

print("\n" + "=" * 60)
if MODO_SIMULADO:
    print("⚠️  MODO SIMULADO ACTIVO")
    print("   └─ Los SMS se imprimirán en consola, NO se enviarán realmente")
else:
    print("✅ MODO REAL ACTIVO")
    print("   └─ Los SMS se enviarán a través de la API de SMS Masivos")
print("=" * 60)

print("\n💡 Para cambiar el modo, edita el archivo .env:")
print("   - SMS_MODO_SIMULADO=true  → Modo simulado (para pruebas)")
print("   - SMS_MODO_SIMULADO=false → Modo real (envío verdadero)")
