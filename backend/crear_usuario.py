import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.database import SessionLocal
from backend.models import Usuario
import hashlib

from backend.models import Usuario
import hashlib

# Datos del nuevo usuario
usuario = "Nora"
password = "123456"
rol = "admin"

# Crear sesión

db = SessionLocal()

# Verificar si existe
existe = db.query(Usuario).filter_by(usuario=usuario).first()
if existe:
    print("⚠️ El usuario ya existe.")
else:
    hash_pw = hashlib.sha256(password.encode()).hexdigest()
    nuevo = Usuario(usuario=usuario, hash_password=hash_pw, rol=rol)
    db.add(nuevo)
    db.commit()
    print(f"✅ Usuario '{usuario}' creado con rol '{rol}'.")

db.close()