# Importamos los módulos necesarios de FastAPI y otras utilidades
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from backend.database import SessionLocal  # Sesión de base de datos
from backend.models import Usuario  # Modelo de SQLAlchemy
import hashlib  # Para hashear contraseñas

# Creamos un router que encapsula todas las rutas relacionadas a usuarios
router = APIRouter()

# Definimos el esquema de datos que se espera al crear o editar usuarios
class UsuarioData(BaseModel):
    usuario: str               # Nombre de usuario obligatorio
    password: str              # Contraseña obligatoria
    rol: str | None = None     # Rol opcional, si no se especifica se usa "operador"

# Ruta GET para obtener la lista de todos los usuarios (sin mostrar contraseñas)
@router.get("/usuarios")
def listar_usuarios():
    db = SessionLocal()  # Abrimos una sesión con la base de datos
    try:
        usuarios = db.query(Usuario).all()  # Obtenemos todos los registros de la tabla usuarios
        return [{"id": u.id, "usuario": u.usuario, "rol": u.rol} for u in usuarios]
    finally:
        db.close()  # Cerramos la sesión

# Ruta POST para crear un nuevo usuario
@router.post("/crear-usuario", status_code=201)
def crear_usuario(data: UsuarioData):
    db = SessionLocal()
    try:
        # Verificamos que el nombre de usuario no esté repetido
        if db.query(Usuario).filter_by(usuario=data.usuario).first():
            raise HTTPException(status_code=400, detail="El usuario ya existe")

        # Hasheamos la contraseña con SHA-256 (no se guarda en texto plano)
        hash_pw = hashlib.sha256(data.password.encode()).hexdigest()

        # Creamos el nuevo usuario con los datos recibidos
        nuevo = Usuario(
            usuario=data.usuario,
            hash_password=hash_pw,
            rol=data.rol or "operador"  # Si no se pasó rol, se pone "operador" por defecto
        )
        db.add(nuevo)    # Lo agregamos a la sesión
        db.commit()      # Guardamos los cambios en la base
        return {"mensaje": "Usuario creado correctamente"}
    finally:
        db.close()

# Ruta PUT para modificar un usuario existente
@router.put("/editar-usuario/{usuario}")
def editar_usuario(usuario: str, data: UsuarioData):
    db = SessionLocal()
    try:
        # Buscamos el usuario por su nombre
        u = db.query(Usuario).filter_by(usuario=usuario).first()
        if not u:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")

        # Si se pasa un nuevo rol, lo actualizamos
        if data.rol:
            u.rol = data.rol

        # Si se pasa una nueva contraseña, la hasheamos y actualizamos
        if data.password:
            u.hash_password = hashlib.sha256(data.password.encode()).hexdigest()

        db.commit()  # Guardamos los cambios
        return {"mensaje": "Usuario actualizado correctamente"}
    finally:
        db.close()

# Ruta DELETE para eliminar un usuario existente
@router.delete("/eliminar-usuario/{usuario}")
def eliminar_usuario(usuario: str):
    db = SessionLocal()
    try:
        # Buscamos el usuario por su nombre
        u = db.query(Usuario).filter_by(usuario=usuario).first()
        if not u:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")

        db.delete(u)   # Eliminamos el usuario
        db.commit()    # Confirmamos los cambios
        return {"mensaje": f"{usuario} eliminado correctamente"}
    finally:
        db.close()