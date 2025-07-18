import sqlite3

# Ruta a tu base actual con usuarios registrados
DATABASE_PATH = r"F:\Proyectos Python\VerificarSms\usuarios.db"

def agregar_usuario_id():
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    # Verificar si la columna ya existe
    cursor.execute("PRAGMA table_info(verificaciones)")
    columnas = [col[1] for col in cursor.fetchall()]

    if "usuario_id" not in columnas:
        cursor.execute("""
            ALTER TABLE verificaciones ADD COLUMN usuario_id INTEGER REFERENCES usuarios(id)
        """)
        print("✅ Columna 'usuario_id' agregada correctamente.")
    else:
        print("ℹ️ La columna 'usuario_id' ya existe.")

    conn.commit()
    conn.close()

if __name__ == "__main__":
    agregar_usuario_id()