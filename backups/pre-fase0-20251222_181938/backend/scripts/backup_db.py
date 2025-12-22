"""
Script para crear backups de la base de datos
"""
import sqlite3
import shutil
from pathlib import Path
from datetime import datetime

# Rutas
db_path = Path(__file__).parent.parent.parent / "usuarios.db"
backup_dir = Path(__file__).parent.parent.parent / "backups"

def crear_backup():
    """Crea un backup de la base de datos con timestamp"""
    try:
        # Crear directorio de backups si no existe
        backup_dir.mkdir(exist_ok=True)
        
        # Nombre del backup con timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"usuarios_backup_{timestamp}.db"
        backup_path = backup_dir / backup_name
        
        # Copiar base de datos
        shutil.copy2(db_path, backup_path)
        
        # Obtener tamaño del archivo
        size_mb = backup_path.stat().st_size / (1024 * 1024)
        
        print("✅ Backup creado exitosamente")
        print(f"📁 Ubicación: {backup_path}")
        print(f"📊 Tamaño: {size_mb:.2f} MB")
        print(f"🕒 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Listar todos los backups
        backups = sorted(backup_dir.glob("usuarios_backup_*.db"))
        print(f"\n📋 Total de backups: {len(backups)}")
        
        return backup_path
        
    except Exception as e:
        print(f"❌ Error al crear backup: {e}")
        return None

def exportar_sql():
    """Exporta la base de datos a un archivo SQL"""
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        sql_name = f"usuarios_export_{timestamp}.sql"
        sql_path = backup_dir / sql_name
        
        # Crear directorio si no existe
        backup_dir.mkdir(exist_ok=True)
        
        # Conectar y exportar
        conn = sqlite3.connect(db_path)
        
        with open(sql_path, 'w', encoding='utf-8') as f:
            for line in conn.iterdump():
                f.write(f"{line}\n")
        
        conn.close()
        
        size_kb = sql_path.stat().st_size / 1024
        
        print("✅ Exportación SQL creada exitosamente")
        print(f"📁 Ubicación: {sql_path}")
        print(f"📊 Tamaño: {size_kb:.2f} KB")
        
        return sql_path
        
    except Exception as e:
        print(f"❌ Error al exportar SQL: {e}")
        return None

def listar_backups():
    """Lista todos los backups disponibles"""
    if not backup_dir.exists():
        print("⚠️  No hay backups disponibles")
        return
    
    backups = sorted(backup_dir.glob("usuarios_backup_*.db"), reverse=True)
    sql_exports = sorted(backup_dir.glob("usuarios_export_*.sql"), reverse=True)
    
    if backups:
        print(f"\n📦 Backups (.db) - Total: {len(backups)}")
        print("-" * 80)
        for backup in backups[:10]:  # Mostrar últimos 10
            size_mb = backup.stat().st_size / (1024 * 1024)
            timestamp = backup.stem.replace("usuarios_backup_", "")
            print(f"  • {backup.name} - {size_mb:.2f} MB")
    
    if sql_exports:
        print(f"\n📄 Exportaciones SQL - Total: {len(sql_exports)}")
        print("-" * 80)
        for sql in sql_exports[:10]:  # Mostrar últimos 10
            size_kb = sql.stat().st_size / 1024
            print(f"  • {sql.name} - {size_kb:.2f} KB")

def main():
    print("="*80)
    print("🗄️  BACKUP DE BASE DE DATOS")
    print("="*80)
    
    print("\n1. Creando backup binario (.db)...")
    crear_backup()
    
    print("\n" + "="*80)
    print("2. Creando exportación SQL...")
    exportar_sql()
    
    print("\n" + "="*80)
    listar_backups()
    
    print("\n" + "="*80)
    print("✅ Proceso completado")
    print("="*80)

if __name__ == "__main__":
    main()
