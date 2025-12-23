"""Prueba con formato exacto del panel web (número con barra al final)"""
import requests
from dotenv import load_dotenv
import os

load_dotenv()

API_KEY = os.getenv('SMS_API_KEY')
API_URL = "http://servicio.smsmasivos.com.ar/enviar_sms_bloque.asp"

print("=" * 60)
print("🧪 PRUEBA CON FORMATO DE PANEL WEB")
print("=" * 60)

# Formato exacto del panel: número con / al final
numero_test = "3814123693/"  # Con barra como en el panel
mensaje_test = "Los Quilmes S.A. - Codigo: 5678"

print(f"\n📱 Número: {numero_test}")
print(f"📝 Mensaje: {mensaje_test}")
print(f"🔑 API Key: {API_KEY[:20]}...")

data = {
    "APIKEY": API_KEY,
    "TOS": numero_test,
    "MSG": mensaje_test
}

print("\n🚀 Enviando con formato del panel web...")

try:
    response = requests.post(API_URL, data=data, timeout=10)
    
    print(f"\n✅ Status: {response.status_code}")
    print(f"📄 Respuesta: '{response.text}'")
    
    if "OK" in response.text:
        print("\n✅ API acepta el envío")
        print("📱 Revisá el celular en unos segundos")
    else:
        print(f"\n⚠️ Respuesta: {response.text}")
        
except Exception as e:
    print(f"\n❌ ERROR: {e}")

print("=" * 60)
