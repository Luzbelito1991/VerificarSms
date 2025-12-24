"""
Configuración de Rate Limiting para VerificarSms
================================================

Define límites de tasa para diferentes endpoints y usuarios.
Usa Redis como backend para tracking distribuido.
"""

from typing import Dict, Any
from pydantic import BaseModel


class RateLimitConfig(BaseModel):
    """Configuración de un límite de tasa"""
    limit: int  # Número de requests permitidos
    period: int  # Período en segundos
    description: str


# ========================================
# 🚦 LÍMITES POR ENDPOINT
# ========================================

# Formato: "número/período"
# Ejemplos: "5/minute", "100/hour", "1000/day"

RATE_LIMITS: Dict[str, RateLimitConfig] = {
    # 📱 SMS - El más crítico (prevenir spam y costos)
    "sms_enviar": RateLimitConfig(
        limit=5,
        period=60,  # 5 SMS por minuto por IP/usuario
        description="Envío de SMS de verificación"
    ),
    
    "sms_enviar_por_hora": RateLimitConfig(
        limit=30,
        period=3600,  # 30 SMS por hora
        description="Límite por hora para SMS"
    ),
    
    "sms_enviar_por_dia": RateLimitConfig(
        limit=200,
        period=86400,  # 200 SMS por día
        description="Límite diario para SMS"
    ),
    
    # 🔐 Autenticación - Prevenir brute force
    "login_intentos": RateLimitConfig(
        limit=5,
        period=300,  # 5 intentos por 5 minutos
        description="Intentos de login"
    ),
    
    "password_reset": RateLimitConfig(
        limit=3,
        period=3600,  # 3 resets por hora
        description="Recuperación de contraseña"
    ),
    
    # 📊 API General
    "api_general": RateLimitConfig(
        limit=100,
        period=60,  # 100 requests por minuto
        description="API general"
    ),
    
    # 🔍 Consultas y reportes
    "consultas": RateLimitConfig(
        limit=30,
        period=60,  # 30 consultas por minuto
        description="Consultas de datos"
    ),
}


# ========================================
# 👥 LÍMITES POR ROL
# ========================================

ROLE_MULTIPLIERS: Dict[str, float] = {
    "admin": 3.0,      # Admins pueden hacer 3x más requests
    "operador": 1.0,   # Operadores tienen límite estándar
    "guest": 0.3,      # Invitados tienen límite reducido
}


# ========================================
# 🎯 WHITELIST Y BLACKLIST
# ========================================

# IPs que no tienen límite de tasa
WHITELIST_IPS = [
    "127.0.0.1",
    "localhost",
    # Agregar IPs de confianza aquí
]

# IPs bloqueadas completamente
BLACKLIST_IPS = [
    # Agregar IPs maliciosas aquí
]


# ========================================
# ⚙️ CONFIGURACIÓN DE REDIS
# ========================================

REDIS_KEY_PREFIX = "ratelimit:"
REDIS_KEY_EXPIRE = 86400  # 24 horas - limpieza automática


# ========================================
# 📝 MENSAJES DE ERROR
# ========================================

ERROR_MESSAGES = {
    "rate_limit_exceeded": "Límite de solicitudes excedido. Por favor espera {retry_after} segundos antes de intentar nuevamente.",
    "rate_limit_exceeded_sms": "Has alcanzado el límite de SMS permitidos. Límite: {limit} por {period}s. Intenta nuevamente en {retry_after}s.",
    "ip_blocked": "Tu IP ha sido bloqueada debido a actividad sospechosa.",
    "too_many_login_attempts": "Demasiados intentos de login. Intenta nuevamente en {retry_after} minutos.",
}


# ========================================
# 🔧 FUNCIONES DE UTILIDAD
# ========================================

def get_limit_for_endpoint(endpoint: str, role: str = "operador") -> RateLimitConfig:
    """
    Obtiene el límite configurado para un endpoint y rol.
    
    Args:
        endpoint: Nombre del endpoint (ej: "sms_enviar")
        role: Rol del usuario (ej: "admin", "operador")
    
    Returns:
        RateLimitConfig con límite ajustado según rol
    """
    config = RATE_LIMITS.get(endpoint)
    
    if not config:
        # Límite por defecto si no está configurado
        config = RATE_LIMITS["api_general"]
    
    # Aplicar multiplicador por rol
    multiplier = ROLE_MULTIPLIERS.get(role.lower(), 1.0)
    
    return RateLimitConfig(
        limit=int(config.limit * multiplier),
        period=config.period,
        description=config.description
    )


def get_rate_limit_string(endpoint: str) -> str:
    """
    Convierte configuración a formato de slowapi.
    
    Args:
        endpoint: Nombre del endpoint
    
    Returns:
        String en formato "limit/period" (ej: "5/minute")
    """
    config = RATE_LIMITS.get(endpoint, RATE_LIMITS["api_general"])
    
    # Convertir segundos a unidad legible
    if config.period == 60:
        period = "minute"
    elif config.period == 3600:
        period = "hour"
    elif config.period == 86400:
        period = "day"
    else:
        # Para períodos personalizados, usar segundos
        return f"{config.limit}/{config.period} seconds"
    
    return f"{config.limit}/{period}"


def is_ip_whitelisted(ip: str) -> bool:
    """Verifica si una IP está en whitelist"""
    return ip in WHITELIST_IPS


def is_ip_blacklisted(ip: str) -> bool:
    """Verifica si una IP está en blacklist"""
    return ip in BLACKLIST_IPS


def format_retry_after(seconds: int) -> str:
    """
    Formatea segundos en mensaje legible.
    
    Args:
        seconds: Segundos hasta poder reintentar
    
    Returns:
        String legible (ej: "2 minutos", "30 segundos")
    """
    if seconds >= 3600:
        hours = seconds // 3600
        return f"{hours} hora{'s' if hours != 1 else ''}"
    elif seconds >= 60:
        minutes = seconds // 60
        return f"{minutes} minuto{'s' if minutes != 1 else ''}"
    else:
        return f"{seconds} segundo{'s' if seconds != 1 else ''}"
