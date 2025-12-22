"""
Script para eliminar todas las sucursales de la base de datos
"""
import sqlite3
import os

# Ruta a la base de datos
db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "usuarios.db")

try:
    # Conectar a la base de datos
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Verificar cuántas sucursales hay
    cursor.execute("SELECT COUNT(*) FROM sucursales")
    total_antes = cursor.fetchone()[0]
    
    if total_antes == 0:
        print("⚠️  No hay sucursales para eliminar")
        conn.close()
        exit(0)
    
    print(f"📊 Sucursales actuales: {total_antes}")
    
    # Mostrar las sucursales antes de eliminar
    cursor.execute("SELECT codigo, nombre FROM sucursales ORDER BY codigo")
    print("\n📋 Sucursales a eliminar:")
    for row in cursor.fetchall():
        print(f"  - {row[0]}: {row[1]}")
    
    # Confirmar eliminación
    print("\n🗑️  Eliminando todas las sucursales...")
    cursor.execute("DELETE FROM sucursales")
    conn.commit()
    
    # Verificar
    cursor.execute("SELECT COUNT(*) FROM sucursales")
    total_despues = cursor.fetchone()[0]
    
    print(f"\n✅ {total_antes} sucursales eliminadas")
    print(f"📊 Total actual: {total_despues}")
    
    conn.close()
    
except Exception as e:
    print(f"❌ Error: {e}")
