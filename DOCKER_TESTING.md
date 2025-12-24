# 🧪 Testing de Implementación Docker

Guía para verificar que la implementación Docker funciona correctamente.

## 📋 Pre-requisitos

```bash
# Verificar que Docker esté instalado
docker --version
docker-compose --version

# Ejecutar script de verificación (opcional)
# Windows
.\check_docker.ps1

# Linux/Mac
bash check_docker.sh
```

---

## ✅ Test 1: Archivos Creados

Verificar que todos los archivos Docker existen:

```bash
ls -la Dockerfile
ls -la docker-compose.yml
ls -la .dockerignore
ls -la docker-entrypoint.sh
ls -la .env.docker
ls -la Makefile
```

**Resultado esperado**: Todos los archivos existen ✅

---

## ✅ Test 2: Configuración Básica

```bash
# Crear archivo .env
cp .env.docker .env

# Verificar que se creó
cat .env | head -20
```

**Resultado esperado**: Archivo .env creado con configuraciones ✅

---

## ✅ Test 3: Build de Imágenes

```bash
# Construir imágenes (primera vez puede tardar 5-10 min)
docker-compose build

# O con Makefile
make build
```

**Resultado esperado**:
```
Building app
Step 1/15 : FROM python:3.11-slim as base
...
Successfully built <image-id>
Successfully tagged verificarsms_app:latest
```

---

## ✅ Test 4: Levantar Servicios

```bash
# Levantar todos los servicios
docker-compose up -d

# Verificar que están corriendo
docker-compose ps
```

**Resultado esperado**:
```
NAME                    STATUS        PORTS
verificarsms-app        Up (healthy)  0.0.0.0:8000->8000/tcp
verificarsms-postgres   Up (healthy)  0.0.0.0:5432->5432/tcp
verificarsms-redis      Up (healthy)  0.0.0.0:6379->6379/tcp
```

---

## ✅ Test 5: Logs de Inicialización

```bash
# Ver logs de la aplicación
docker-compose logs app
```

**Resultado esperado**:
```
🚀 Iniciando VerificarSms...
⏳ Esperando a que PostgreSQL esté listo...
   Host: postgres
   Port: 5432
✅ PostgreSQL está listo
📊 Inicializando base de datos...
✅ Base de datos inicializada
👤 Verificando usuario administrador...
✅ Usuario admin creado (usuario: admin, contraseña: admin123)
⚠️  IMPORTANTE: Cambia esta contraseña después del primer login
🔧 Configuración del entorno:
   DEBUG: false
   ENVIRONMENT: production
   SMS_MODO_SIMULADO: false
🎉 Inicialización completada
🚀 Ejecutando: uvicorn backend.main:app --host 0.0.0.0 --port 8000
INFO:     Started server process [1]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

---

## ✅ Test 6: Health Check

```bash
# Verificar endpoint de salud
curl http://localhost:8000/health

# O con navegador
# http://localhost:8000/health
```

**Resultado esperado**:
```json
{
  "status": "healthy",
  "service": "VerificarSms API",
  "version": "2.0.0",
  "database": "connected"
}
```

---

## ✅ Test 7: Acceso Web

```bash
# Abrir en navegador
start http://localhost:8000  # Windows
open http://localhost:8000   # Mac
xdg-open http://localhost:8000  # Linux
```

**Resultado esperado**:
- ✅ Página de login se muestra
- ✅ CSS cargado correctamente
- ✅ Sin errores en consola del navegador

---

## ✅ Test 8: Login

En el navegador:

1. Usuario: `admin`
2. Contraseña: `admin123`
3. Click en "Iniciar Sesión"

**Resultado esperado**:
- ✅ Login exitoso
- ✅ Redirige a home/dashboard
- ✅ Menú lateral visible

---

## ✅ Test 9: Base de Datos PostgreSQL

```bash
# Conectar a PostgreSQL
docker-compose exec postgres psql -U admin -d verificarsms

# Dentro de psql, ejecutar:
\dt
# Debe mostrar tablas: usuarios, verificaciones, password_reset_tokens, sucursales

SELECT usuario, rol FROM usuarios;
# Debe mostrar: admin | admin

\q
```

**Resultado esperado**: Tablas creadas y usuario admin existe ✅

---

## ✅ Test 10: Redis

```bash
# Conectar a Redis
docker-compose exec redis redis-cli -a <REDIS_PASSWORD>

# Dentro de redis-cli:
PING
# Debe responder: PONG

KEYS *
# Puede estar vacío o con algunas keys de sesión

EXIT
```

**Resultado esperado**: Redis responde correctamente ✅

---

## ✅ Test 11: Hot Reload (Desarrollo)

Si usas `docker-compose.override.yml`:

```bash
# Editar un archivo
echo "# Test change" >> backend/main.py

# Ver logs
docker-compose logs -f app
```

**Resultado esperado**:
```
INFO:     Detected file change in 'backend/main.py'
INFO:     Reloading...
INFO:     Application startup complete.
```

---

## ✅ Test 12: Makefile (si aplica)

```bash
# Probar comandos del Makefile
make help        # Ver ayuda
make status      # Ver estado
make health      # Check de salud
make logs-app    # Ver logs de app
```

**Resultado esperado**: Todos los comandos funcionan ✅

---

## ✅ Test 13: Envío de SMS (Modo Simulado)

1. Login en la app
2. Ir a "Verificar SMS"
3. Llenar formulario:
   - DNI: 12345678
   - Teléfono: 1234567890
   - Comercio: 776
   - Monto: 1000
4. Enviar

**Ver logs**:
```bash
docker-compose logs -f app
```

**Resultado esperado** (con SMS_MODO_SIMULADO=true):
```
📱 [MODO SIMULADO] SMS enviado a 1234567890
Mensaje: Tu codigo de verificacion es: 1234
```

---

## ✅ Test 14: Backups

```bash
# Crear backup
docker-compose exec -T postgres pg_dump -U admin verificarsms > test_backup.sql

# Verificar que se creó
ls -lh test_backup.sql

# Debe tener contenido
head -20 test_backup.sql
```

**Resultado esperado**: Backup creado exitosamente ✅

---

## ✅ Test 15: Restart y Persistencia

```bash
# Detener servicios
docker-compose down

# Levantar de nuevo
docker-compose up -d

# Verificar que datos persisten
curl http://localhost:8000/health

# Login con admin/admin123 debe funcionar
```

**Resultado esperado**: Datos persisten después de restart ✅

---

## 🧹 Limpieza Después de Tests

```bash
# Detener servicios
docker-compose down

# Eliminar volúmenes (opcional - borra datos)
docker-compose down -v

# Eliminar imágenes (opcional)
docker image prune -f

# Eliminar archivo de test
rm test_backup.sql
```

---

## 🐛 Troubleshooting

### Puerto 8000 ocupado

```bash
# Ver qué usa el puerto
netstat -ano | findstr :8000  # Windows
lsof -i :8000                 # Linux/Mac

# Cambiar puerto en .env
echo "APP_PORT=8001" >> .env
docker-compose up -d
```

### PostgreSQL no inicia

```bash
# Ver logs detallados
docker-compose logs postgres

# Reiniciar servicio
docker-compose restart postgres

# Reset completo
docker-compose down -v
docker-compose up -d
```

### App no se conecta a BD

```bash
# Verificar que PostgreSQL está healthy
docker-compose ps

# Debe mostrar: (healthy)
# Si dice "starting", esperar 30 segundos

# Ver logs de conexión
docker-compose logs app | grep -i "database\|postgres\|connection"
```

### Health check falla

```bash
# Ver detalles del health check
docker inspect verificarsms-app | grep -A 20 Health

# Probar manualmente
docker-compose exec app python -c "
from backend.config import engine
try:
    engine.connect()
    print('✅ Conexión exitosa')
except Exception as e:
    print(f'❌ Error: {e}')
"
```

---

## ✅ Checklist Final

Después de todos los tests:

- [ ] Archivos Docker creados
- [ ] .env configurado
- [ ] Imágenes construidas
- [ ] Servicios corriendo (healthy)
- [ ] Logs sin errores
- [ ] Health check responde
- [ ] Página web accesible
- [ ] Login funciona
- [ ] PostgreSQL conectado
- [ ] Redis funciona
- [ ] Hot reload funciona (dev)
- [ ] Makefile funciona
- [ ] SMS simulado funciona
- [ ] Backups funcionan
- [ ] Persistencia funciona

---

## 🎉 Resultado

Si todos los tests pasan:

```
✅ Implementación Docker EXITOSA
✅ Proyecto listo para desarrollo
✅ Proyecto listo para producción (con config apropiada)
```

Si algún test falla, consulta:
1. Logs: `docker-compose logs -f`
2. DOCKER.md - Sección Troubleshooting
3. DOCKER_QUICKSTART.md - Problemas comunes

---

**Fecha**: 24 de Diciembre, 2025  
**Estado**: ✅ Listo para testing
