from backend.database import engine, Base, SessionLocal
from sqlalchemy import inspect
from backend.models import Verificacion

# 👀 Verificar si existe la tabla
inspector = inspect(engine)
if "verificaciones" in inspector.get_table_names():
    print("🧨 Eliminando tabla 'verificaciones'...")
    Verificacion.__table__.drop(engine)
else:
    print("ℹ️ La tabla 'verificaciones' no existe. No hay que eliminar.")

# 🏗️ Crear la tabla con estructura actualizada
print("🔧 Recreando tabla 'verificaciones' con DateTime...")
Verificacion.__table__.create(engine)

# 🧪 Probar que funciona insertando un dummy
print("📤 Insertando verificación de prueba...")
db = SessionLocal()
dummy = Verificacion(
    person_id="TEST12345678",
    phone_number="3814123456",
    merchant_code="777",
    verification_code="9999",
    fecha=None,  # se tomará por default datetime.now()
    usuario_id=1  # asegurate que exista un usuario con ID 1
)
db.add(dummy)
db.commit()
db.close()

print("✅ Tabla 'verificaciones' reiniciada y funcionando con DateTime")