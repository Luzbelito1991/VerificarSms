"""
Script para exportar todos los datos de SQLite a JSON como backup
Ejecutar antes de migrar a PostgreSQL
"""
import sqlite3
import json
from datetime import datetime
from pathlib import Path

def export_to_json():
    """Exporta todas las tablas de SQLite a JSON"""
    
    # Conectar a SQLite
    conn = sqlite3.connect('usuarios.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Crear carpeta de backups si no existe
    backup_dir = Path('backups')
    backup_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Obtener todas las tablas
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]
    
    backup_data = {
        'export_date': timestamp,
        'database': 'usuarios.db',
        'tables': {}
    }
    
    # Exportar cada tabla
    for table in tables:
        print(f"📊 Exportando tabla: {table}")
        cursor.execute(f"SELECT * FROM {table}")
        rows = cursor.fetchall()
        
        # Convertir a lista de diccionarios
        table_data = []
        for row in rows:
            row_dict = {}
            for key in row.keys():
                value = row[key]
                # Convertir datetime a string
                if isinstance(value, (datetime,)):
                    value = value.isoformat()
                row_dict[key] = value
            table_data.append(row_dict)
        
        backup_data['tables'][table] = table_data
        print(f"   ✅ {len(table_data)} registros exportados")
    
    # Guardar JSON
    output_file = backup_dir / f'sqlite_backup_{timestamp}.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(backup_data, f, indent=2, ensure_ascii=False)
    
    conn.close()
    
    print(f"\n✅ Backup JSON creado: {output_file}")
    print(f"📦 Tamaño: {output_file.stat().st_size / 1024:.2f} KB")
    
    return str(output_file)

if __name__ == '__main__':
    print("🔄 Iniciando exportación de datos...")
    export_to_json()
    print("\n✨ Exportación completada!")
