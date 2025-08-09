from backend.database import SessionLocal
from backend.models import Verificacion

print("🧹 Limpiando todos los registros de la tabla 'verificaciones'...")

db = SessionLocal()
db.query(Verificacion).delete()
db.commit()
db.close()

print("✅ Tabla 'verificaciones' vaciada correctamente")