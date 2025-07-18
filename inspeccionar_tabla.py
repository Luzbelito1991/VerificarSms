import sqlite3

conn = sqlite3.connect("usuarios.db")
cursor = conn.cursor()

cursor.execute("PRAGMA table_info(verificaciones)")
columnas = cursor.fetchall()

print("📋 Estructura de la tabla 'verificaciones':")
for col in columnas:
    cid, nombre, tipo, notnull, default, pk = col
    print(f"- {nombre} ({tipo}) | NOT NULL: {bool(notnull)} | PK: {bool(pk)}")

conn.close()