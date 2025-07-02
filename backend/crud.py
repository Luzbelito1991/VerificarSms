import json
import os
import bcrypt

# Ruta al archivo JSON donde se almacenan los usuarios
DB_FILE = 'usuarios.json'

# Carga todos los usuarios desde el archivo JSON, o devuelve una lista vacía si no existe
def cargar_usuarios():
    if not os.path.exists(DB_FILE):
        return []
    with open(DB_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

# Guarda la lista de usuarios actualizada en el archivo JSON
def guardar_usuarios(usuarios):
    with open(DB_FILE, 'w', encoding='utf-8') as f:
        json.dump(usuarios, f, indent=2)

# Crea un nuevo usuario con contraseña encriptada (si no existe previamente)
def crear_usuario(usuario, password, rol):
    usuarios = cargar_usuarios()

    # Verifica si ya existe un usuario con el mismo nombre
    if any(u["usuario"] == usuario for u in usuarios):
        return False, "El usuario ya existe"

    # Encripta la contraseña usando bcrypt
    hash_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    # Agrega el nuevo usuario a la lista
    usuarios.append({"usuario": usuario, "password": hash_pw, "rol": rol})
    guardar_usuarios(usuarios)
    return True, "Usuario creado"

# Elimina un usuario por nombre de usuario
def eliminar_usuario(usuario):
    usuarios = cargar_usuarios()
    nuevos = [u for u in usuarios if u["usuario"] != usuario]

    if len(nuevos) == len(usuarios):
        return False, "Usuario no encontrado"

    guardar_usuarios(nuevos)
    return True, "Usuario eliminado"

# Edita el rol y/o contraseña de un usuario existente
def editar_usuario(usuario, nuevo_rol=None, nueva_contraseña=None):
    usuarios = cargar_usuarios()

    for u in usuarios:
        if u["usuario"] == usuario:
            if nuevo_rol:
                u["rol"] = nuevo_rol
            if nueva_contraseña:
                # Encripta la nueva contraseña si se proporciona
                hash_pw = bcrypt.hashpw(nueva_contraseña.encode(), bcrypt.gensalt()).decode()
                u["password"] = hash_pw
            guardar_usuarios(usuarios)
            return True, "Usuario actualizado"

    return False, "Usuario no encontrado"

# Devuelve todos los usuarios, ocultando sus contraseñas (para mostrarlos en frontend)
def obtener_usuarios_sin_password():
    return [{"usuario": u["usuario"], "rol": u["rol"]} for u in cargar_usuarios()]