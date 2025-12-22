"""
Script para ver el contenido completo de la base de datos
"""
import sqlite3
from pathlib import Path

# Ruta a la base de datos
db_path = Path(__file__).parent.parent.parent / "usuarios.db"

def ver_tabla(cursor, nombre_tabla):
    """Muestra el contenido de una tabla"""
    print(f"\n{'='*80}")
    print(f"📋 TABLA: {nombre_tabla.upper()}")
    print(f"{'='*80}")
    
    # Obtener información de las columnas
    cursor.execute(f"PRAGMA table_info({nombre_tabla})")
    columnas = cursor.fetchall()
    nombres_columnas = [col[1] for col in columnas]
    
    # Obtener datos
    cursor.execute(f"SELECT * FROM {nombre_tabla}")
    filas = cursor.fetchall()
    
    print(f"\n📊 Total de registros: {len(filas)}")
    
    if len(filas) > 0:
        # Mostrar encabezados
        print("\n" + " | ".join(nombres_columnas))
        print("-" * 80)
        
        # Mostrar filas
        for fila in filas:
            valores = [str(v) if v is not None else "NULL" for v in fila]
            print(" | ".join(valores))
    else:
        print("⚠️  Tabla vacía")

def main():
    try:
        # Conectar a la base de datos
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🗄️  BASE DE DATOS: usuarios.db")
        print("="*80)
        
        # Obtener lista de tablas
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tablas = cursor.fetchall()
        
        print(f"\n📑 Tablas encontradas: {len(tablas)}")
        print([tabla[0] for tabla in tablas])
        
        # Mostrar contenido de cada tabla
        for (nombre_tabla,) in tablas:
            ver_tabla(cursor, nombre_tabla)
        
        conn.close()
        
        print(f"\n{'='*80}")
        print("✅ Consulta completada")
        print(f"{'='*80}\n")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
