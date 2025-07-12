from fastapi import APIRouter, HTTPException, Request, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
from backend.database import get_db, SessionLocal
from backend.models import Usuario
import hashlib

router = APIRouter()

# 📦 Esquemas para recibir datos del frontend
class UsuarioCreate(BaseModel):
    usuario: str
    password: str
    rol: str | None = None

class UsuarioUpdate(BaseModel):
    nuevo_usuario: str
    password: str | None = None
    rol: str | None = None

class LoginRequest(BaseModel):
    usuario: str
    password: str

# 🔐 Ruta de login con sesión
@router.post("/login")
async def login(data: LoginRequest, request: Request, db: Session = Depends(get_db)):
    user = db.query(Usuario).filter_by(usuario=data.usuario).first()

    hash_pw = hashlib.sha256(data.password.encode()).hexdigest()
    if not user or user.hash_password != hash_pw:
        raise HTTPException(status_code=401, detail="Credenciales inválidas")

    request.session["usuario"] = user.usuario
    request.session["rol"] = user.rol

    return {"ok": True, "usuario": user.usuario, "rol": user.rol}


# 👤 Crear usuario nuevo
@router.post("/crear-usuario")
def crear_usuario(data: UsuarioCreate):
    db = SessionLocal()
    try:
        existe = db.query(Usuario).filter_by(usuario=data.usuario).first()
        if existe:
            raise HTTPException(status_code=400, detail="El usuario ya existe")

        hash_pw = hashlib.sha256(data.password.encode()).hexdigest()
        nuevo = Usuario(usuario=data.usuario, hash_password=hash_pw, rol=data.rol or "operador")

        db.add(nuevo)
        db.commit()

        return {"ok": True, "usuario": nuevo.usuario, "rol": nuevo.rol}
    finally:
        db.close()

# 🗑️ Eliminar usuario
@router.delete("/eliminar-usuario/{nombre}")
def eliminar_usuario(nombre: str, db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter_by(usuario=nombre).first()
    if not usuario:
        return {"ok": False, "detail": f"El usuario '{nombre}' no existe"}

    db.delete(usuario)
    db.commit()
    return {"ok": True, "mensaje": f"Usuario '{nombre}' eliminado correctamente"}

# ✏️ Editar usuario existente (nombre, password, rol)
@router.put("/editar-usuario/{nombre}")
def editar_usuario(nombre: str, data: UsuarioUpdate, db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter_by(usuario=nombre).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    # Validar si el nuevo nombre ya existe
    if data.nuevo_usuario != nombre:
        existe = db.query(Usuario).filter_by(usuario=data.nuevo_usuario).first()
        if existe:
            raise HTTPException(status_code=400, detail="El nuevo nombre ya está en uso")
        usuario.usuario = data.nuevo_usuario

    if data.password:
        nuevo_hash = hashlib.sha256(data.password.encode()).hexdigest()
        if usuario.hash_password != nuevo_hash:
            usuario.hash_password = nuevo_hash

    if data.rol and data.rol != usuario.rol:
        usuario.rol = data.rol

    db.commit()

    return {
        "ok": True,
        "usuario": usuario.usuario,
        "rol": usuario.rol,
        "mensaje": "Usuario actualizado correctamente"
    }