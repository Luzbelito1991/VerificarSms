"""Prueba con parámetro FROM (remitente)"""
import requests
from dotenv import load_dotenv
import os

load_dotenv()

API_KEY = os.getenv('SMS_API_KEY')
API_URL = "http://servicio.smsmasivos.com.ar/enviar_sms_bloque.asp"

print("=" * 60)
print("🧪 PRUEBA CON PARÁMETRO FROM")
print("=" * 60)

numero_test = "3814123693"
mensaje_test = "Los Quilmes S.A. - Codigo: 9999"
remitente = "DEMO"  # o "SMS Masivos"

print(f"\n📱 Número: {numero_test}")
print(f"📝 Mensaje: {mensaje_test}")
print(f"📤 From: {remitente}")
print(f"🔑 API Key: {API_KEY[:20]}...")

# Intentar con parámetro FROM
data = {
    "APIKEY": API_KEY,
    "TOS": numero_test,
    "MSG": mensaje_test,
    "FROM": remitente
}

print("\n🚀 Enviando con FROM...")

try:
    response = requests.post(API_URL, data=data, timeout=10)
    
    print(f"\n✅ Status: {response.status_code}")
    print(f"📄 Respuesta: '{response.text}'")
    
    if "OK" in response.text:
        print("\n✅ Enviado")
        print("📱 Verificá el celular")
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")

print("\n" + "=" * 60)

# Segunda prueba con DELIVERY (confirmación de entrega)
print("🧪 PRUEBA CON DELIVERY")
print("=" * 60)

data2 = {
    "APIKEY": API_KEY,
    "TOS": numero_test,
    "MSG": mensaje_test,
    "DELIVERY": "1"  # Solicitar confirmación
}

print("\n🚀 Enviando con DELIVERY...")

try:
    response = requests.post(API_URL, data=data2, timeout=10)
    
    print(f"\n✅ Status: {response.status_code}")
    print(f"📄 Respuesta: '{response.text}'")
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")

print("=" * 60)
