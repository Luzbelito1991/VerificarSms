# 🐋 Workflow de Docker para Múltiples Ordenadores

## 📋 Setup Inicial (Por Ordenador)

### 1. Instalar Docker Desktop
- **Windows**: https://www.docker.com/products/docker-desktop
- **Mac**: https://www.docker.com/products/docker-desktop
- **Linux**: `sudo apt install docker.io docker-compose`

### 2. Clonar el Repositorio
```bash
git clone <tu-repo-url>
cd VerificarSms
```

### 3. Configurar Variables de Entorno
```bash
# Copiar el archivo de ejemplo
cp .env.example .env

# Editar con tus valores
notepad .env  # Windows
nano .env     # Linux/Mac
```

### 4. Iniciar Todo con Docker
```bash
docker-compose up -d
```

¡Listo! La aplicación estará corriendo en http://localhost:8000

---

## 🚀 Comandos Diarios

### Iniciar el Proyecto
```bash
# Iniciar todos los servicios
docker-compose up -d

# Ver logs en tiempo real
docker-compose logs -f app

# Ver solo logs del servidor
docker-compose logs -f app
```

### Detener el Proyecto
```bash
# Detener sin borrar datos
docker-compose stop

# Detener y eliminar contenedores (mantiene base de datos)
docker-compose down

# Detener y eliminar TODO (incluye base de datos)
docker-compose down -v
```

### Verificar Estado
```bash
# Ver servicios corriendo
docker-compose ps

# Ver logs de todos los servicios
docker-compose logs

# Health check
curl http://localhost:8000/health
```

### Acceder al Contenedor
```bash
# Entrar al contenedor de la aplicación
docker-compose exec app bash

# Ejecutar comando directamente
docker-compose exec app python -c "print('Hello')"

# Ver base de datos
docker-compose exec postgres psql -U verificarsms -d verificarsms_db
```

### Actualizar Código
```bash
# 1. Hacer pull del repositorio
git pull origin main

# 2. Reconstruir la imagen
docker-compose build app

# 3. Reiniciar con nueva imagen
docker-compose up -d app
```

### Migraciones de Base de Datos
```bash
# Crear nuevas tablas
docker-compose exec app python -m backend.init_db

# Backup de base de datos
docker-compose exec postgres pg_dump -U verificarsms verificarsms_db > backup.sql

# Restaurar backup
docker-compose exec -T postgres psql -U verificarsms verificarsms_db < backup.sql
```

---

## 🔄 Workflow entre Ordenadores

### En Ordenador A (Hacer cambios)
```bash
# 1. Hacer tus cambios
# 2. Probar localmente
docker-compose up -d

# 3. Commit y push
git add .
git commit -m "Descripción del cambio"
git push origin main
```

### En Ordenador B o C (Recibir cambios)
```bash
# 1. Traer cambios
git pull origin main

# 2. Reconstruir si hay cambios en requirements.txt o Dockerfile
docker-compose build

# 3. Reiniciar servicios
docker-compose up -d

# 4. Ver logs para verificar
docker-compose logs -f app
```

---

## 🛠️ Desarrollo con Hot Reload

Para desarrollo con recarga automática de código:

```bash
# Usar docker-compose.override.yml (ya configurado)
docker-compose up -d

# Los cambios en archivos Python se recargan automáticamente
# Los cambios en templates HTML se aplican al refrescar el navegador
```

---

## 🐛 Solución de Problemas

### Puerto ya en uso
```bash
# Ver qué está usando el puerto 8000
netstat -ano | findstr :8000  # Windows
lsof -i :8000                 # Linux/Mac

# Detener servidor local
Get-Process | Where-Object { $_.ProcessName -in @("python", "uvicorn") } | Stop-Process -Force
```

### Contenedor no inicia
```bash
# Ver logs detallados
docker-compose logs app

# Reconstruir desde cero
docker-compose down -v
docker-compose build --no-cache
docker-compose up -d
```

### Base de datos corrupta
```bash
# Eliminar volumen y recrear
docker-compose down -v
docker-compose up -d
docker-compose exec app python -m backend.init_db
```

### Limpiar espacio
```bash
# Eliminar contenedores e imágenes no usadas
docker system prune -a

# Eliminar solo volúmenes huérfanos
docker volume prune
```

---

## 📊 Monitoreo

### Ver recursos utilizados
```bash
docker stats

# Solo del proyecto
docker stats $(docker-compose ps -q)
```

### Acceder a PostgreSQL
```bash
# Conectar a la base de datos
docker-compose exec postgres psql -U verificarsms -d verificarsms_db

# Consultas útiles
\dt                    # Ver tablas
\d+ usuarios          # Describir tabla
SELECT * FROM usuarios LIMIT 5;
\q                    # Salir
```

### Acceder a Redis
```bash
# Conectar a Redis
docker-compose exec redis redis-cli

# Comandos útiles
KEYS *                # Ver todas las keys
GET session:abc123    # Ver valor de una key
FLUSHALL              # Limpiar todo (¡cuidado!)
EXIT                  # Salir
```

---

## 🚀 Producción

### Variables de Entorno Críticas
```bash
# En .env de producción
DEBUG=false
SECRET_KEY=<generar-clave-aleatoria-segura>
DATABASE_URL=postgresql://user:pass@host:5432/db
REDIS_URL=redis://host:6379/0
CORS_ORIGINS=["https://tu-dominio.com"]
```

### Generar SECRET_KEY segura
```bash
docker-compose exec app python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### SSL/HTTPS (con Nginx)
Ver `docker-compose.prod.yml` para configuración con Nginx y Let's Encrypt.

---

## 📦 Comandos Útiles del Makefile

Si tienes `make` instalado:

```bash
make start        # Iniciar servicios
make stop         # Detener servicios
make restart      # Reiniciar servicios
make logs         # Ver logs
make shell        # Entrar al contenedor
make test         # Ejecutar tests
make migrate      # Inicializar BD
make clean        # Limpiar todo
```

---

## ✅ Checklist Diario

**Al iniciar el día:**
- [ ] `git pull origin main`
- [ ] `docker-compose up -d`
- [ ] Abrir http://localhost:8000
- [ ] Verificar logs: `docker-compose logs -f app`

**Al terminar:**
- [ ] `git add .`
- [ ] `git commit -m "Descripción"`
- [ ] `git push origin main`
- [ ] `docker-compose stop` (opcional si apagas el PC)

**Al cambiar de ordenador:**
- [ ] `git pull origin main`
- [ ] `docker-compose build` (si hay cambios en deps)
- [ ] `docker-compose up -d`

---

## 🆘 Soporte

- Logs de aplicación: `docker-compose logs app`
- Logs de PostgreSQL: `docker-compose logs postgres`
- Logs de Redis: `docker-compose logs redis`
- Health check: http://localhost:8000/health
- Docs API: http://localhost:8000/docs
