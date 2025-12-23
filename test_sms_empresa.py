"""Prueba con el nombre de la empresa (OBLIGATORIO para códigos de verificación)"""
import requests
from dotenv import load_dotenv
import os

load_dotenv()

API_KEY = os.getenv('SMS_API_KEY')
API_URL = "http://servicio.smsmasivos.com.ar/enviar_sms_bloque.asp"

print("=" * 60)
print("🧪 PRUEBA CON NOMBRE DE EMPRESA (OBLIGATORIO)")
print("=" * 60)

# Según documentación: "IMPORTANTE: Si va a enviar códigos de verificación es 
# OBLIGATORIO agregar el nombre de su empresa en los mensajes."

numero_test = "3814123693"
mensaje_test = "Los Quilmes S.A. - Codigo de verificacion: 1234"

print(f"\n📱 Número: {numero_test}")
print(f"📝 Mensaje: {mensaje_test}")
print(f"🔑 API Key: {API_KEY[:20]}...")

data = {
    "APIKEY": API_KEY,
    "TOS": numero_test,
    "MSG": mensaje_test
}

print("\n🚀 Enviando...")

try:
    response = requests.post(API_URL, data=data, timeout=10)
    
    print(f"\n✅ Status: {response.status_code}")
    print(f"📄 Respuesta: {response.text}")
    
    if response.text.strip() == "OK":
        print("\n✅ SMS ENVIADO CORRECTAMENTE")
        print("⏰ Esperá unos segundos para que llegue al celular")
        print(f"📱 Verificá el número: {numero_test}")
    else:
        print(f"\n❌ Error: {response.text}")
        
except Exception as e:
    print(f"\n❌ ERROR: {e}")

print("=" * 60)
