from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 🗂️ Ruta de la base de datos — ajustala si usás otro archivo
DATABASE_URL = "sqlite:///./usuarios.db"

# 🔌 Motor de conexión
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}  # Solo necesario para SQLite
)

# ⚙️ Configuración de sesiones
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# 📐 Clase base para modelos SQLAlchemy
Base = declarative_base()

# ✅ Función que se usa con Depends en FastAPI
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()