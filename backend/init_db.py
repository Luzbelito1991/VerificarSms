"""Inicialización de la base de datos"""
from backend.config import engine, Base
from backend.models import Usuario, Verificacion, PasswordResetToken, Sucursal


def init_db():
    """Crea todas las tablas en la base de datos"""
    Base.metadata.create_all(bind=engine)
    print("✅ Base de datos inicializada correctamente")
    print("📊 Tablas creadas: usuarios, verificaciones, password_reset_tokens, sucursales")


if __name__ == "__main__":
    init_db()

    