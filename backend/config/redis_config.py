"""
Configuración de Redis para sesiones y caché
"""
import redis
from redis import Redis
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()

# Configuración de Redis
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Cliente Redis singleton
_redis_client: Optional[Redis] = None

def get_redis_client() -> Redis:
    """
    Obtener cliente Redis (singleton pattern)
    """
    global _redis_client
    if _redis_client is None:
        _redis_client = redis.from_url(
            REDIS_URL,
            decode_responses=True,
            socket_connect_timeout=5,
            socket_keepalive=True,
            health_check_interval=30
        )
    return _redis_client

def close_redis_client():
    """
    Cerrar conexión Redis
    """
    global _redis_client
    if _redis_client is not None:
        _redis_client.close()
        _redis_client = None

# Configuración de sesiones
SESSION_EXPIRE_SECONDS = 28800  # 8 horas
SESSION_KEY_PREFIX = "session:"

# Configuración de caché
CACHE_EXPIRE_SECONDS = 3600  # 1 hora
CACHE_KEY_PREFIX = "cache:"

# Rate limiting
RATE_LIMIT_ATTEMPTS = 5  # intentos
RATE_LIMIT_WINDOW = 300  # 5 minutos en segundos
RATE_LIMIT_KEY_PREFIX = "ratelimit:"
