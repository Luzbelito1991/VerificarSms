# 📦 Importaciones necesarias
from fastapi import APIRouter, HTTPException, Request, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models import Usuario
import hashlib

# 🚪 Inicializar el router
router = APIRouter()

# 🔧 Función auxiliar para hashear contraseñas
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

# 📦 Esquemas para datos recibidos desde el frontend
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

# 👤 Crear nuevo usuario si no existe
@router.post("/crear-usuario")
def crear_usuario(data: UsuarioCreate, db: Session = Depends(get_db)):
    existe = db.query(Usuario).filter_by(usuario=data.usuario).first()
    if existe:
        raise HTTPException(status_code=400, detail="El usuario ya existe")

    nuevo = Usuario(
        usuario=data.usuario,
        hash_password=hash_password(data.password),
        rol=data.rol or "operador"
    )

    db.add(nuevo)
    db.commit()

    return {"ok": True, "usuario": nuevo.usuario, "rol": nuevo.rol, "mensaje": "Usuario creado correctamente"}

# 🔐 Iniciar sesión: validar credenciales y guardar sesión en cookies
@router.post("/login")
async def login(data: LoginRequest, request: Request, db: Session = Depends(get_db)):
    user = db.query(Usuario).filter_by(usuario=data.usuario).first()

    if not user or user.hash_password != hash_password(data.password):
        raise HTTPException(status_code=401, detail="Credenciales inválidas")

    request.session["usuario"] = user.usuario
    request.session["rol"] = user.rol

    return {"ok": True, "usuario": user.usuario, "rol": user.rol, "mensaje": "Inicio de sesión exitoso"}

# ✏️ Editar usuario: nombre, contraseña y rol
@router.put("/editar-usuario/{nombre}")
def editar_usuario(nombre: str, data: UsuarioUpdate, db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter_by(usuario=nombre).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    if data.nuevo_usuario != nombre:
        if db.query(Usuario).filter_by(usuario=data.nuevo_usuario).first():
            raise HTTPException(status_code=400, detail="El nuevo nombre ya está en uso")
        usuario.usuario = data.nuevo_usuario

    if data.password:
        nuevo_hash = hash_password(data.password)
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

# 🗑️ Eliminar usuario por nombre
@router.delete("/eliminar-usuario/{nombre}")
def eliminar_usuario(nombre: str, db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter_by(usuario=nombre).first()
    if not usuario:
        raise HTTPException(status_code=404, detail=f"El usuario '{nombre}' no existe")

    db.delete(usuario)
    db.commit()
    return {"ok": True, "mensaje": f"Usuario '{nombre}' eliminado correctamente"}

# 🔍 Ver detalle de un usuario
@router.get("/usuario-detalle/{nombre}")
def ver_usuario(nombre: str, db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter_by(usuario=nombre).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    return {
        "ok": True,
        "usuario": usuario.usuario,
        "rol": usuario.rol
    }