"""Utilidades de seguridad y autenticación"""
import hashlib
import bcrypt
from fastapi import Request, HTTPException, status
from sqlalchemy.orm import Session
from backend.config.database import get_db


def hash_password(password: str) -> str:
    """Hashea una contraseña usando bcrypt"""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifica si una contraseña coincide con su hash.
    Soporta tanto bcrypt (nuevo) como SHA-256 (legacy)
    """
    # Detectar si es bcrypt (empieza con $2b$ o $2a$)
    if hashed_password.startswith('$2b$') or hashed_password.startswith('$2a$'):
        try:
            return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
        except:
            return False
    else:
        # Legacy SHA-256
        sha256_hash = hashlib.sha256(plain_password.encode()).hexdigest()
        return sha256_hash == hashed_password


async def get_current_user(request: Request):
    """
    Dependencia para obtener el usuario actual de la sesión.
    Lee desde Redis para sesiones persistentes.
    """
    from backend.models import Usuario
    from backend.config.database import SessionLocal
    from backend.services.session_service import session_store
    
    # Intentar obtener session_id de Redis primero
    session_id = request.session.get("session_id")
    
    if session_id:
        # Leer sesión desde Redis
        session_data = session_store.get_session(session_id)
        if session_data:
            usuario_sesion = session_data.get("usuario")
        else:
            # Sesión expirada o inválida
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Sesión expirada"
            )
    else:
        # Fallback: leer desde SessionMiddleware (compatibilidad)
        usuario_sesion = request.session.get("usuario")
    
    if not usuario_sesion:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No autenticado"
        )
    
    # Obtener sesión DB temporal
    db = SessionLocal()
    try:
        user = db.query(Usuario).filter(Usuario.usuario == usuario_sesion).first()
    finally:
        db.close()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado"
        )
    
    return user
