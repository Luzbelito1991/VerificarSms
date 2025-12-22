"""
Sistema de sesiones con Redis
"""
import json
import secrets
from typing import Optional, Dict, Any
from datetime import datetime
from backend.config.redis_config import (
    get_redis_client, 
    SESSION_EXPIRE_SECONDS,
    SESSION_KEY_PREFIX
)

class RedisSessionStore:
    """
    Almacenamiento de sesiones en Redis
    """
    
    def __init__(self):
        self.redis = get_redis_client()
        self.expire_seconds = SESSION_EXPIRE_SECONDS
    
    def create_session(self, user_data: Dict[str, Any]) -> str:
        """
        Crear nueva sesión
        
        Args:
            user_data: Datos del usuario (usuario, rol, id, etc.)
        
        Returns:
            session_id: ID de sesión único
        """
        # Generar session ID seguro
        session_id = secrets.token_urlsafe(32)
        
        # Agregar timestamp
        session_data = {
            **user_data,
            "created_at": datetime.now().isoformat(),
            "last_activity": datetime.now().isoformat()
        }
        
        # Guardar en Redis con expiración
        key = f"{SESSION_KEY_PREFIX}{session_id}"
        self.redis.setex(
            key,
            self.expire_seconds,
            json.dumps(session_data)
        )
        
        return session_id
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Obtener datos de sesión
        
        Args:
            session_id: ID de sesión
        
        Returns:
            Datos de sesión o None si no existe
        """
        key = f"{SESSION_KEY_PREFIX}{session_id}"
        data = self.redis.get(key)
        
        if data:
            session_data = json.loads(data)
            
            # Actualizar última actividad
            session_data["last_activity"] = datetime.now().isoformat()
            self.redis.setex(
                key,
                self.expire_seconds,
                json.dumps(session_data)
            )
            
            return session_data
        
        return None
    
    def update_session(self, session_id: str, data: Dict[str, Any]):
        """
        Actualizar datos de sesión
        """
        key = f"{SESSION_KEY_PREFIX}{session_id}"
        existing = self.get_session(session_id)
        
        if existing:
            existing.update(data)
            existing["last_activity"] = datetime.now().isoformat()
            self.redis.setex(
                key,
                self.expire_seconds,
                json.dumps(existing)
            )
    
    def delete_session(self, session_id: str):
        """
        Eliminar sesión (logout)
        """
        key = f"{SESSION_KEY_PREFIX}{session_id}"
        self.redis.delete(key)
    
    def get_all_sessions(self) -> list:
        """
        Obtener todas las sesiones activas (para admin panel)
        """
        keys = self.redis.keys(f"{SESSION_KEY_PREFIX}*")
        sessions = []
        
        for key in keys:
            data = self.redis.get(key)
            if data:
                session_data = json.loads(data)
                ttl = self.redis.ttl(key)
                session_data["ttl_seconds"] = ttl
                session_data["session_id"] = key.replace(SESSION_KEY_PREFIX, "")
                sessions.append(session_data)
        
        return sessions
    
    def extend_session(self, session_id: str):
        """
        Extender tiempo de expiración de sesión
        """
        key = f"{SESSION_KEY_PREFIX}{session_id}"
        self.redis.expire(key, self.expire_seconds)

# Instancia global
session_store = RedisSessionStore()
