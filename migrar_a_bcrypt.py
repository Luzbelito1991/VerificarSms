"""
Script de migración: SHA-256 → bcrypt
ADVERTENCIA: Este script convierte contraseñas hasheadas con SHA-256 a bcrypt.
Como no podemos revertir el hash SHA-256, todas las contraseñas se resetearán.
"""
import bcrypt
from backend.database import SessionLocal, engine
from backend.models import Base, Usuario

def migrar():
    print("⚠️  ADVERTENCIA: Este script recreará la base de datos y reseteará contraseñas")
    print("   Se creará un usuario admin por defecto con password 'admin123'\n")
    
    respuesta = input("¿Continuar? (si/no): ")
    if respuesta.lower() != "si":
        print("❌ Migración cancelada")
        return
    
    # 1. Recrear tablas
    print("\n🗂️  Recreando estructura de base de datos...")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    
    # 2. Crear usuario admin por defecto
    db = SessionLocal()
    try:
        admin_hash = bcrypt.hashpw("admin123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        admin = Usuario(
            usuario="admin",
            hash_password=admin_hash,
            rol="admin"
        )
        db.add(admin)
        db.commit()
        print("✅ Usuario 'admin' creado con contraseña 'admin123'")
        
        # Crear usuario operador de prueba
        operador_hash = bcrypt.hashpw("operador123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        operador = Usuario(
            usuario="operador",
            hash_password=operador_hash,
            rol="operador"
        )
        db.add(operador)
        db.commit()
        print("✅ Usuario 'operador' creado con contraseña 'operador123'")
        
        print("\n🎉 Migración completada exitosamente")
        print("\n📋 Credenciales por defecto:")
        print("   Admin: admin / admin123")
        print("   Operador: operador / operador123")
        
    except Exception as e:
        print(f"❌ Error durante migración: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    migrar()
