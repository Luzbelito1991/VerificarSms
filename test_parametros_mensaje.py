"""Probando diferentes nombres de parámetros para el mensaje"""
import requests
from dotenv import load_dotenv
import os

load_dotenv()

API_KEY = os.getenv('SMS_API_KEY')
URL = "http://servicio.smsmasivos.com.ar/enviar_sms.asp?api=1"

numero_test = "3814123693"
mensaje_test = "Los Quilmes - Codigo: 1111"

print("=" * 60)
print("🧪 PROBANDO NOMBRES DE PARÁMETROS")
print("=" * 60)

# Probar diferentes nombres para el parámetro del mensaje
parametros_mensaje = ["MSG", "MESSAGE", "MENSAJE", "TEXT", "TEXTO", "SMS", "BODY"]

for param_name in parametros_mensaje:
    print(f"\n📝 Probando parámetro: {param_name}")
    data = {
        "APIKEY": API_KEY,
        "TOS": numero_test,
        param_name: mensaje_test
    }
    
    try:
        response = requests.post(URL, data=data, timeout=10)
        respuesta = response.text.strip()
        
        if "no se indicó texto" not in respuesta and len(respuesta) < 50:
            print(f"   ✅ {response.status_code}: {respuesta}")
            if respuesta == "OK" or "OK" in respuesta:
                print(f"   🎉 ¡POSIBLE ÉXITO! Verificá el celular y el saldo")
        else:
            print(f"   ❌ {response.status_code}: {respuesta[:80]}")
    except Exception as e:
        print(f"   ❌ Error: {e}")

print("\n" + "=" * 60)
print("📱 Revisá tu cuenta SMS Masivos")
print("   Si bajó el contador, ese parámetro funciona")
print("=" * 60)
