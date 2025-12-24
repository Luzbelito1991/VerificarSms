"""
Middleware de Rate Limiting para VerificarSms
==============================================

Implementa rate limiting usando Redis como backend.
Protege endpoints críticos de abuso y spam.
"""

from fastapi import Request, HTTPException, status
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from typing import Optional
import redis
import logging

from backend.config import settings
from backend.config.rate_limits import (
    is_ip_whitelisted,
    is_ip_blacklisted,
    format_retry_after,
    ERROR_MESSAGES,
    REDIS_KEY_PREFIX,
)

logger = logging.getLogger(__name__)


# ========================================
# 🔧 CONFIGURACIÓN DE REDIS
# ========================================

def get_redis_connection() -> Optional[redis.Redis]:
    """
    Obtiene conexión a Redis para rate limiting.
    
    Returns:
        Cliente Redis o None si no está configurado
    """
    try:
        if not settings.REDIS_URL:
            logger.warning("⚠️  Redis no configurado - rate limiting deshabilitado")
            return None
        
        redis_client = redis.from_url(
            settings.REDIS_URL,
            decode_responses=True,
            socket_connect_timeout=2,
            socket_timeout=2
        )
        
        # Verificar conexión
        redis_client.ping()
        logger.info("✅ Redis conectado para rate limiting")
        return redis_client
        
    except Exception as e:
        logger.error(f"❌ Error conectando a Redis: {e}")
        return None


# ========================================
# 🚦 FUNCIONES DE KEY
# ========================================

def get_identifier(request: Request) -> str:
    """
    Obtiene identificador único para rate limiting.
    Usa usuario si está autenticado, sino IP.
    
    Args:
        request: Request de FastAPI
    
    Returns:
        String único para identificar al cliente
    """
    # Si hay usuario autenticado, usar su ID
    if hasattr(request.state, "user") and request.state.user:
        user = request.state.user
        return f"user:{user.usuario}"
    
    # Sino, usar IP
    ip = get_remote_address(request)
    return f"ip:{ip}"


def get_real_ip(request: Request) -> str:
    """
    Obtiene la IP real del cliente considerando proxies.
    
    Args:
        request: Request de FastAPI
    
    Returns:
        IP del cliente
    """
    # Verificar headers de proxy
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        # Tomar la primera IP (cliente original)
        return forwarded.split(",")[0].strip()
    
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip
    
    # Fallback a IP de conexión directa
    return get_remote_address(request)


# ========================================
# 🚨 MIDDLEWARE DE BLACKLIST/WHITELIST
# ========================================

async def check_ip_restrictions(request: Request, call_next):
    """
    Middleware para verificar IP blacklist/whitelist.
    
    Args:
        request: Request de FastAPI
        call_next: Siguiente middleware
    
    Raises:
        HTTPException 403 si IP está bloqueada
    
    Returns:
        Response del siguiente middleware
    """
    ip = get_real_ip(request)
    
    # Verificar blacklist
    if is_ip_blacklisted(ip):
        logger.warning(f"🚫 IP bloqueada intentó acceder: {ip}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=ERROR_MESSAGES["ip_blocked"]
        )
    
    # Si está en whitelist, agregar flag
    if is_ip_whitelisted(ip):
        request.state.whitelisted = True
        logger.debug(f"✅ IP en whitelist: {ip}")
    
    return await call_next(request)


# ========================================
# 🎯 LIMITER PRINCIPAL
# ========================================

# Inicializar limiter con Redis si está disponible
redis_client = get_redis_connection()

if redis_client:
    limiter = Limiter(
        key_func=get_identifier,
        storage_uri=settings.REDIS_URL,
        strategy="fixed-window",  # Estrategia de ventana fija
        headers_enabled=True,  # Incluir headers de rate limit
    )
    logger.info("✅ Rate limiting habilitado con Redis")
else:
    # Fallback a memoria (solo para desarrollo)
    limiter = Limiter(
        key_func=get_identifier,
        strategy="fixed-window",
        headers_enabled=True,
    )
    logger.warning("⚠️  Rate limiting usando memoria (no distribuido)")


# ========================================
# 📝 HANDLER DE ERRORES
# ========================================

def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    """
    Handler personalizado para errores de rate limit.
    
    Args:
        request: Request de FastAPI
        exc: Excepción de rate limit
    
    Returns:
        HTTPException con mensaje personalizado
    """
    # Calcular tiempo de retry con manejo de error
    try:
        retry_after = int(exc.detail.split("Retry after ")[1].split(" seconds")[0])
    except (IndexError, ValueError):
        # Si no se puede parsear, usar 60 segundos por defecto
        retry_after = 60
    
    retry_formatted = format_retry_after(retry_after)
    
    # Determinar tipo de error según endpoint
    path = request.url.path
    
    if "/send-sms" in path or "/sms" in path:
        message = ERROR_MESSAGES["rate_limit_exceeded_sms"].format(
            limit=exc.detail.split(" ")[0],
            period=exc.detail.split(" per ")[1].split(" ")[0],
            retry_after=retry_formatted
        )
    elif "/login" in path:
        message = ERROR_MESSAGES["too_many_login_attempts"].format(
            retry_after=retry_formatted
        )
    else:
        message = ERROR_MESSAGES["rate_limit_exceeded"].format(
            retry_after=retry_formatted
        )
    
    # Log del evento
    identifier = get_identifier(request)
    logger.warning(
        f"🚦 Rate limit excedido - {identifier} - {path} - Retry: {retry_formatted}"
    )
    
    raise HTTPException(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        detail={
            "ok": False,
            "mensaje": message,
            "retry_after": retry_after,
            "retry_after_formatted": retry_formatted,
        },
        headers={"Retry-After": str(retry_after)}
    )


# ========================================
# 🔧 FUNCIONES DE UTILIDAD
# ========================================

def get_rate_limit_status(identifier: str, limit_key: str) -> dict:
    """
    Obtiene estado actual de rate limit para un identificador.
    
    Args:
        identifier: ID del usuario/IP
        limit_key: Clave del límite (ej: "sms_enviar")
    
    Returns:
        Dict con estado del rate limit
    """
    if not redis_client:
        return {
            "enabled": False,
            "message": "Rate limiting no disponible"
        }
    
    try:
        key = f"{REDIS_KEY_PREFIX}{limit_key}:{identifier}"
        current = redis_client.get(key)
        ttl = redis_client.ttl(key)
        
        return {
            "enabled": True,
            "identifier": identifier,
            "limit_key": limit_key,
            "current_usage": int(current) if current else 0,
            "ttl": ttl if ttl > 0 else 0,
            "reset_in": format_retry_after(ttl) if ttl > 0 else "N/A"
        }
    except Exception as e:
        logger.error(f"Error obteniendo estado de rate limit: {e}")
        return {
            "enabled": False,
            "error": str(e)
        }


def reset_rate_limit(identifier: str, limit_key: str) -> bool:
    """
    Resetea el contador de rate limit para un identificador.
    
    Args:
        identifier: ID del usuario/IP
        limit_key: Clave del límite
    
    Returns:
        True si se reseteo exitosamente
    """
    if not redis_client:
        return False
    
    try:
        key = f"{REDIS_KEY_PREFIX}{limit_key}:{identifier}"
        redis_client.delete(key)
        logger.info(f"✅ Rate limit reseteado: {key}")
        return True
    except Exception as e:
        logger.error(f"Error reseteando rate limit: {e}")
        return False


def get_all_rate_limits() -> list:
    """
    Obtiene todos los rate limits activos.
    
    Returns:
        Lista de dicts con información de rate limits activos
    """
    if not redis_client:
        return []
    
    try:
        pattern = f"{REDIS_KEY_PREFIX}*"
        keys = redis_client.keys(pattern)
        
        limits = []
        for key in keys:
            value = redis_client.get(key)
            ttl = redis_client.ttl(key)
            
            limits.append({
                "key": key.replace(REDIS_KEY_PREFIX, ""),
                "count": int(value) if value else 0,
                "ttl": ttl,
                "reset_in": format_retry_after(ttl) if ttl > 0 else "Expirado"
            })
        
        return limits
    except Exception as e:
        logger.error(f"Error obteniendo rate limits: {e}")
        return []


# ========================================
# 🎨 DECORADORES PERSONALIZADOS
# ========================================

def require_rate_limit(limit_string: str, exempt_when: callable = None):
    """
    Decorador personalizado para aplicar rate limiting.
    
    Args:
        limit_string: String de límite (ej: "5/minute")
        exempt_when: Función que determina si se debe eximir del límite
    
    Returns:
        Decorador
    """
    def decorator(func):
        async def wrapper(request: Request, *args, **kwargs):
            # Verificar si está exento
            if exempt_when and exempt_when(request):
                return await func(request, *args, **kwargs)
            
            # Verificar whitelist
            if hasattr(request.state, "whitelisted") and request.state.whitelisted:
                return await func(request, *args, **kwargs)
            
            # Aplicar rate limit usando slowapi
            return await limiter.limit(limit_string)(func)(request, *args, **kwargs)
        
        return wrapper
    return decorator
