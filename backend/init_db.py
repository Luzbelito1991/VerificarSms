from backend.database import engine, Base
from backend.models import Usuario

def init_db():
    Base.metadata.create_all(bind=engine)
    print("✅ Tabla 'usuarios' creada correctamente")

if __name__ == "__main__":
    init_db()

    