# 📦 Importaciones necesarias
from fastapi import APIRouter, HTTPException, Request, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

# 🆕 Usar configuración y servicios centralizados
from backend.config import get_db
from backend.models import Usuario
from backend.services import AuthService, UserService
from backend.services.session_service import session_store
from backend.core.security import verify_password

# 🚪 Inicializar el router
router = APIRouter()

# 📦 Esquemas para datos recibidos desde el frontend
class UsuarioCreate(BaseModel):
    usuario: str
    password: str
    rol: str | None = None
    email: str | None = None

class UsuarioUpdate(BaseModel):
    nuevo_usuario: str
    password: str | None = None
    rol: str | None = None
    email: str | None = None

class LoginRequest(BaseModel):
    usuario: str
    password: str

# 👤 Crear nuevo usuario si no existe
@router.post("/crear-usuario")
def crear_usuario(data: UsuarioCreate, db: Session = Depends(get_db)):
    # Verificar si existe
    if UserService.get_user_by_username(db, data.usuario):
        raise HTTPException(status_code=400, detail="El usuario ya existe")

    # Verificar email único si se proporciona
    if data.email:
        existing_email = db.query(Usuario).filter(Usuario.email == data.email).first()
        if existing_email:
            raise HTTPException(status_code=400, detail="El email ya está registrado")

    # Crear usando el servicio
    nuevo = AuthService.create_user(
        db,
        username=data.usuario,
        password=data.password,
        rol=data.rol or "operador"
    )
    
    # Agregar email si se proporcionó
    if data.email:
        nuevo.email = data.email
        db.commit()
        db.refresh(nuevo)

    return {
        "ok": True,
        "usuario": nuevo.usuario,
        "rol": nuevo.rol,
        "email": nuevo.email,
        "mensaje": "Usuario creado correctamente"
    }

# 🔓 Iniciar sesión: validar credenciales y guardar sesión en Redis
@router.post("/login")
async def login(data: LoginRequest, request: Request, db: Session = Depends(get_db)):
    # Autenticar usando el servicio
    user = AuthService.authenticate_user(db, data.usuario, data.password)

    if not user:
        raise HTTPException(status_code=401, detail="Credenciales inválidas")

    # Crear sesión en Redis
    session_id = session_store.create_session({
        "usuario": user.usuario,
        "rol": user.rol,
        "id": user.id,
        "email": user.email
    })
    
    # Guardar session_id en cookie (mantener compatibilidad)
    request.session["session_id"] = session_id
    request.session["usuario"] = user.usuario
    request.session["rol"] = user.rol

    return {
        "ok": True,
        "usuario": user.usuario,
        "rol": user.rol,
        "mensaje": "Inicio de sesión exitoso"
    }

# ✏️ Editar usuario: nombre, contraseña y rol
@router.put("/editar-usuario/{nombre}")
def editar_usuario(nombre: str, data: UsuarioUpdate, request: Request, db: Session = Depends(get_db)):
    usuario = UserService.get_user_by_username(db, nombre)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    # 🔍 Detectar si está editando su propio usuario
    usuario_sesion = request.session.get("usuario")
    editando_propio_usuario = usuario_sesion and usuario_sesion.lower() == nombre.lower()

    # Actualizar nombre si cambió
    if data.nuevo_usuario != nombre:
        if UserService.get_user_by_username(db, data.nuevo_usuario):
            raise HTTPException(status_code=400, detail="El nuevo nombre ya está en uso")
        usuario.usuario = data.nuevo_usuario

        # 🔄 Actualizar sesión si está editando su propio usuario
        if editando_propio_usuario:
            request.session["usuario"] = data.nuevo_usuario

    # Actualizar contraseña solo si cambió
    if data.password:
        if not verify_password(data.password, usuario.hash_password):
            AuthService.change_password(db, usuario.id, data.password)

    # Actualizar rol
    if data.rol and data.rol != usuario.rol:
        usuario.rol = data.rol
        
        # 🔄 Actualizar rol en sesión si está editando su propio usuario
        if editando_propio_usuario:
            request.session["rol"] = data.rol
    
    # Actualizar email si cambió
    if data.email is not None:
        if data.email != usuario.email:
            # Verificar que no esté en uso por otro usuario
            existing = db.query(Usuario).filter(Usuario.email == data.email, Usuario.id != usuario.id).first()
            if existing:
                raise HTTPException(status_code=400, detail="El email ya está en uso")
            usuario.email = data.email

    db.commit()

    return {
        "ok": True,
        "usuario": usuario.usuario,
        "rol": usuario.rol,
        "email": usuario.email,
        "editando_propio_usuario": editando_propio_usuario,
        "mensaje": "Usuario actualizado correctamente"
    }

# 🗑️ Eliminar usuario
@router.delete("/eliminar-usuario/{nombre}")
def eliminar_usuario(nombre: str, request: Request, db: Session = Depends(get_db)):
    usuario = UserService.get_user_by_username(db, nombre)
    if not usuario:
        raise HTTPException(status_code=404, detail=f"El usuario '{nombre}' no existe")

    # 🚫 Prevenir eliminar el usuario de la sesión actual
    usuario_sesion = request.session.get("usuario")
    if usuario_sesion and usuario_sesion.lower() == nombre.lower():
        raise HTTPException(
            status_code=403, 
            detail="No podés eliminar tu propio usuario mientras tenés la sesión activa"
        )

    # 🗑️ Eliminar usando el servicio (cascade automático)
    UserService.delete_user(db, usuario.id)

    return {"ok": True, "mensaje": f"Usuario '{nombre}' eliminado correctamente"}


# 🔍 Ver detalle de un usuario
@router.get("/usuario-detalle/{nombre}")
def ver_usuario(nombre: str, db: Session = Depends(get_db)):
    usuario = UserService.get_user_by_username(db, nombre)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    return {
        "ok": True,
        "usuario": usuario.usuario,
        "rol": usuario.rol,
        "email": usuario.email or ""
    }

# 🔐 Obtener usuario actual de la sesión
@router.get("/usuario-actual")
def obtener_usuario_actual(request: Request, db: Session = Depends(get_db)):
    usuario_nombre = request.session.get("usuario")
    
    if not usuario_nombre:
        raise HTTPException(status_code=401, detail="No hay sesión activa")
    
    usuario = UserService.get_user_by_username(db, usuario_nombre)
    
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    return {
        "ok": True,
        "usuario": usuario.usuario,
        "rol": usuario.rol
    }
