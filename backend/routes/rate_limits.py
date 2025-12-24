"""
Router para gestión de Rate Limiting
======================================

Endpoints administrativos para monitorear y gestionar rate limits.
Solo accesible para usuarios con rol admin.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from pydantic import BaseModel
from typing import List, Optional

from backend.core import get_current_user
from backend.models import Usuario
from backend.middleware.rate_limiting import (
    get_rate_limit_status,
    reset_rate_limit,
    get_all_rate_limits,
    redis_client,
)
from backend.config.rate_limits import RATE_LIMITS, ROLE_MULTIPLIERS

router = APIRouter(prefix="/admin/rate-limits", tags=["Admin - Rate Limiting"])


# ========================================
# 📊 MODELOS
# ========================================

class RateLimitInfo(BaseModel):
    """Información de un rate limit"""
    endpoint: str
    limit: int
    period: int
    description: str


class RateLimitStatus(BaseModel):
    """Estado actual de un rate limit"""
    identifier: str
    limit_key: str
    current_usage: int
    ttl: int
    reset_in: str


class ResetRequest(BaseModel):
    """Request para resetear rate limit"""
    identifier: str
    limit_key: str


# ========================================
# 🔐 VERIFICACIÓN DE ADMIN
# ========================================

def require_admin(user: Usuario = Depends(get_current_user)):
    """Verifica que el usuario sea admin"""
    if user.rol.lower() != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso denegado. Solo administradores."
        )
    return user


# ========================================
# 📋 ENDPOINTS
# ========================================

@router.get("/config", response_model=List[RateLimitInfo])
def get_rate_limits_config(admin: Usuario = Depends(require_admin)):
    """
    Obtiene la configuración de todos los rate limits.
    
    Returns:
        Lista de rate limits configurados
    """
    return [
        RateLimitInfo(
            endpoint=key,
            limit=config.limit,
            period=config.period,
            description=config.description
        )
        for key, config in RATE_LIMITS.items()
    ]


@router.get("/active")
def get_active_limits(admin: Usuario = Depends(require_admin)):
    """
    Obtiene todos los rate limits activos en Redis.
    
    Returns:
        Lista de rate limits activos con sus contadores
    """
    if not redis_client:
        raise HTTPException(
            status_code=503,
            detail="Redis no disponible. Rate limiting deshabilitado."
        )
    
    limits = get_all_rate_limits()
    
    return {
        "ok": True,
        "total": len(limits),
        "limits": limits
    }


@router.get("/status/{identifier}/{limit_key}")
def get_limit_status(
    identifier: str,
    limit_key: str,
    admin: Usuario = Depends(require_admin)
):
    """
    Obtiene el estado de un rate limit específico.
    
    Args:
        identifier: ID del usuario o IP (ej: "user:admin", "ip:192.168.1.1")
        limit_key: Clave del límite (ej: "sms_enviar")
    
    Returns:
        Estado actual del rate limit
    """
    if not redis_client:
        raise HTTPException(
            status_code=503,
            detail="Redis no disponible"
        )
    
    status = get_rate_limit_status(identifier, limit_key)
    
    return {
        "ok": True,
        "status": status
    }


@router.post("/reset")
def reset_limit(
    reset_req: ResetRequest,
    admin: Usuario = Depends(require_admin)
):
    """
    Resetea el contador de un rate limit específico.
    
    Args:
        reset_req: Datos del rate limit a resetear
    
    Returns:
        Confirmación del reseteo
    """
    if not redis_client:
        raise HTTPException(
            status_code=503,
            detail="Redis no disponible"
        )
    
    success = reset_rate_limit(reset_req.identifier, reset_req.limit_key)
    
    if success:
        return {
            "ok": True,
            "mensaje": f"Rate limit reseteado: {reset_req.identifier} - {reset_req.limit_key}"
        }
    else:
        raise HTTPException(
            status_code=500,
            detail="Error al resetear rate limit"
        )


@router.delete("/clear-all")
def clear_all_limits(admin: Usuario = Depends(require_admin)):
    """
    Elimina todos los rate limits activos (CUIDADO).
    Útil para testing o emergencias.
    
    Returns:
        Número de límites eliminados
    """
    if not redis_client:
        raise HTTPException(
            status_code=503,
            detail="Redis no disponible"
        )
    
    try:
        from backend.config.rate_limits import REDIS_KEY_PREFIX
        
        pattern = f"{REDIS_KEY_PREFIX}*"
        keys = redis_client.keys(pattern)
        
        if keys:
            deleted = redis_client.delete(*keys)
        else:
            deleted = 0
        
        return {
            "ok": True,
            "mensaje": f"Rate limits eliminados: {deleted}",
            "deleted_count": deleted
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al limpiar rate limits: {str(e)}"
        )


@router.get("/roles")
def get_role_multipliers(admin: Usuario = Depends(require_admin)):
    """
    Obtiene los multiplicadores de rate limit por rol.
    
    Returns:
        Multiplicadores configurados
    """
    return {
        "ok": True,
        "multipliers": ROLE_MULTIPLIERS,
        "description": "Multiplicadores aplicados a los límites base según rol del usuario"
    }


@router.get("/redis-status")
def get_redis_status(admin: Usuario = Depends(require_admin)):
    """
    Verifica el estado de conexión con Redis.
    
    Returns:
        Estado de Redis
    """
    if not redis_client:
        return {
            "ok": False,
            "connected": False,
            "message": "Redis no configurado"
        }
    
    try:
        redis_client.ping()
        info = redis_client.info()
        
        return {
            "ok": True,
            "connected": True,
            "version": info.get("redis_version"),
            "uptime_days": info.get("uptime_in_days"),
            "connected_clients": info.get("connected_clients"),
            "used_memory_human": info.get("used_memory_human"),
        }
    except Exception as e:
        return {
            "ok": False,
            "connected": False,
            "error": str(e)
        }


@router.get("/stats")
def get_rate_limit_stats(admin: Usuario = Depends(require_admin)):
    """
    Obtiene estadísticas generales de rate limiting.
    
    Returns:
        Estadísticas agregadas
    """
    if not redis_client:
        raise HTTPException(
            status_code=503,
            detail="Redis no disponible"
        )
    
    try:
        from backend.config.rate_limits import REDIS_KEY_PREFIX
        
        # Obtener todas las keys
        pattern = f"{REDIS_KEY_PREFIX}*"
        keys = redis_client.keys(pattern)
        
        # Agrupar por tipo de límite
        stats = {}
        for key in keys:
            # Extraer tipo de límite
            parts = key.replace(REDIS_KEY_PREFIX, "").split(":")
            if len(parts) >= 1:
                limit_type = parts[0]
                
                if limit_type not in stats:
                    stats[limit_type] = {
                        "count": 0,
                        "total_requests": 0
                    }
                
                stats[limit_type]["count"] += 1
                value = redis_client.get(key)
                if value:
                    stats[limit_type]["total_requests"] += int(value)
        
        return {
            "ok": True,
            "total_active_limits": len(keys),
            "by_type": stats
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener estadísticas: {str(e)}"
        )
