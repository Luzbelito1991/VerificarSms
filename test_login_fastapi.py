"""
Simular el flujo de login completo con FastAPI
"""
import asyncio
from fastapi import Request
from fastapi.testclient import TestClient
from backend.main import app

# Crear cliente de test
client = TestClient(app)

# Probar login
response = client.post(
    "/login",
    json={"usuario": "admin", "password": "admin123"},
    headers={"Content-Type": "application/json"}
)

print(f"Status Code: {response.status_code}")
print(f"Response: {response.text}")

if response.status_code == 200:
    data = response.json()
    print(f"✅ LOGIN EXITOSO")
    print(f"  Usuario: {data.get('usuario')}")
    print(f"  Rol: {data.get('rol')}")
else:
    print(f"❌ LOGIN FALLÓ")
    try:
        error = response.json()
        print(f"  Error: {error}")
    except:
        print(f"  Respuesta no JSON: {response.text}")
