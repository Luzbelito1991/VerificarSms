"""
Script para agregar la columna email a la tabla usuarios existente
"""
import sqlite3
import os

# Ruta a la base de datos
db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "usuarios.db")

try:
    # Conectar a la base de datos
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Verificar si la columna ya existe
    cursor.execute("PRAGMA table_info(usuarios)")
    columns = [column[1] for column in cursor.fetchall()]
    
    if "email" in columns:
        print("✅ La columna 'email' ya existe en la tabla usuarios")
    else:
        # Agregar la columna email (sin UNIQUE porque SQLite no lo permite en ALTER TABLE)
        cursor.execute("""
            ALTER TABLE usuarios 
            ADD COLUMN email VARCHAR(255)
        """)
        conn.commit()
        print("✅ Columna 'email' agregada exitosamente a la tabla usuarios")
        print("⚠️  Nota: La restricción UNIQUE se aplicará en nuevos registros")
    
    # Mostrar estructura de la tabla
    cursor.execute("PRAGMA table_info(usuarios)")
    print("\n📋 Estructura actual de la tabla usuarios:")
    for column in cursor.fetchall():
        print(f"  - {column[1]} ({column[2]})")
    
    conn.close()
    
except Exception as e:
    print(f"❌ Error: {e}")
