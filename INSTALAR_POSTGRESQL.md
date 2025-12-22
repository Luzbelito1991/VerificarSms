# 🐘 Instalación de PostgreSQL para Windows

**Fecha:** 22 de diciembre de 2025  
**Propósito:** Preparar PostgreSQL para migración desde SQLite

---

## 📥 PASO 1: Descargar PostgreSQL

### Opción A: PostgreSQL Oficial (RECOMENDADA)

1. **Ir al sitio oficial:**
   ```
   https://www.postgresql.org/download/windows/
   ```

2. **Descargar el instalador de EnterpriseDB:**
   - Versión recomendada: **PostgreSQL 16.x**
   - Hacer clic en "Download the installer"
   - Link directo: https://www.enterprisedb.com/downloads/postgres-postgresql-downloads
   - Descargar: `postgresql-16.x-windows-x64.exe` (aprox. 300 MB)

### Opción B: Chocolatey (Si tienes Chocolatey instalado)
```powershell
choco install postgresql
```

---

## 🔧 PASO 2: Instalación

### 2.1 Ejecutar Instalador
1. Hacer doble clic en `postgresql-16.x-windows-x64.exe`
2. Clic en "Next"

### 2.2 Directorio de Instalación
```
C:\Program Files\PostgreSQL\16
```
✅ Dejar por defecto, clic en "Next"

### 2.3 Componentes a Instalar
Seleccionar TODO:
- [x] PostgreSQL Server
- [x] pgAdmin 4 (interfaz gráfica)
- [x] Stack Builder
- [x] Command Line Tools

✅ Clic en "Next"

### 2.4 Directorio de Datos
```
C:\Program Files\PostgreSQL\16\data
```
✅ Dejar por defecto, clic en "Next"

### 2.5 **⚠️ IMPORTANTE: Contraseña de Superusuario**

Crear contraseña para el usuario `postgres`:

```
Contraseña: [ELIGE UNA CONTRASEÑA SEGURA]
Ejemplo: PostgresAdmin2025!
```

📝 **ANOTA ESTA CONTRASEÑA** - La vas a necesitar

✅ Clic en "Next"

### 2.6 Puerto
```
Puerto: 5432
```
✅ Dejar por defecto, clic en "Next"

### 2.7 Locale
```
Locale: Spanish, Argentina (o Default locale)
```
✅ Clic en "Next"

### 2.8 Resumen
- Revisar configuración
- Clic en "Next"

### 2.9 Instalación
- Esperar 5-10 minutos
- Desmarcar "Launch Stack Builder" al finalizar
- Clic en "Finish"

---

## ✅ PASO 3: Verificar Instalación

Abrir **PowerShell** como administrador:

```powershell
# Verificar que psql está instalado
& "C:\Program Files\PostgreSQL\16\bin\psql.exe" --version
```

Debería mostrar:
```
psql (PostgreSQL) 16.x
```

---

## 🗄️ PASO 4: Crear Base de Datos

### 4.1 Conectar a PostgreSQL

```powershell
# Agregar PostgreSQL al PATH temporalmente
$env:Path += ";C:\Program Files\PostgreSQL\16\bin"

# Conectar como superusuario
psql -U postgres
```

Te pedirá la contraseña que configuraste en el paso 2.5

### 4.2 Crear Base de Datos y Usuario

Una vez dentro de `psql`, ejecutar estos comandos **UNO POR UNO**:

```sql
-- Crear base de datos
CREATE DATABASE verificarsms;

-- Crear usuario
CREATE USER verificarsms_user WITH PASSWORD 'VerificarSMS2025!';

-- Dar permisos al usuario
GRANT ALL PRIVILEGES ON DATABASE verificarsms TO verificarsms_user;

-- Cambiar owner de la base de datos
ALTER DATABASE verificarsms OWNER TO verificarsms_user;

-- Verificar que se creó
\l
```

Deberías ver `verificarsms` en la lista de bases de datos.

### 4.3 Salir de psql

```sql
\q
```

---

## 🧪 PASO 5: Probar Conexión

### 5.1 Conectar con el usuario nuevo

```powershell
psql -U verificarsms_user -d verificarsms -h localhost
```

Contraseña: `VerificarSMS2025!`

### 5.2 Verificar que estás en la BD correcta

```sql
SELECT current_database();
```

Debería mostrar: `verificarsms`

### 5.3 Crear tabla de prueba

```sql
CREATE TABLE test_conexion (
    id SERIAL PRIMARY KEY,
    mensaje TEXT,
    fecha TIMESTAMP DEFAULT NOW()
);

INSERT INTO test_conexion (mensaje) VALUES ('PostgreSQL funcionando!');

SELECT * FROM test_conexion;
```

Si ves el registro, ¡todo funciona! ✅

### 5.4 Limpiar y salir

```sql
DROP TABLE test_conexion;
\q
```

---

## 📝 PASO 6: Guardar Configuración

### 6.1 Agregar PostgreSQL al PATH permanentemente

**PowerShell como Administrador:**

```powershell
$postgresPath = "C:\Program Files\PostgreSQL\16\bin"
[Environment]::SetEnvironmentVariable("Path", $env:Path + ";$postgresPath", [EnvironmentVariableTarget]::Machine)
```

Reiniciar PowerShell.

### 6.2 Crear archivo de configuración de conexión

**Crear archivo:** `F:\Proyectos Python\VerificarSms\postgres_config.txt`

```
Host: localhost
Puerto: 5432
Base de datos: verificarsms
Usuario: verificarsms_user
Contraseña: VerificarSMS2025!

Connection String:
postgresql://verificarsms_user:VerificarSMS2025!@localhost:5432/verificarsms
```

⚠️ **NO subir este archivo a git** (ya está en .gitignore como .txt)

---

## 🎯 PASO 7: Instalar Driver de Python

En tu entorno virtual:

```powershell
.\python-dotenv\Scripts\activate
pip install psycopg2-binary
```

---

## 🔍 PASO 8: Verificar con Python

Crear archivo temporal: `test_postgres.py`

```python
import psycopg2

try:
    conn = psycopg2.connect(
        host="localhost",
        port=5432,
        database="verificarsms",
        user="verificarsms_user",
        password="VerificarSMS2025!"
    )
    
    print("✅ Conexión exitosa a PostgreSQL!")
    
    cursor = conn.cursor()
    cursor.execute("SELECT version();")
    version = cursor.fetchone()[0]
    print(f"📊 Versión: {version}")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"❌ Error: {e}")
```

Ejecutar:
```powershell
python test_postgres.py
```

---

## 📊 RESUMEN

### ✅ Checklist de Instalación

- [ ] PostgreSQL 16 instalado
- [ ] Contraseña de superusuario anotada
- [ ] Base de datos `verificarsms` creada
- [ ] Usuario `verificarsms_user` creado
- [ ] Permisos otorgados
- [ ] Conexión probada con `psql`
- [ ] PostgreSQL agregado al PATH
- [ ] `psycopg2-binary` instalado en Python
- [ ] Test de conexión desde Python exitoso

### 📋 Datos de Conexión

```
Host: localhost
Puerto: 5432
Database: verificarsms
Usuario: verificarsms_user
Password: VerificarSMS2025!

Connection String:
postgresql://verificarsms_user:VerificarSMS2025!@localhost:5432/verificarsms
```

---

## 🚨 Solución de Problemas

### Error: "psql is not recognized"
```powershell
# Agregar al PATH manualmente
$env:Path += ";C:\Program Files\PostgreSQL\16\bin"
```

### Error: "FATAL: password authentication failed"
- Verificar que la contraseña sea correcta
- Revisar el archivo `pg_hba.conf`:
  ```
  C:\Program Files\PostgreSQL\16\data\pg_hba.conf
  ```
- Cambiar `md5` a `trust` temporalmente para testing

### Error: "could not connect to server"
- Verificar que el servicio esté corriendo:
  ```powershell
  Get-Service postgresql-x64-16
  ```
- Si está detenido:
  ```powershell
  Start-Service postgresql-x64-16
  ```

### Ver logs de PostgreSQL
```
C:\Program Files\PostgreSQL\16\data\log\
```

---

## 🎉 Siguiente Paso

Una vez completada la instalación, continuar con:
- **FASE0_MIGRACION.md** - Paso 3: Migrar esquema y datos

