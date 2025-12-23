"""Script para probar el envío REAL de SMS a SMS Masivos"""
import requests
from dotenv import load_dotenv
import os

load_dotenv()

API_KEY = os.getenv('SMS_API_KEY')
API_URL = "http://servicio.smsmasivos.com.ar/enviar_sms_bloque.asp"

print("=" * 60)
print("🧪 PRUEBA DE ENVÍO REAL A SMS MASIVOS")
print("=" * 60)

print(f"\n📍 URL API: {API_URL}")
print(f"🔑 API Key: {API_KEY[:20]}... (primeros 20 caracteres)")

# Datos de prueba
numero_test = "3814123693"  # Tu número
mensaje_test = "Prueba desde VerificarSMS - Codigo: 1234"

print(f"\n📱 Número destino: {numero_test}")
print(f"📝 Mensaje: {mensaje_test}")

# Construir la petición según documentación oficial (POST a enviar_sms_bloque.asp)
data = {
    "APIKEY": API_KEY,
    "TOS": numero_test,  # 10 dígitos sin 0 ni 15
    "MSG": mensaje_test
}

print("\n" + "=" * 60)
print("🚀 ENVIANDO PETICIÓN POST (enviar_sms_bloque.asp)...")
print("=" * 60)

try:
    response = requests.post(API_URL, data=data, timeout=10)
    
    print(f"\n✅ Status Code: {response.status_code}")
    print(f"📄 Respuesta del servidor:")
    print("-" * 60)
    print(response.text)
    print("-" * 60)
    
    if response.status_code == 200:
        print("\n✅ La petición fue exitosa (HTTP 200)")
        print("   Revisá la respuesta del servidor para confirmar el envío")
    else:
        print(f"\n❌ Error HTTP {response.status_code}")
        
except requests.RequestException as e:
    print(f"\n❌ Error al conectar con la API:")
    print(f"   {str(e)}")
    
print("\n" + "=" * 60)
print("💡 NOTAS:")
print("   - Si ves 'OK' o código de éxito en la respuesta, el SMS se envió")
print("   - Si ves 'ERROR' o 'INVALID', verificá la API Key o el número")
print("   - Si no llega al celular, verificá el saldo en SMS Masivos")
print("=" * 60)
