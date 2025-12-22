"""Configuración de la base de datos SQLAlchemy"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .settings import settings

# 🔌 Motor de conexión con configuración específica por tipo de BD
if settings.DATABASE_URL.startswith("postgresql"):
    # PostgreSQL: Pool de conexiones para multi-usuario
    engine = create_engine(
        settings.DATABASE_URL,
        pool_size=10,  # 🔄 Pool de 10 conexiones
        max_overflow=20,  # 📈 Hasta 30 conexiones simultáneas
        pool_pre_ping=True,  # ✅ Verificar conexiones antes de usar
        pool_recycle=3600,  # 🔄 Reciclar conexiones cada hora
        echo=settings.DEBUG  # 🐞 Log SQL queries en debug
    )
else:
    # SQLite: Configuración simple para desarrollo
    engine = create_engine(
        settings.DATABASE_URL,
        connect_args={"check_same_thread": False},
        echo=settings.DEBUG
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
