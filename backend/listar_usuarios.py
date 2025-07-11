import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.database import SessionLocal
from backend.models import Usuario

db = SessionLocal()

usuarios = db.query(Usuario).all()

if usuarios:
    print("👥 Lista de usuarios registrados:")
    for u in usuarios:
        print(f"- {u.usuario} ({u.rol})")
else:
    print("⚠️ No hay usuarios registrados.")

db.close()