from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import RedirectResponse, JSONResponse
from pydantic import BaseModel
from backend.database import SessionLocal
from backend.models import Usuario
import hashlib

router = APIRouter()

# 📦 Esquemas para recibir datos del frontend
class UsuarioCreate(BaseModel):
    usuario: str
    password: str
    rol: str | None = None

class LoginRequest(BaseModel):
    usuario: str
    password: str

# 🔐 Ruta de login con sesión
@router.post("/login")
async def login(data: LoginRequest, request: Request):
    db = SessionLocal()
    try:
        user = db.query(Usuario).filter_by(usuario=data.usuario).first()

        if not user or user.hash_password != hashlib.sha256(data.password.encode()).hexdigest():
            return JSONResponse(status_code=401, content={"ok": False, "detail": "Credenciales inválidas"})

        # ✅ Guardar datos en sesión
        request.session["usuario"] = user.usuario
        request.session["rol"] = user.rol

        return {
            "ok": True,
            "usuario": user.usuario,
            "rol": user.rol
        }

    finally:
        db.close()

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
def eliminar_usuario(nombre: str):
    db = SessionLocal()
    try:
        usuario = db.query(Usuario).filter_by(usuario=nombre).first()
        if not usuario:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")

        db.delete(usuario)
        db.commit()
        return {"ok": True}
    finally:
        db.close()

# ✏️ Editar usuario existente
@router.put("/editar-usuario/{nombre}")
def editar_usuario(nombre: str, data: UsuarioCreate):
    db = SessionLocal()
    try:
        usuario = db.query(Usuario).filter_by(usuario=nombre).first()
        if not usuario:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")

        if data.password:
            usuario.hash_password = hashlib.sha256(data.password.encode()).hexdigest()

        usuario.rol = data.rol or usuario.rol
        db.commit()

        return {"ok": True, "usuario": usuario.usuario, "rol": usuario.rol}
    finally:
        db.close()