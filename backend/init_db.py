"""Inicialización de la base de datos"""
from backend.config import engine, Base
from backend.models import Usuario, Verificacion, PasswordResetToken, Sucursal
from backend.database import SessionLocal
import hashlib
import sys
import io

# Configurar encoding para Windows
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


def init_db():
    """Crea todas las tablas en la base de datos"""
    Base.metadata.create_all(bind=engine)
    print("✅ Base de datos inicializada correctamente")
    print("📊 Tablas creadas: usuarios, verificaciones, password_reset_tokens, sucursales")


def create_default_admin():
    """Crea un usuario administrador por defecto si no existe"""
    db = SessionLocal()
    try:
        # Verificar si ya existe el usuario admin
        admin = db.query(Usuario).filter(Usuario.usuario == "admin").first()
        
        if admin:
            print("ℹ️  Usuario 'admin' ya existe")
            return
        
        # Crear usuario admin con contraseña "admin123"
        password_hash = hashlib.sha256("admin123".encode()).hexdigest()
        admin = Usuario(
            usuario="admin",
            password=password_hash,
            rol="admin",
            sucursal="776"  # Sucursal por defecto
        )
        
        db.add(admin)
        db.commit()
        
        print("✅ Usuario administrador creado:")
        print("   👤 Usuario: admin")
        print("   🔑 Contraseña: admin123")
        print("   ⚠️  IMPORTANTE: Cambia esta contraseña después del primer login!")
        
    except Exception as e:
        print(f"❌ Error al crear usuario admin: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    init_db()
    create_default_admin()

    