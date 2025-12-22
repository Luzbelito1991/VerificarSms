"""
Script para restaurar un backup de la base de datos
"""
import sqlite3
import shutil
from pathlib import Path
from datetime import datetime

# Rutas
db_path = Path(__file__).parent.parent.parent / "usuarios.db"
backup_dir = Path(__file__).parent.parent.parent / "backups"

def listar_backups_disponibles():
    """Lista todos los backups disponibles"""
    if not backup_dir.exists():
        print("⚠️  No hay backups disponibles")
        return []
    
    backups = sorted(backup_dir.glob("usuarios_backup_*.db"), reverse=True)
    
    if not backups:
        print("⚠️  No hay backups disponibles")
        return []
    
    print("\n📦 Backups disponibles:")
    print("-" * 80)
    for i, backup in enumerate(backups, 1):
        size_mb = backup.stat().st_size / (1024 * 1024)
        timestamp = backup.stem.replace("usuarios_backup_", "")
        fecha = datetime.strptime(timestamp, "%Y%m%d_%H%M%S").strftime("%Y-%m-%d %H:%M:%S")
        print(f"{i}. {backup.name}")
        print(f"   📅 Fecha: {fecha} | 📊 Tamaño: {size_mb:.2f} MB")
    
    return backups

def restaurar_backup(backup_path):
    """Restaura un backup específico"""
    try:
        # Crear backup de seguridad de la DB actual antes de restaurar
        if db_path.exists():
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            seguridad_path = backup_dir / f"usuarios_pre_restore_{timestamp}.db"
            shutil.copy2(db_path, seguridad_path)
            print(f"✅ Backup de seguridad creado: {seguridad_path.name}")
        
        # Restaurar el backup seleccionado
        shutil.copy2(backup_path, db_path)
        
        print(f"\n✅ Base de datos restaurada exitosamente")
        print(f"📁 Desde: {backup_path.name}")
        print(f"📍 Hacia: {db_path}")
        
    except Exception as e:
        print(f"❌ Error al restaurar backup: {e}")

def main():
    print("="*80)
    print("♻️  RESTAURAR BACKUP DE BASE DE DATOS")
    print("="*80)
    
    backups = listar_backups_disponibles()
    
    if not backups:
        return
    
    print("\n" + "="*80)
    print("⚠️  ADVERTENCIA: Esto reemplazará la base de datos actual")
    print("   Se creará un backup de seguridad automáticamente")
    print("="*80)
    
    try:
        opcion = input("\nSelecciona el número del backup a restaurar (0 para cancelar): ")
        opcion = int(opcion)
        
        if opcion == 0:
            print("❌ Operación cancelada")
            return
        
        if 1 <= opcion <= len(backups):
            backup_seleccionado = backups[opcion - 1]
            confirmar = input(f"\n¿Confirmar restauración de '{backup_seleccionado.name}'? (s/n): ")
            
            if confirmar.lower() == 's':
                restaurar_backup(backup_seleccionado)
            else:
                print("❌ Operación cancelada")
        else:
            print("❌ Opción inválida")
            
    except ValueError:
        print("❌ Entrada inválida")
    except KeyboardInterrupt:
        print("\n❌ Operación cancelada")

if __name__ == "__main__":
    main()
