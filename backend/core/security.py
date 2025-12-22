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
    """
    from backend.models import Usuario
    from backend.config.database import SessionLocal
    
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
