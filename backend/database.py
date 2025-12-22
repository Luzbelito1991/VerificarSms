import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# 📁 Cargar variables de entorno
load_dotenv()

# 🐘 URL de base de datos (PostgreSQL por defecto, SQLite como fallback)
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./usuarios.db")

# 🔌 Motor de conexión con configuración específica por tipo de BD
if DATABASE_URL.startswith("postgresql"):
    # PostgreSQL: Sin check_same_thread, con pool de conexiones
    engine = create_engine(
        DATABASE_URL,
        pool_size=10,  # 🔄 Pool de 10 conexiones para multi-usuario
        max_overflow=20,  # 📈 Hasta 30 conexiones simultáneas
        pool_pre_ping=True,  # ✅ Verificar conexiones antes de usar
        echo=False  # 🔇 Cambiar a True para debug SQL
    )
else:
    # SQLite: Con check_same_thread para compatibilidad
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        echo=False
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