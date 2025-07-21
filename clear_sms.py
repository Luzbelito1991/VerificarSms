from backend.database import SessionLocal
from backend.models import Verificacion

db = SessionLocal()
db.query(Verificacion).delete()
db.commit()
db.close()

print("✅ Tabla de SMS vaciada exitosamente")