# 📦 Importaciones necesarias
from fastapi import APIRouter, HTTPException, Request, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models import Usuario
import bcrypt

# 🚪 Inicializar el router
router = APIRouter()

# 🔧 Función auxiliar para hashear contraseñas con bcrypt
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

# 🔐 Función para verificar contraseñas
def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

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

# 🔓 Iniciar sesión: validar credenciales y guardar sesión en cookies
@router.post("/login")
async def login(data: LoginRequest, request: Request, db: Session = Depends(get_db)):
    user = db.query(Usuario).filter_by(usuario=data.usuario).first()

    if not user or not verify_password(data.password, user.hash_password):
        raise HTTPException(status_code=401, detail="Credenciales inválidas")

    request.session["usuario"] = user.usuario
    request.session["rol"] = user.rol

    return {"ok": True, "usuario": user.usuario, "rol": user.rol, "mensaje": "Inicio de sesión exitoso"}

# ✏️ Editar usuario: nombre, contraseña y rol
@router.put("/editar-usuario/{nombre}")
def editar_usuario(nombre: str, data: UsuarioUpdate, request: Request, db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter_by(usuario=nombre).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    # 🔍 Detectar si está editando su propio usuario
    usuario_sesion = request.session.get("usuario")
    editando_propio_usuario = usuario_sesion and usuario_sesion.lower() == nombre.lower()

    if data.nuevo_usuario != nombre:
        if db.query(Usuario).filter_by(usuario=data.nuevo_usuario).first():
            raise HTTPException(status_code=400, detail="El nuevo nombre ya está en uso")
        usuario.usuario = data.nuevo_usuario

        # 🔄 Actualizar sesión si está editando su propio usuario
        if editando_propio_usuario:
            request.session["usuario"] = data.nuevo_usuario

    if data.password:
        # Solo actualizar si la contraseña cambió
        if not verify_password(data.password, usuario.hash_password):
            usuario.hash_password = hash_password(data.password)

    if data.rol and data.rol != usuario.rol:
        usuario.rol = data.rol
        
        # 🔄 Actualizar rol en sesión si está editando su propio usuario
        if editando_propio_usuario:
            request.session["rol"] = data.rol

    db.commit()

    return {
        "ok": True,
        "usuario": usuario.usuario,
        "rol": usuario.rol,
        "editando_propio_usuario": editando_propio_usuario,  # Informa al frontend
        "mensaje": "Usuario actualizado correctamente"
    }

from backend.models import Usuario, Verificacion  # agrega Verificacion

@router.delete("/eliminar-usuario/{nombre}")
def eliminar_usuario(nombre: str, request: Request, db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter_by(usuario=nombre).first()
    if not usuario:
        raise HTTPException(status_code=404, detail=f"El usuario '{nombre}' no existe")

    # 🚫 Prevenir eliminar el usuario de la sesión actual
    usuario_sesion = request.session.get("usuario")
    if usuario_sesion and usuario_sesion.lower() == nombre.lower():
        raise HTTPException(
            status_code=403, 
            detail="No podés eliminar tu propio usuario mientras tenés la sesión activa"
        )

    # 🗑️ Las verificaciones se borran automáticamente con cascade
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

# 🔐 Obtener usuario actual de la sesión
@router.get("/usuario-actual")
def obtener_usuario_actual(request: Request, db: Session = Depends(get_db)):
    usuario_nombre = request.session.get("usuario")
    
    if not usuario_nombre:
        raise HTTPException(status_code=401, detail="No hay sesión activa")
    
    usuario = db.query(Usuario).filter_by(usuario=usuario_nombre).first()
    
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    return {
        "ok": True,
        "usuario": usuario.usuario,
        "rol": usuario.rol
    }