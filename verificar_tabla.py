from backend.database import SessionLocal
from backend.models import Verificacion

db = SessionLocal()
registros = db.query(Verificacion).order_by(Verificacion.fecha.desc()).all()

if not registros:
    print("🧹 La tabla 'verificaciones' está vacía")
else:
    print(f"📋 Total de registros: {len(registros)}\n")
    for r in registros:
        print(f"{r.fecha.strftime('%Y-%m-%d %H:%M:%S')} | {r.person_id} | {r.phone_number} | {r.merchant_code} | {r.verification_code} | usuario_id={r.usuario_id}")

db.close()