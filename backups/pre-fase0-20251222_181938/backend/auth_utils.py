from fastapi import Request, HTTPException, status, Depends
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import Usuario

# ======================================
# 🔐 Dependencia de autenticación basada en sesión
# ======================================
# Esta función se usa como dependencia en rutas protegidas.
# Verifica que haya una sesión activa y que el usuario exista en la base.
# Si no está logueado o no se encuentra en la base, lanza error HTTP.

def get_current_user(
    request: Request,
    db: Session = Depends(get_db)
) -> Usuario:
    username = request.session.get("usuario")  # 🧠 Obtiene usuario desde sesión

    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Sesión no iniciada"  # 🔒 No hay usuario en sesión
        )

    # 🗃️ Busca el usuario en la base
    user = db.query(Usuario).filter_by(usuario=username).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )

    return user  # ✅ Devuelve el objeto Usuario si todo está bien