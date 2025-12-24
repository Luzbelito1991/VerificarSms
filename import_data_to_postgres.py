"""
Importar datos desde JSON a PostgreSQL en Docker
"""
import json
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.models import Usuario, Verificacion
from backend.config.database import Base

# URL de PostgreSQL en Docker
POSTGRES_URL = "postgresql://admin:admin123@localhost:5432/verificarsms"

print("🔄 Importando datos a PostgreSQL...")
print("=" * 60)

# Crear conexión
engine = create_engine(POSTGRES_URL)
Session = sessionmaker(bind=engine)
session = Session()

try:
    # Leer usuarios
    with open('usuarios_export.json', 'r', encoding='utf-8') as f:
        usuarios_data = json.load(f)
    
    print(f"\n📥 Importando {len(usuarios_data)} usuarios...")
    
    # Eliminar admin que creamos antes (evitar duplicados)
    session.query(Usuario).filter(Usuario.usuario == "admin").delete()
    session.commit()
    
    for data in usuarios_data:
        # Verificar si ya existe
        existing = session.query(Usuario).filter(Usuario.id == data['id']).first()
        if not existing:
            usuario = Usuario(
                id=data['id'],
                usuario=data['usuario'],
                hash_password=data['hash_password'],
                rol=data['rol'],
                email=data.get('email')
            )
            session.add(usuario)
    
    session.commit()
    print(f"✅ Usuarios importados")
    
    # Leer verificaciones
    with open('verificaciones_export.json', 'r', encoding='utf-8') as f:
        verificaciones_data = json.load(f)
    
    print(f"\n📥 Importando {len(verificaciones_data)} verificaciones...")
    
    for data in verificaciones_data:
        # Verificar si ya existe
        existing = session.query(Verificacion).filter(Verificacion.id == data['id']).first()
        if not existing:
            verif = Verificacion(
                id=data['id'],
                dni=data['dni'],
                telefono=data['telefono'],
                codigo_verificacion=data['codigo_verificacion'],
                fecha_envio=data['fecha_envio'],
                usuario_id=data['usuario_id'],
                sucursal=data.get('sucursal')
            )
            session.add(verif)
    
    session.commit()
    print(f"✅ Verificaciones importadas")
    
    # Verificar totales
    total_usuarios = session.query(Usuario).count()
    total_verificaciones = session.query(Verificacion).count()
    
    print("\n" + "=" * 60)
    print("📊 RESULTADO")
    print("=" * 60)
    print(f"Total usuarios en DB: {total_usuarios}")
    print(f"Total verificaciones en DB: {total_verificaciones}")
    print("\n🎉 ¡Importación completada!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    session.rollback()
finally:
    session.close()
