# 🐋 Guía Docker - VerificarSms

## 📋 Contenido
- [Requisitos Previos](#requisitos-previos)
- [Inicio Rápido](#inicio-rápido)
- [Configuración Detallada](#configuración-detallada)
- [Comandos Útiles](#comandos-útiles)
- [Desarrollo con Docker](#desarrollo-con-docker)
- [Producción](#producción)
- [Troubleshooting](#troubleshooting)

---

## 🔧 Requisitos Previos

### Instalar Docker Desktop
- **Windows/Mac**: [Docker Desktop](https://www.docker.com/products/docker-desktop)
- **Linux**: Docker Engine + Docker Compose

```bash
# Verificar instalación
docker --version
docker-compose --version
```

---

## 🚀 Inicio Rápido

### 1. Configurar variables de entorno

```bash
# Copiar archivo de ejemplo
cp .env.docker .env

# Editar .env y configurar:
# - SECRET_KEY (generar una nueva)
# - SMS_API_KEY
# - Contraseñas de PostgreSQL y Redis
# - Configuración SMTP (opcional)
```

### 2. Generar SECRET_KEY única

```bash
# En Windows PowerShell
python -c "import secrets; print(secrets.token_urlsafe(32))"

# O en Python
python
>>> import secrets
>>> secrets.token_urlsafe(32)
```

### 3. Levantar servicios

```bash
# Construir y levantar todos los servicios
docker-compose up -d

# Ver logs
docker-compose logs -f app
```

### 4. Acceder a la aplicación

- **Web**: http://localhost:8000
- **Usuario**: `admin`
- **Contraseña**: `admin123` (cámbiala inmediatamente)

---

## ⚙️ Configuración Detallada

### Estructura de Servicios

```yaml
📦 docker-compose.yml
├── 🐘 postgres    (Base de datos PostgreSQL 15)
├── 🔴 redis       (Caché y sesiones)
├── 🚀 app         (FastAPI application)
└── 🎨 tailwind    (CSS builder - solo desarrollo)
```

### Variables de Entorno Importantes

#### Base de Datos
```env
POSTGRES_DB=verificarsms
POSTGRES_USER=admin
POSTGRES_PASSWORD=tu-password-segura
DATABASE_URL=postgresql://admin:password@postgres:5432/verificarsms
```

#### Redis
```env
REDIS_PASSWORD=tu-redis-password
REDIS_URL=redis://:password@redis:6379/0
```

#### Aplicación
```env
SECRET_KEY=clave-secreta-unica-y-segura
DEBUG=false
ENVIRONMENT=production
APP_PORT=8000
```

#### SMS API
```env
SMS_API_KEY=tu-api-key
SMS_MODO_SIMULADO=false  # true para testing
```

#### Email (opcional)
```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=tu-email@gmail.com
SMTP_PASSWORD=tu-app-password
```

---

## 📝 Comandos Útiles

### Gestión de Contenedores

```bash
# Levantar servicios
docker-compose up -d

# Levantar con rebuild
docker-compose up -d --build

# Detener servicios
docker-compose down

# Detener y eliminar volúmenes (⚠️ elimina datos)
docker-compose down -v

# Ver logs
docker-compose logs -f
docker-compose logs -f app
docker-compose logs -f postgres

# Ver estado
docker-compose ps

# Reiniciar un servicio
docker-compose restart app
```

### Acceso a Contenedores

```bash
# Shell en el contenedor de la app
docker-compose exec app bash

# Shell en PostgreSQL
docker-compose exec postgres psql -U admin -d verificarsms

# Shell en Redis
docker-compose exec redis redis-cli -a <REDIS_PASSWORD>
```

### Base de Datos

```bash
# Crear backup
docker-compose exec postgres pg_dump -U admin verificarsms > backup.sql

# Restaurar backup
docker-compose exec -T postgres psql -U admin -d verificarsms < backup.sql

# Ver tablas
docker-compose exec postgres psql -U admin -d verificarsms -c "\dt"

# Conectar con cliente SQL
docker-compose exec postgres psql -U admin -d verificarsms
```

### Limpieza

```bash
# Eliminar contenedores detenidos
docker-compose down

# Eliminar imágenes no usadas
docker image prune -a

# Eliminar todo (⚠️ cuidado)
docker system prune -a --volumes
```

---

## 🔧 Desarrollo con Docker

### Modo Desarrollo

Para desarrollo con hot-reload y Tailwind CSS:

```bash
# Levantar con perfil de desarrollo
docker-compose --profile dev up -d

# Esto inicia:
# - PostgreSQL
# - Redis
# - FastAPI con auto-reload
# - Tailwind CSS en modo watch
```

### Volúmenes en Desarrollo

Puedes montar código local para hot-reload:

```yaml
# En docker-compose.override.yml
version: '3.8'
services:
  app:
    volumes:
      - ./backend:/app/backend
      - ./templates:/app/templates
      - ./static:/app/static
    environment:
      DEBUG: "true"
    command: uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

```bash
# Usar override
docker-compose -f docker-compose.yml -f docker-compose.override.yml up -d
```

### Ejecutar Tests

```bash
# Ejecutar tests en el contenedor
docker-compose exec app pytest

# Con coverage
docker-compose exec app pytest --cov=backend --cov-report=html
```

---

## 🏭 Producción

### Checklist de Seguridad

- [ ] Cambiar `SECRET_KEY` a valor único y seguro
- [ ] Cambiar contraseñas de PostgreSQL y Redis
- [ ] Cambiar contraseña del usuario `admin`
- [ ] Configurar `DEBUG=false`
- [ ] Configurar `ENVIRONMENT=production`
- [ ] Configurar CORS correctamente
- [ ] Habilitar HTTPS (usar Nginx reverse proxy)
- [ ] Configurar backups automáticos
- [ ] Configurar monitoring y logs

### Ejemplo con Nginx Reverse Proxy

```yaml
# docker-compose.prod.yml
version: '3.8'
services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - app
    networks:
      - verificarsms-network
```

```nginx
# nginx.conf
server {
    listen 80;
    server_name tu-dominio.com;
    
    location / {
        proxy_pass http://app:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

### Backups Automáticos

```bash
# Crear script de backup (backup.sh)
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
docker-compose exec -T postgres pg_dump -U admin verificarsms > backups/backup_$DATE.sql
find backups/ -name "*.sql" -mtime +7 -delete  # Eliminar backups de más de 7 días
```

```bash
# Agregar a crontab (Linux)
0 2 * * * /path/to/backup.sh  # Backup diario a las 2 AM
```

### Logging Centralizado

```yaml
# En docker-compose.prod.yml
services:
  app:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

---

## 🐛 Troubleshooting

### La app no se conecta a PostgreSQL

```bash
# Verificar que PostgreSQL esté listo
docker-compose logs postgres

# Ver health check
docker-compose ps

# Probar conexión manual
docker-compose exec app python -c "
from backend.config import engine
engine.connect()
print('✅ Conexión exitosa')
"
```

### Errores de permisos

```bash
# Asegurarse que el entrypoint sea ejecutable
chmod +x docker-entrypoint.sh

# Reconstruir imagen
docker-compose build --no-cache app
```

### Puerto 8000 ya en uso

```bash
# Cambiar puerto en .env
APP_PORT=8001

# O detener el servicio que usa el puerto
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux
lsof -i :8000
kill -9 <PID>
```

### Volúmenes con datos antiguos

```bash
# Eliminar volúmenes y empezar de cero
docker-compose down -v
docker-compose up -d
```

### Ver logs detallados

```bash
# Logs de todos los servicios
docker-compose logs -f

# Solo un servicio
docker-compose logs -f app

# Últimas N líneas
docker-compose logs --tail=100 app
```

### Reiniciar servicios

```bash
# Reiniciar todo
docker-compose restart

# Solo un servicio
docker-compose restart app

# Forzar recreación
docker-compose up -d --force-recreate app
```

---

## 🔍 Health Checks

### Verificar estado de servicios

```bash
# Ver health status
docker-compose ps

# Probar endpoint de salud
curl http://localhost:8000/health

# Ver detalles
docker inspect verificarsms-app | grep -A 10 Health
```

---

## 📊 Monitoring

### Ver uso de recursos

```bash
# Stats en tiempo real
docker stats

# Uso de un contenedor específico
docker stats verificarsms-app
```

### Logs estructurados

Los logs de la aplicación están en formato JSON para fácil parsing:

```bash
# Ver logs y filtrar
docker-compose logs app | grep ERROR
docker-compose logs app | grep "sms_sent"
```

---

## 🚀 Comandos Avanzados

### Escalar servicios

```bash
# Múltiples instancias de la app (requiere load balancer)
docker-compose up -d --scale app=3
```

### Ejecutar comandos en contenedores

```bash
# Ejecutar script Python
docker-compose exec app python -m backend.scripts.agregar_email

# Ejecutar shell script
docker-compose exec app bash -c "ls -la /app"

# Como usuario root (para instalar paquetes)
docker-compose exec --user root app bash
```

### Inspeccionar red

```bash
# Ver redes
docker network ls

# Inspeccionar red del proyecto
docker network inspect verificarsms_verificarsms-network
```

---

## 📚 Recursos Adicionales

- [Documentación oficial Docker](https://docs.docker.com/)
- [Documentación Docker Compose](https://docs.docker.com/compose/)
- [Best Practices Dockerfile](https://docs.docker.com/develop/develop-images/dockerfile_best-practices/)
- [FastAPI en Docker](https://fastapi.tiangolo.com/deployment/docker/)

---

## 💡 Tips y Mejores Prácticas

1. **Siempre usar `.env` para configuración** - No hardcodear valores
2. **Generar SECRET_KEY única** - Nunca usar la de ejemplo
3. **Backups regulares** - Automatizar con cron
4. **Monitoring** - Configurar alertas para servicios críticos
5. **HTTPS en producción** - Usar Nginx + Let's Encrypt
6. **Logs rotativos** - Configurar max-size para no llenar disco
7. **Health checks** - Permiten que Docker reinicie servicios caídos
8. **Named volumes** - Para persistencia de datos importante
9. **Multi-stage builds** - Mantiene imágenes pequeñas
10. **Usuario no-root** - Mejor seguridad en contenedores
