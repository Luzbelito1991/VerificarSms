"""Prueba con enviar_sms.asp + método POST + parámetros nuevos"""
import requests
from dotenv import load_dotenv
import os

load_dotenv()

API_KEY = os.getenv('SMS_API_KEY')

print("=" * 60)
print("🧪 PROBANDO MÚLTIPLES COMBINACIONES")
print("=" * 60)

numero_test = "3814123693"
mensaje_test = "Los Quilmes - Codigo: 8888"

# PRUEBA 1: enviar_sms.asp con POST y APIKEY/TOS/MSG
print("\n1️⃣ POST a enviar_sms.asp con APIKEY/TOS/MSG")
print("-" * 60)
url1 = "http://servicio.smsmasivos.com.ar/enviar_sms.asp"
data1 = {"APIKEY": API_KEY, "TOS": numero_test, "MSG": mensaje_test}
try:
    r = requests.post(url1, data=data1, timeout=10)
    print(f"Status: {r.status_code} | Respuesta: {r.text[:100]}")
except Exception as e:
    print(f"Error: {e}")

# PRUEBA 2: enviar_sms.asp?api=1 con POST
print("\n2️⃣ POST a enviar_sms.asp?api=1")
print("-" * 60)
url2 = "http://servicio.smsmasivos.com.ar/enviar_sms.asp?api=1"
try:
    r = requests.post(url2, data=data1, timeout=10)
    print(f"Status: {r.status_code} | Respuesta: {r.text[:100]}")
except Exception as e:
    print(f"Error: {e}")

# PRUEBA 3: GET a enviar_sms.asp?api=1 con params
print("\n3️⃣ GET a enviar_sms.asp?api=1")
print("-" * 60)
url3 = "http://servicio.smsmasivos.com.ar/enviar_sms.asp?api=1"
try:
    r = requests.get(url3, params=data1, timeout=10)
    print(f"Status: {r.status_code} | Respuesta: {r.text[:100]}")
except Exception as e:
    print(f"Error: {e}")

# PRUEBA 4: enviar_sms_bloque.asp con lista de números
print("\n4️⃣ POST a enviar_sms_bloque.asp con números separados")
print("-" * 60)
url4 = "http://servicio.smsmasivos.com.ar/enviar_sms_bloque.asp"
data4 = {"APIKEY": API_KEY, "TOS": numero_test + ",", "MSG": mensaje_test}
try:
    r = requests.post(url4, data=data4, timeout=10)
    print(f"Status: {r.status_code} | Respuesta: {r.text[:100]}")
except Exception as e:
    print(f"Error: {e}")

print("\n" + "=" * 60)
print("📱 Verificá tu cuenta SMS Masivos:")
print("   - ¿Bajo el contador de SMS?")
print("   - Si bajó, ese método funcionó")
print("=" * 60)
