# 🚀 Quick Start - Docker

Guía rápida para tener el proyecto corriendo en menos de 5 minutos.

## ⚡ Pasos Rápidos

### 1️⃣ Verificar Docker (30 segundos)

```bash
# Windows
.\check_docker.ps1

# Linux/Mac
bash check_docker.sh
```

### 2️⃣ Configurar Ambiente (1 minuto)

```bash
# Copiar archivo de configuración
cp .env.docker .env

# Generar SECRET_KEY única
python -c "import secrets; print(secrets.token_urlsafe(32))"
# Copiar el resultado en .env → SECRET_KEY=...
```

**Mínimo requerido en `.env`:**
```env
SECRET_KEY=tu-clave-secreta-generada-arriba
SMS_API_KEY=tu-api-key-de-sms
POSTGRES_PASSWORD=cambia-esta-contraseña
REDIS_PASSWORD=cambia-esta-contraseña-también
```

### 3️⃣ Levantar Servicios (2 minutos)

```bash
# Construir y levantar
docker-compose up -d

# Ver logs mientras inicia
docker-compose logs -f app
```

**Espera ver:**
```
✅ PostgreSQL está listo
✅ Base de datos inicializada
✅ Usuario admin creado
🚀 Ejecutando: uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

### 4️⃣ Acceder (10 segundos)

1. Abre: **http://localhost:8000**
2. Login:
   - Usuario: `admin`
   - Contraseña: `admin123`
3. **¡Listo!** 🎉

---

## 📝 Comandos Útiles

```bash
# Ver estado
docker-compose ps

# Ver logs
docker-compose logs -f app

# Detener
docker-compose down

# Reiniciar
docker-compose restart app

# Ver todos los comandos
make help  # Si tienes make instalado
```

---

## 🔧 Troubleshooting Rápido

### ❌ Error: "port is already allocated"

```bash
# Windows - Ver qué usa el puerto 8000
netstat -ano | findstr :8000
taskkill /PID <numero> /F

# Linux/Mac
lsof -i :8000
kill -9 <PID>

# O cambiar puerto en .env
echo "APP_PORT=8001" >> .env
docker-compose up -d
```

### ❌ Error: "No such file or directory: .env"

```bash
# Crear archivo .env
cp .env.docker .env
# Luego edita con tus valores
```

### ❌ PostgreSQL no inicia

```bash
# Ver logs detallados
docker-compose logs postgres

# Eliminar volumen y reintentar
docker-compose down -v
docker-compose up -d
```

### ❌ App no se conecta a base de datos

```bash
# Verificar que PostgreSQL esté healthy
docker-compose ps

# Debe mostrar: postgres (healthy)
# Si dice "starting", espera 30 segundos más
```

---

## 🎯 Siguientes Pasos

1. **Cambiar contraseña admin**
   - Login → Mantenimiento → Gestión de Usuarios
   - Editar usuario "admin" → Nueva contraseña

2. **Configurar SMS**
   - Edita `.env`
   - Configura `SMS_API_KEY=tu-clave`
   - Para testing: `SMS_MODO_SIMULADO=true`

3. **Crear más usuarios**
   - Mantenimiento → Gestión de Usuarios
   - Agregar operadores con sus sucursales

4. **Enviar primer SMS**
   - Ir a "Verificar SMS"
   - Ingresar datos del cliente
   - ¡Listo!

---

## 📚 Documentación Completa

- [DOCKER.md](DOCKER.md) - Guía completa de Docker
- [README.md](README.md) - Documentación general
- [GUIA_USO.md](GUIA_USO.md) - Manual de usuario

---

## 🆘 ¿Necesitas Ayuda?

```bash
# Verificar salud del sistema
docker-compose ps
curl http://localhost:8000/health

# Ver todos los logs
docker-compose logs

# Entrar al contenedor (debug avanzado)
docker-compose exec app bash
```

Si el problema persiste, revisa [DOCKER.md - Troubleshooting](DOCKER.md#troubleshooting)
