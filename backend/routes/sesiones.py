"""
Rutas para administración de sesiones activas
"""
from fastapi import APIRouter, Depends, HTTPException
from backend.models import Usuario
from backend.core import get_current_user
from backend.services.session_service import session_store

router = APIRouter(prefix="/api/sesiones", tags=["Sesiones"])

@router.get("/activas")
def get_sesiones_activas(current_user: Usuario = Depends(get_current_user)):
    """
    Obtener todas las sesiones activas (solo admin)
    """
    if current_user.rol.lower() != "admin":
        raise HTTPException(status_code=403, detail="Acceso denegado")
    
    sesiones = session_store.get_all_sessions()
    
    return {
        "ok": True,
        "total": len(sesiones),
        "sesiones": sesiones
    }

@router.delete("/cerrar/{session_id}")
def cerrar_sesion_admin(session_id: str, current_user: Usuario = Depends(get_current_user)):
    """
    Cerrar sesión de otro usuario (solo admin)
    """
    if current_user.rol.lower() != "admin":
        raise HTTPException(status_code=403, detail="Acceso denegado")
    
    session_store.delete_session(session_id)
    
    return {
        "ok": True,
        "mensaje": "Sesión cerrada correctamente"
    }
