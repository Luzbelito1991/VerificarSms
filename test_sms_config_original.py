"""Prueba con configuración ORIGINAL que funcionaba"""
import requests
from dotenv import load_dotenv
import os

load_dotenv()

API_KEY = os.getenv('SMS_API_KEY')
API_URL = "http://servicio.smsmasivos.com.ar/enviar_sms.asp"

print("=" * 60)
print("🧪 PRUEBA CON CONFIGURACIÓN ORIGINAL")
print("=" * 60)

numero_test = "3814123693"
mensaje_test = "Los Quilmes S.A. - Codigo de verificacion: 7777"

print(f"\n📱 Número: {numero_test}")
print(f"📝 Mensaje: {mensaje_test}")
print(f"🔑 API Key: {API_KEY[:20]}...")

# CONFIGURACIÓN ORIGINAL: GET con api_key, numero, mensaje
params = {
    "api_key": API_KEY,
    "numero": numero_test,
    "mensaje": mensaje_test
}

print("\n🚀 Enviando con GET (configuración original)...")

try:
    response = requests.get(API_URL, params=params, timeout=10)
    
    print(f"\n✅ Status: {response.status_code}")
    print(f"📄 Respuesta: '{response.text}'")
    
    if response.status_code == 200:
        print("\n✅ ENVIADO EXITOSAMENTE")
        print("📱 REVISÁ TU CELULAR AHORA")
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")

print("=" * 60)
