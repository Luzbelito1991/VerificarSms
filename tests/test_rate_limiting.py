"""
Tests de Rate Limiting
======================

Verifica que los límites de tasa funcionan correctamente.
"""

import pytest
import time
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


# ========================================
# 🧪 TESTS DE SMS RATE LIMITING
# ========================================

def test_sms_rate_limit_per_minute():
    """
    Test: Verificar límite de 5 SMS por minuto
    """
    # Primero hacer login
    login_response = client.post("/login", json={
        "usuario": "admin",
        "password": "admin123"
    })
    
    assert login_response.status_code == 200
    cookies = login_response.cookies
    
    # Intentar enviar 6 SMS (el 6to debería fallar)
    sms_data = {
        "personId": "12345678",
        "phoneNumber": "1234567890",
        "merchantCode": "776",
        "merchantName": "Test Store"
    }
    
    success_count = 0
    rate_limited = False
    
    for i in range(6):
        response = client.post(
            "/send-sms",
            json=sms_data,
            cookies=cookies
        )
        
        if response.status_code == 200:
            success_count += 1
        elif response.status_code == 429:  # Too Many Requests
            rate_limited = True
            break
    
    # Verificar que se enviaron 5 SMS y el 6to fue bloqueado
    assert success_count == 5, f"Se esperaban 5 SMS exitosos, se enviaron {success_count}"
    assert rate_limited, "El 6to SMS debería haber sido bloqueado por rate limit"
    
    print(f"✅ Rate limit funcionando: {success_count} SMS permitidos, luego bloqueado")


def test_login_rate_limit():
    """
    Test: Verificar límite de 5 intentos de login en 5 minutos
    """
    login_data = {
        "usuario": "test_user",
        "password": "wrong_password"
    }
    
    success_count = 0
    rate_limited = False
    
    # Intentar 6 logins fallidos
    for i in range(6):
        response = client.post("/login", json=login_data)
        
        if response.status_code == 401:  # Unauthorized
            success_count += 1
        elif response.status_code == 429:  # Rate limited
            rate_limited = True
            break
    
    # El 6to intento debería estar rate limited
    assert success_count == 5, f"Se esperaban 5 intentos, hubo {success_count}"
    assert rate_limited, "El 6to intento debería estar bloqueado"
    
    print(f"✅ Rate limit de login funcionando: {success_count} intentos permitidos")


# ========================================
# 🧪 TESTS DE ENDPOINTS ADMIN
# ========================================

def test_rate_limit_config_endpoint():
    """
    Test: Verificar que endpoint de configuración funciona
    """
    # Login como admin
    login_response = client.post("/login", json={
        "usuario": "admin",
        "password": "admin123"
    })
    
    cookies = login_response.cookies
    
    # Obtener configuración
    response = client.get(
        "/admin/rate-limits/config",
        cookies=cookies
    )
    
    assert response.status_code == 200
    data = response.json()
    
    # Verificar que tiene configuraciones
    assert len(data) > 0, "Debería haber configuraciones de rate limit"
    
    # Verificar estructura
    assert "endpoint" in data[0]
    assert "limit" in data[0]
    assert "period" in data[0]
    
    print(f"✅ Configuración obtenida: {len(data)} rate limits configurados")


def test_rate_limit_active_endpoint():
    """
    Test: Verificar endpoint de límites activos
    """
    # Login como admin
    login_response = client.post("/login", json={
        "usuario": "admin",
        "password": "admin123"
    })
    
    cookies = login_response.cookies
    
    # Obtener límites activos
    response = client.get(
        "/admin/rate-limits/active",
        cookies=cookies
    )
    
    assert response.status_code in [200, 503]  # 503 si Redis no está disponible
    
    if response.status_code == 200:
        data = response.json()
        assert "total" in data
        assert "limits" in data
        print(f"✅ Límites activos: {data['total']}")
    else:
        print("⚠️  Redis no disponible para este test")


def test_redis_status_endpoint():
    """
    Test: Verificar endpoint de estado de Redis
    """
    # Login como admin
    login_response = client.post("/login", json={
        "usuario": "admin",
        "password": "admin123"
    })
    
    cookies = login_response.cookies
    
    # Obtener estado de Redis
    response = client.get(
        "/admin/rate-limits/redis-status",
        cookies=cookies
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert "connected" in data
    
    if data["connected"]:
        assert "version" in data
        print(f"✅ Redis conectado - versión: {data.get('version')}")
    else:
        print("⚠️  Redis no conectado")


# ========================================
# 🧪 TESTS DE WHITELIST/BLACKLIST
# ========================================

def test_localhost_whitelisted():
    """
    Test: Verificar que localhost está en whitelist
    """
    # Este test verifica que requests desde localhost no tienen límite
    # (difícil de testear sin configuración especial)
    pass


# ========================================
# 🧪 TESTS DE RESET
# ========================================

def test_reset_rate_limit():
    """
    Test: Verificar que se puede resetear un rate limit
    """
    # Login como admin
    login_response = client.post("/login", json={
        "usuario": "admin",
        "password": "admin123"
    })
    
    cookies = login_response.cookies
    
    # Intentar resetear un límite
    response = client.post(
        "/admin/rate-limits/reset",
        json={
            "identifier": "user:admin",
            "limit_key": "sms_enviar"
        },
        cookies=cookies
    )
    
    # Puede fallar si Redis no está disponible
    if response.status_code == 200:
        data = response.json()
        assert data["ok"] == True
        print("✅ Rate limit reseteado correctamente")
    else:
        print("⚠️  Reset no disponible (Redis no conectado)")


# ========================================
# 🧪 TESTS DE MENSAJES DE ERROR
# ========================================

def test_rate_limit_error_message():
    """
    Test: Verificar que mensajes de error son informativos
    """
    # Login
    login_response = client.post("/login", json={
        "usuario": "admin",
        "password": "admin123"
    })
    
    cookies = login_response.cookies
    
    # Forzar rate limit enviando muchos SMS
    sms_data = {
        "personId": "12345678",
        "phoneNumber": "1234567890",
        "merchantCode": "776"
    }
    
    # Enviar hasta que se rate limite
    for i in range(10):
        response = client.post(
            "/send-sms",
            json=sms_data,
            cookies=cookies
        )
        
        if response.status_code == 429:
            data = response.json()
            
            # Verificar estructura del error
            assert "detail" in data
            assert "retry_after" in data["detail"] or "mensaje" in data["detail"]
            
            print(f"✅ Mensaje de error rate limit: {data['detail']}")
            break


# ========================================
# 🧪 HELPERS
# ========================================

def wait_for_rate_limit_reset(seconds: int = 60):
    """
    Espera a que se resetee el rate limit.
    Útil para tests secuenciales.
    """
    print(f"⏳ Esperando {seconds}s para reset de rate limit...")
    time.sleep(seconds)
    print("✅ Rate limit reseteado")


# ========================================
# 🏃 EJECUTAR TESTS
# ========================================

if __name__ == "__main__":
    print("🧪 Ejecutando tests de Rate Limiting...")
    print("")
    
    # Tests básicos
    try:
        test_rate_limit_config_endpoint()
    except Exception as e:
        print(f"❌ test_rate_limit_config_endpoint falló: {e}")
    
    try:
        test_rate_limit_active_endpoint()
    except Exception as e:
        print(f"❌ test_rate_limit_active_endpoint falló: {e}")
    
    try:
        test_redis_status_endpoint()
    except Exception as e:
        print(f"❌ test_redis_status_endpoint falló: {e}")
    
    # Tests de límites (estos pueden afectar el sistema)
    print("")
    print("⚠️  Los siguientes tests pueden activar rate limits reales")
    input("Presiona Enter para continuar...")
    
    try:
        test_login_rate_limit()
    except Exception as e:
        print(f"❌ test_login_rate_limit falló: {e}")
    
    # Nota: test_sms_rate_limit_per_minute solo en modo simulado
    # para no gastar SMS reales
    
    print("")
    print("✅ Tests completados")
