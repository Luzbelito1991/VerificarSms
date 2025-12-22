"""
Script para crear tabla de sucursales y migrar datos desde el config
"""
import sqlite3
import os
import sys

# Agregar el path del proyecto
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from backend.config.settings import Settings

# Cargar configuración
settings = Settings()

# Ruta a la base de datos
db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "usuarios.db")

try:
    # Conectar a la base de datos
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Verificar si la tabla ya existe
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='sucursales'")
    tabla_existe = cursor.fetchone()
    
    if tabla_existe:
        print("⚠️  La tabla 'sucursales' ya existe")
        respuesta = input("¿Deseas recrearla? (s/n): ")
        if respuesta.lower() != 's':
            print("❌ Operación cancelada")
            conn.close()
            sys.exit(0)
        
        # Eliminar tabla existente
        cursor.execute("DROP TABLE sucursales")
        print("🗑️  Tabla anterior eliminada")
    
    # Crear tabla de sucursales
    cursor.execute("""
        CREATE TABLE sucursales (
            codigo VARCHAR(10) PRIMARY KEY,
            nombre VARCHAR(100) NOT NULL
        )
    """)
    print("✅ Tabla 'sucursales' creada exitosamente")
    
    # Migrar datos desde el config
    print("\n📊 Migrando sucursales desde la configuración...")
    for codigo, nombre in settings.SUCURSALES.items():
        cursor.execute(
            "INSERT INTO sucursales (codigo, nombre) VALUES (?, ?)",
            (codigo, nombre)
        )
        print(f"  ✓ {codigo}: {nombre}")
    
    conn.commit()
    
    # Mostrar resumen
    cursor.execute("SELECT COUNT(*) FROM sucursales")
    total = cursor.fetchone()[0]
    print(f"\n✅ Migración completada: {total} sucursales registradas")
    
    # Mostrar todas las sucursales
    cursor.execute("SELECT codigo, nombre FROM sucursales ORDER BY codigo")
    print("\n📋 Sucursales en la base de datos:")
    for row in cursor.fetchall():
        print(f"  - {row[0]}: {row[1]}")
    
    conn.close()
    
except Exception as e:
    print(f"❌ Error: {e}")
