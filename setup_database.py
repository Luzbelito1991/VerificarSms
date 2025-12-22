"""
Script para configurar la base de datos PostgreSQL
Crea la base de datos y usuario directamente desde Python
"""
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import getpass

def setup_database():
    print("🔐 Configuración de Base de Datos PostgreSQL")
    print("=" * 50)
    
    # Solicitar contraseña del usuario postgres
    password = getpass.getpass("Ingrese la contraseña del usuario postgres: ")
    
    try:
        # Conectar a la base de datos por defecto (postgres)
        print("\n📡 Conectando a PostgreSQL...")
        conn = psycopg2.connect(
            host="localhost",
            port=5432,
            user="postgres",
            password=password,
            database="postgres"
        )
        
        # Configurar autocommit para ejecutar comandos DDL
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        print("✅ Conexión exitosa\n")
        
        # 1. Crear usuario
        print("👤 Creando usuario verificarsms_user...")
        try:
            cursor.execute("CREATE USER verificarsms_user WITH PASSWORD 'VerificarSMS2025!'")
            print("✅ Usuario creado\n")
        except psycopg2.errors.DuplicateObject:
            print("ℹ️  Usuario ya existe (OK)\n")
        
        # 2. Crear base de datos
        print("🗄️  Creando base de datos verificarsms...")
        try:
            cursor.execute("""
                CREATE DATABASE verificarsms
                    WITH 
                    ENCODING = 'UTF8'
                    OWNER = verificarsms_user
            """)
            print("✅ Base de datos creada\n")
        except psycopg2.errors.DuplicateDatabase:
            print("ℹ️  Base de datos ya existe (OK)\n")
        
        # 3. Dar permisos
        print("🔑 Configurando permisos...")
        cursor.execute("GRANT ALL PRIVILEGES ON DATABASE verificarsms TO verificarsms_user")
        print("✅ Permisos asignados\n")
        
        cursor.close()
        conn.close()
        
        # 4. Conectar a la nueva base de datos para configurar el schema
        print("🔧 Configurando schema public...")
        conn2 = psycopg2.connect(
            host="localhost",
            port=5432,
            user="postgres",
            password=password,
            database="verificarsms"
        )
        conn2.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor2 = conn2.cursor()
        
        cursor2.execute("GRANT ALL ON SCHEMA public TO verificarsms_user")
        cursor2.execute("GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO verificarsms_user")
        cursor2.execute("GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO verificarsms_user")
        cursor2.execute("ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO verificarsms_user")
        cursor2.execute("ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO verificarsms_user")
        
        print("✅ Schema configurado\n")
        
        cursor2.close()
        conn2.close()
        
        print("\n" + "=" * 50)
        print("✅ Configuración completada exitosamente")
        print("\n📝 Credenciales de conexión:")
        print("   Host: localhost")
        print("   Puerto: 5432")
        print("   Base de datos: verificarsms")
        print("   Usuario: verificarsms_user")
        print("   Contraseña: VerificarSMS2025!")
        print("\n🔗 String de conexión:")
        print("   postgresql://verificarsms_user:VerificarSMS2025!@localhost:5432/verificarsms")
        
    except psycopg2.OperationalError as e:
        print(f"\n❌ Error de conexión: {e}")
        print("\n💡 Verifica que:")
        print("   - El servicio PostgreSQL esté corriendo")
        print("   - La contraseña sea correcta")
        print("   - El puerto 5432 esté disponible")
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    setup_database()
