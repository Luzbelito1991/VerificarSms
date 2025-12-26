"""Script para insertar sucursales en la base de datos"""
import sqlite3

def insertar_sucursales():
    conn = sqlite3.connect('usuarios.db')
    cursor = conn.cursor()
    
    sucursales = {
        "389": "Los Quilmes - Casa Central",
        "561": "Los Quilmes - Sucursal Centro",
        "776": "Limite Deportes Alberdi",
        "777": "Limite Deportes Lules",
        "778": "Limite Deportes Famaillá",
        "779": "Limite Deportes Alderetes",
        "781": "Limite Deportes Banda de Río Salí"
    }
    
    try:
        # Verificar cuántas existen
        cursor.execute("SELECT COUNT(*) FROM sucursales")
        total_antes = cursor.fetchone()[0]
        print(f"Sucursales antes: {total_antes}")
        
        # Insertar sucursales
        for codigo, nombre in sucursales.items():
            try:
                cursor.execute(
                    "INSERT INTO sucursales (codigo, nombre) VALUES (?, ?)",
                    (codigo, nombre)
                )
                print(f"✓ Insertada: {codigo} - {nombre}")
            except sqlite3.IntegrityError:
                print(f"⚠️  Ya existe: {codigo} - {nombre}")
        
        conn.commit()
        
        # Verificar resultado
        cursor.execute("SELECT codigo, nombre FROM sucursales ORDER BY codigo")
        print("\n📋 Sucursales en la base de datos:")
        for row in cursor.fetchall():
            print(f"  - {row[0]}: {row[1]}")
        
        cursor.execute("SELECT COUNT(*) FROM sucursales")
        total_despues = cursor.fetchone()[0]
        print(f"\n✅ Total de sucursales: {total_despues}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    insertar_sucursales()
