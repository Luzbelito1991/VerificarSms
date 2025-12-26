# 📱 VerificarSms

Sistema de verificación por SMS para "Los Quilmes S.A." - Envío de códigos de verificación a clientes con gestión de usuarios y control de acceso por roles.

## ✨ Características Principales

- ✅ **Envío de SMS** de verificación con códigos únicos
- ✅ **Gestión de usuarios** con roles (admin/operador)
- ✅ **Historial completo** de SMS enviados
- ✅ **Docker ready** - Despliegue con un comando
- ✅ **Rate Limiting** - Protección contra abuso y control de costos
- ✅ **PostgreSQL + Redis** - Base de datos y caché en producción
- ✅ **Recuperación de contraseñas** por email
- ✅ **Modo simulado** para testing sin gastar SMS

## 🚀 Instalación Rápida

### 🐋 Con Docker (Recomendado)

La forma más rápida y sencilla de ejecutar el proyecto en cualquier entorno:

```bash
# 1. Clonar el repositorio
git clone <url-del-repositorio>
cd VerificarSms

# 2. Configurar variables de entorno
cp .env.docker .env
# Edita .env con tus configuraciones

# 3. Levantar servicios
docker-compose up -d

# 4. Acceder a la aplicación
# http://localhost:8000
# Usuario: admin | Contraseña: admin123
```

**Ventajas:**
- ✅ Sin instalación de Python ni dependencias
- ✅ PostgreSQL y Redis incluidos
- ✅ Mismo entorno en desarrollo y producción
- ✅ Fácil de escalar y desplegar

📚 **Documentación completa**: Ver [DOCKER.md](DOCKER.md)

---

### 🐍 Instalación Local (Python)

#### Prerequisitos
- Python 3.8 o superior
- Git
- Node.js 16+ (opcional, para compilar CSS)

#### Configuración Automática

El proyecto incluye un script de instalación automática que configura todo lo necesario:

```bash
# 1. Clonar el repositorio
git clone <url-del-repositorio>
cd VerificarSms

# 2. Ejecutar script de instalación
python setup.py
```

El script automáticamente:
- ✅ Verifica la versión de Python
- ✅ Crea el entorno virtual
- ✅ Instala todas las dependencias
- ✅ Configura el archivo .env con una SECRET_KEY única
- ✅ Inicializa la base de datos PostgreSQL (si usas Docker)
- ✅ Crea el usuario administrador por defecto
- ✅ Compila el CSS de Tailwind

### Iniciar el Servidor

**Windows:**
```bash
# Activar entorno virtual
python-dotenv\Scripts\activate

# Iniciar servidor
uvicorn backend.main:app --reload
```

**Linux/Mac:**
```bash
# Activar entorno virtual
source python-dotenv/bin/activate

# Iniciar servidor
uvicorn backend.main:app --reload
```

Abre tu navegador en: **http://localhost:8000**

### Credenciales por Defecto

```
Usuario: admin
Contraseña: admin123
```

⚠️ **IMPORTANTE:** Cambia esta contraseña después del primer login desde el panel de gestión de usuarios.

---

## 📋 Instalación Manual (si prefieres hacerlo paso a paso)

### 1. Crear Entorno Virtual

```bash
python -m venv python-dotenv
```

### 2. Activar Entorno Virtual

**Windows:**
```bash
python-dotenv\Scripts\activate
```

**Linux/Mac:**
```bash
source python-dotenv/bin/activate
```

### 3. Instalar Dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar Variables de Entorno

```bash
# Copiar archivo de ejemplo
copy .env.example .env  # Windows
cp .env.example .env    # Linux/Mac
```

Edita el archivo `.env` y configura:
- `SECRET_KEY`: genera una clave segura (puedes usar un generador online)
- `SMS_API_KEY`: tu API key de SMS Masivos
- `SMS_MODO_SIMULADO`: `true` para pruebas (imprime en consola), `false` para envíos reales

### 5. Inicializar Base de Datos

```bash
python -m backend.init_db
```

Esto crea automáticamente:
- La base de datos `usuarios.db`
- Todas las tablas necesarias
- El usuario administrador por defecto

### 6. Compilar CSS (Opcional)

Si quieres modificar estilos:

```bash
npm install
npm run build     # Compilar una vez
npm run dev       # Compilar en modo watch (detecta cambios)
```

### 7. Iniciar Servidor

```bash
uvicorn backend.main:app --reload
```

---

## 🔧 Configuración

### Variables de Entorno Importantes

| Variable | Descripción | Valor por Defecto |
|----------|-------------|-------------------|
| `SECRET_KEY` | Clave para sesiones | (generada automáticamente) |
| `DATABASE_URL` | URL de conexión a BD PostgreSQL | `postgresql://admin:admin123@postgres:5432/verificarsms` |
| `SMS_API_KEY` | API Key de SMS Masivos | `tu-api-key-aqui` |
| `SMS_MODO_SIMULADO` | Modo prueba (true/false) | `true` |
| `DEBUG` | Modo debug | `true` |

---

## 🚨 Solución de Problemas

### Error: "No module named 'backend'"

```bash
# Asegúrate de estar en la raíz del proyecto y con el entorno activado
cd VerificarSms
python-dotenv\Scripts\activate  # Windows
python -c "import backend"      # Debe funcionar sin error
```

### Error: "SECRET_KEY not found"

```bash
# Verifica que existe .env en la raíz del proyecto
dir .env  # Windows
ls .env   # Linux/Mac

# Si no existe, cópialo del ejemplo
copy .env.example .env
```

### Error al Iniciar: "Address already in use"

Otro proceso está usando el puerto 8000:

```bash
# Usa otro puerto
uvicorn backend.main:app --reload --port 8001
```

### Base de Datos Corrupta o Falta

```bash
# Respaldar (si existe)
copy usuarios.db usuarios.db.backup

# Reinicializar
del usuarios.db
python -m backend.init_db
```

---

## 🔄 Actualización desde Git

Si clonas el repositorio en una nueva máquina o alguien actualiza el código:

```bash
# Actualizar código
git pull

# Ejecutar setup automático (configura todo)
python setup.py

# O manualmente:
# 1. Activar entorno (si no está activo)
python-dotenv\Scripts\activate

# 2. Actualizar dependencias (por si hubo cambios)
pip install -r requirements.txt

# 3. Verificar .env (si no existe, se crea de .env.example)
# 4. Verificar BD (si no existe, ejecutar: python -m backend.init_db)

# Iniciar servidor
uvicorn backend.main:app --reload
```

---

## 📚 Documentación Adicional

- [GUIA_USO.md](GUIA_USO.md) - Manual de usuario detallado
- [ESTRUCTURA.md](ESTRUCTURA.md) - Arquitectura técnica
- [INSTALACION_POSTGRES.md](INSTALACION_POSTGRES.md) - Migración a PostgreSQL
- [CONFIGURAR_EMAIL.md](CONFIGURAR_EMAIL.md) - Setup de recuperación de contraseñas

---

**Última actualización:** Diciembre 2025  
**Versión:** 2.0

