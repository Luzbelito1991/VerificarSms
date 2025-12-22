"""Configuración de la base de datos SQLAlchemy"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .settings import settings

# 🔌 Motor de conexión
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}
)

# ⚙️ Configuración de sesiones
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# 📐 Clase base para modelos SQLAlchemy
Base = declarative_base()


def get_db():
    """Generador de sesiones de base de datos para FastAPI Depends"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
