"""
Script de Migración: SQLite → PostgreSQL
Migra todos los datos de usuarios.db a la base de datos PostgreSQL
"""
import sys
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

# Agregar el directorio raíz al path para importar los modelos
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.models import Usuario, Verificacion
from backend.models.password_reset import PasswordResetToken
from backend.models.sucursal import Sucursal
from backend.config.database import Base

print("🔄 Migración SQLite → PostgreSQL")
print("=" * 60)

# ========== CONFIGURACIÓN ==========
SQLITE_URL = "sqlite:///./usuarios.db"
POSTGRES_URL = "postgresql://admin:admin123@localhost:5432/verificarsms"

print(f"\n📂 Origen: {SQLITE_URL}")
print(f"🐘 Destino: {POSTGRES_URL}")
print("=" * 60)

# ========== CREAR CONEXIONES ==========
print("\n📡 Conectando a bases de datos...")

# Conexión SQLite (origen)
sqlite_engine = create_engine(SQLITE_URL, connect_args={"check_same_thread": False})
SqliteSession = sessionmaker(bind=sqlite_engine)
sqlite_session = SqliteSession()

# Conexión PostgreSQL (destino)
postgres_engine = create_engine(
    POSTGRES_URL, 
    echo=False,
    connect_args={"client_encoding": "utf8"}
)
PostgresSession = sessionmaker(bind=postgres_engine)
postgres_session = PostgresSession()

print("✅ Conexiones establecidas")

# ========== VERIFICAR TABLAS EN SQLITE ==========
print("\n🔍 Verificando tablas en SQLite...")
sqlite_inspector = inspect(sqlite_engine)
sqlite_tables = sqlite_inspector.get_table_names()
print(f"   Tablas encontradas: {', '.join(sqlite_tables)}")

# ========== CREAR TABLAS EN POSTGRESQL ==========
print("\n🏗️  Creando tablas en PostgreSQL...")
try:
    Base.metadata.create_all(bind=postgres_engine)
    print("✅ Tablas creadas exitosamente")
except Exception as e:
    print(f"⚠️  Advertencia al crear tablas: {e}")
    print("   (Puede ser normal si las tablas ya existen)")

# Verificar tablas creadas
postgres_inspector = inspect(postgres_engine)
postgres_tables = postgres_inspector.get_table_names()
print(f"   Tablas en PostgreSQL: {', '.join(postgres_tables)}")

# ========== FUNCIÓN DE MIGRACIÓN GENÉRICA ==========
def migrate_table(model_class, table_name):
    """Migra una tabla completa de SQLite a PostgreSQL"""
    print(f"\n📋 Migrando tabla: {table_name}")
    
    try:
        # Contar registros en SQLite
        count_sqlite = sqlite_session.query(model_class).count()
        print(f"   Registros en SQLite: {count_sqlite}")
        
        if count_sqlite == 0:
            print(f"   ℹ️  Tabla vacía, saltando...")
            return 0
        
        # Leer datos de SQLite
        records = sqlite_session.query(model_class).all()
        
        # Verificar si ya hay datos en PostgreSQL
        count_postgres = postgres_session.query(model_class).count()
        if count_postgres > 0:
            print(f"   ⚠️  PostgreSQL ya tiene {count_postgres} registros")
            respuesta = input(f"   ¿Eliminar y reemplazar? (s/N): ").strip().lower()
            if respuesta == 's':
                postgres_session.query(model_class).delete()
                postgres_session.commit()
                print(f"   🗑️  Registros eliminados")
            else:
                print(f"   ⏭️  Saltando migración de {table_name}")
                return 0
        
        # Insertar en PostgreSQL
        migrated = 0
        for record in records:
            # Crear diccionario con todos los atributos del registro
            record_dict = {}
            for column in model_class.__table__.columns:
                value = getattr(record, column.name)
                record_dict[column.name] = value
            
            # Crear nuevo registro en PostgreSQL
            new_record = model_class(**record_dict)
            postgres_session.add(new_record)
            migrated += 1
        
        postgres_session.commit()
        print(f"   ✅ {migrated} registros migrados")
        
        return migrated
        
    except Exception as e:
        postgres_session.rollback()
        print(f"   ❌ Error al migrar {table_name}: {e}")
        import traceback
        traceback.print_exc()
        return 0

# ========== MIGRAR DATOS ==========
print("\n" + "=" * 60)
print("📦 INICIANDO MIGRACIÓN DE DATOS")
print("=" * 60)

total_migrated = 0

# 1. Migrar Sucursales (no tienen dependencias)
if "sucursales" in sqlite_tables:
    total_migrated += migrate_table(Sucursal, "sucursales")

# 2. Migrar Usuarios (referenciados por otras tablas)
if "usuarios" in sqlite_tables:
    total_migrated += migrate_table(Usuario, "usuarios")

# 3. Migrar Verificaciones (dependen de usuarios)
if "verificaciones" in sqlite_tables:
    total_migrated += migrate_table(Verificacion, "verificaciones")

# 4. Migrar Password Reset Tokens (dependen de usuarios)
if "password_reset_tokens" in sqlite_tables:
    total_migrated += migrate_table(PasswordResetToken, "password_reset_tokens")

# ========== VALIDACIÓN FINAL ==========
print("\n" + "=" * 60)
print("🔍 VALIDACIÓN DE DATOS MIGRADOS")
print("=" * 60)

validation_ok = True

# Validar Sucursales
if "sucursales" in sqlite_tables:
    count_sqlite = sqlite_session.query(Sucursal).count()
    count_postgres = postgres_session.query(Sucursal).count()
    status = "✅" if count_sqlite == count_postgres else "❌"
    print(f"{status} Sucursales: SQLite={count_sqlite}, PostgreSQL={count_postgres}")
    if count_sqlite != count_postgres:
        validation_ok = False

# Validar Usuarios
if "usuarios" in sqlite_tables:
    count_sqlite = sqlite_session.query(Usuario).count()
    count_postgres = postgres_session.query(Usuario).count()
    status = "✅" if count_sqlite == count_postgres else "❌"
    print(f"{status} Usuarios: SQLite={count_sqlite}, PostgreSQL={count_postgres}")
    if count_sqlite != count_postgres:
        validation_ok = False

# Validar Verificaciones
if "verificaciones" in sqlite_tables:
    count_sqlite = sqlite_session.query(Verificacion).count()
    count_postgres = postgres_session.query(Verificacion).count()
    status = "✅" if count_sqlite == count_postgres else "❌"
    print(f"{status} Verificaciones: SQLite={count_sqlite}, PostgreSQL={count_postgres}")
    if count_sqlite != count_postgres:
        validation_ok = False

# Validar Password Reset Tokens
if "password_reset_tokens" in sqlite_tables:
    count_sqlite = sqlite_session.query(PasswordResetToken).count()
    count_postgres = postgres_session.query(PasswordResetToken).count()
    status = "✅" if count_sqlite == count_postgres else "❌"
    print(f"{status} Password Reset Tokens: SQLite={count_sqlite}, PostgreSQL={count_postgres}")
    if count_sqlite != count_postgres:
        validation_ok = False

# ========== RESUMEN ==========
print("\n" + "=" * 60)
print("📊 RESUMEN DE MIGRACIÓN")
print("=" * 60)
print(f"Total de registros migrados: {total_migrated}")
print(f"Validación: {'✅ EXITOSA' if validation_ok else '❌ FALLÓ'}")

if validation_ok:
    print("\n🎉 ¡Migración completada exitosamente!")
    print("\n📝 Próximos pasos:")
    print("   1. Verificar datos en PostgreSQL: python test_postgres.py")
    print("   2. Actualizar .env con DATABASE_URL de PostgreSQL")
    print("   3. Actualizar backend/database.py para usar PostgreSQL")
    print("   4. Probar aplicación con PostgreSQL")
    print("   5. Mantener usuarios.db como backup (NO ELIMINAR AÚN)")
else:
    print("\n⚠️  Algunos registros no coinciden. Revisar errores arriba.")

# Cerrar conexiones
sqlite_session.close()
postgres_session.close()

print("\n" + "=" * 60)
print("🔌 Conexiones cerradas")
print("=" * 60)
