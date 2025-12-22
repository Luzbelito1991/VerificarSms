"""
Script para probar la conexión a PostgreSQL
"""
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def test_connection():
    print("🧪 Prueba de Conexión PostgreSQL")
    print("=" * 50)
    
    conn_params = {
        "host": "localhost",
        "port": 5432,
        "database": "verificarsms",
        "user": "verificarsms_user",
        "password": "VerificarSMS2025!"
    }
    
    try:
        print("\n📡 Conectando a PostgreSQL...")
        print(f"   Host: {conn_params['host']}")
        print(f"   Puerto: {conn_params['port']}")
        print(f"   Base de datos: {conn_params['database']}")
        print(f"   Usuario: {conn_params['user']}\n")
        
        conn = psycopg2.connect(**conn_params)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        print("✅ Conexión exitosa\n")
        
        # Obtener versión
        cursor.execute("SELECT version()")
        version = cursor.fetchone()[0]
        print(f"🐘 PostgreSQL Version:")
        print(f"   {version}\n")
        
        # Listar tablas
        cursor.execute("""
            SELECT tablename 
            FROM pg_tables 
            WHERE schemaname = 'public'
        """)
        tables = cursor.fetchall()
        
        print(f"📋 Tablas en schema public:")
        if tables:
            for table in tables:
                print(f"   - {table[0]}")
        else:
            print("   (ninguna - base de datos vacía)")
        
        print("\n" + "=" * 50)
        print("✅ Prueba de conexión exitosa")
        print("\n🎯 Próximos pasos:")
        print("   1. Migrar datos desde SQLite")
        print("   2. Actualizar database.py para usar PostgreSQL")
        print("   3. Actualizar .env con DATABASE_URL")
        
        cursor.close()
        conn.close()
        
    except psycopg2.OperationalError as e:
        print(f"\n❌ Error de conexión: {e}")
        print("\n💡 Verifica que:")
        print("   - El servicio PostgreSQL esté corriendo")
        print("   - Las credenciales sean correctas")
        print("   - El puerto 5432 esté disponible")
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_connection()
