## 🚦 Rate Limiting - Guía Completa

Sistema de limitación de tasa para prevenir abuso, controlar costos de SMS y mejorar seguridad.

## 📋 Contenido
- [¿Qué es Rate Limiting?](#qué-es-rate-limiting)
- [Características](#características)
- [Configuración](#configuración)
- [Límites Configurados](#límites-configurados)
- [Uso](#uso)
- [Endpoints Admin](#endpoints-admin)
- [Troubleshooting](#troubleshooting)
- [Best Practices](#best-practices)

---

## ❓ ¿Qué es Rate Limiting?

Rate limiting **limita el número de requests** que un usuario/IP puede hacer en un período de tiempo.

### 🎯 Objetivos

1. **💰 Control de Costos** - Prevenir envío masivo de SMS (cada SMS cuesta dinero)
2. **🔐 Seguridad** - Proteger contra brute force en login
3. **⚡ Performance** - Prevenir abuso que sobrecargue el servidor
4. **🛡️ Protección** - Detectar y bloquear actividad sospechosa

---

## ✨ Características

### ✅ Lo que incluye

- ✅ **Redis backend** - Tracking distribuido entre múltiples instancias
- ✅ **Límites por endpoint** - Diferentes límites para diferentes acciones
- ✅ **Límites por rol** - Admins pueden hacer más requests que operadores
- ✅ **Límites múltiples** - Por minuto, hora y día simultáneamente
- ✅ **Whitelist/Blacklist** - IPs de confianza sin límite, IPs maliciosas bloqueadas
- ✅ **Mensajes informativos** - Indica cuánto esperar antes de reintentar
- ✅ **Panel admin** - Monitorear y gestionar límites en tiempo real
- ✅ **Headers HTTP** - Información de límites en cada response

---

## ⚙️ Configuración

### 1. Redis (Requerido)

Rate limiting requiere Redis. Si usas Docker, ya está configurado.

```yaml
# docker-compose.yml
redis:
  image: redis:7-alpine
  command: redis-server --requirepass ${REDIS_PASSWORD}
```

### 2. Variables de Entorno

```env
# .env
REDIS_URL=redis://:password@redis:6379/0
REDIS_PASSWORD=tu-password-segura
```

### 3. Verificar Conexión

```bash
# Ver estado de Redis
curl http://localhost:8000/admin/rate-limits/redis-status \
  -H "Cookie: session=..."
```

---

## 📊 Límites Configurados

Configurados en `backend/config/rate_limits.py`:

### 📱 SMS (Lo más crítico)

| Límite | Cantidad | Período | Descripción |
|--------|----------|---------|-------------|
| `sms_enviar` | 5 | 60s | 5 SMS por minuto |
| `sms_enviar_por_hora` | 30 | 3600s | 30 SMS por hora |
| `sms_enviar_por_dia` | 200 | 86400s | 200 SMS por día |

**Estos límites se aplican simultáneamente**. Si envías 5 SMS en 1 minuto, debes esperar ~1min para el siguiente, AUNQUE tengas cuota en la hora/día.

### 🔐 Autenticación

| Límite | Cantidad | Período | Descripción |
|--------|----------|---------|-------------|
| `login_intentos` | 5 | 300s | 5 intentos de login cada 5 min |
| `password_reset` | 3 | 3600s | 3 resets de password por hora |

### 🌐 API General

| Límite | Cantidad | Período | Descripción |
|--------|----------|---------|-------------|
| `api_general` | 100 | 60s | 100 requests por minuto |
| `consultas` | 30 | 60s | 30 consultas por minuto |

---

## 🎭 Límites por Rol

Los límites se multiplican según el rol del usuario:

```python
ROLE_MULTIPLIERS = {
    "admin": 3.0,      # Admins: 3x el límite base
    "operador": 1.0,   # Operadores: límite estándar
    "guest": 0.3,      # Invitados: 30% del límite
}
```

**Ejemplo**: 
- Límite base SMS: 5/minuto
- Admin: 15 SMS/minuto
- Operador: 5 SMS/minuto
- Guest: 1.5 SMS/minuto (~1-2 SMS/min)

---

## 🚀 Uso

### Para Usuarios Finales

#### Límite Alcanzado

Si ves un error 429:

```json
{
  "detail": {
    "ok": false,
    "mensaje": "Has alcanzado el límite de SMS permitidos. Límite: 5 por 60s. Intenta nuevamente en 45s.",
    "retry_after": 45,
    "retry_after_formatted": "45 segundos"
  }
}
```

**Solución**: Espera el tiempo indicado en `retry_after`.

#### Headers de Rate Limit

Cada response incluye headers informativos:

```http
X-RateLimit-Limit: 5
X-RateLimit-Remaining: 2
X-RateLimit-Reset: 1640000000
```

---

## 👨‍💼 Endpoints Admin

Solo accesibles para usuarios con rol `admin`.

### 1. Ver Configuración

```bash
GET /admin/rate-limits/config
```

**Response**:
```json
[
  {
    "endpoint": "sms_enviar",
    "limit": 5,
    "period": 60,
    "description": "Envío de SMS de verificación"
  },
  ...
]
```

### 2. Ver Límites Activos

```bash
GET /admin/rate-limits/active
```

**Response**:
```json
{
  "ok": true,
  "total": 12,
  "limits": [
    {
      "key": "sms_enviar:user:operador1",
      "count": 3,
      "ttl": 45,
      "reset_in": "45 segundos"
    }
  ]
}
```

### 3. Ver Estado de Usuario/IP

```bash
GET /admin/rate-limits/status/{identifier}/{limit_key}

# Ejemplo:
GET /admin/rate-limits/status/user:admin/sms_enviar
```

### 4. Resetear Límite

```bash
POST /admin/rate-limits/reset
Content-Type: application/json

{
  "identifier": "user:operador1",
  "limit_key": "sms_enviar"
}
```

**Uso**: Liberar límite si fue un error o emergencia.

### 5. Limpiar Todos los Límites

```bash
DELETE /admin/rate-limits/clear-all
```

**⚠️ CUIDADO**: Elimina todos los contadores. Solo para testing o emergencias.

### 6. Estadísticas

```bash
GET /admin/rate-limits/stats
```

**Response**:
```json
{
  "ok": true,
  "total_active_limits": 25,
  "by_type": {
    "sms_enviar": {
      "count": 15,
      "total_requests": 67
    },
    "login_intentos": {
      "count": 10,
      "total_requests": 23
    }
  }
}
```

### 7. Estado de Redis

```bash
GET /admin/rate-limits/redis-status
```

**Response**:
```json
{
  "ok": true,
  "connected": true,
  "version": "7.0.12",
  "uptime_days": 5,
  "connected_clients": 3,
  "used_memory_human": "1.2M"
}
```

---

## 🛡️ Whitelist y Blacklist

### Whitelist (Sin límites)

IPs que no tienen rate limiting:

```python
# backend/config/rate_limits.py
WHITELIST_IPS = [
    "127.0.0.1",
    "localhost",
    "192.168.1.100",  # Agregar IPs de confianza
]
```

**Uso**: Servidores internos, monitoring, IPs de oficinas principales.

### Blacklist (Bloqueadas)

IPs completamente bloqueadas:

```python
BLACKLIST_IPS = [
    "203.0.113.45",  # IP maliciosa
    # Agregar IPs atacantes
]
```

**Error al acceder**:
```json
{
  "detail": "Tu IP ha sido bloqueada debido a actividad sospechosa."
}
```

---

## 🧪 Testing

### Ejecutar Tests

```bash
# Con pytest
pytest tests/test_rate_limiting.py -v

# O directamente
python tests/test_rate_limiting.py
```

### Test Manual

```bash
# Login
curl -X POST http://localhost:8000/login \
  -H "Content-Type: application/json" \
  -d '{"usuario":"admin","password":"admin123"}' \
  -c cookies.txt

# Enviar 6 SMS rápidamente (el 6to debería fallar)
for i in {1..6}; do
  echo "SMS $i"
  curl -X POST http://localhost:8000/send-sms \
    -H "Content-Type: application/json" \
    -b cookies.txt \
    -d '{
      "personId":"12345678",
      "phoneNumber":"1234567890",
      "merchantCode":"776"
    }'
  echo ""
done
```

---

## 🐛 Troubleshooting

### ❌ Redis no disponible

**Error**:
```json
{
  "detail": "Redis no disponible. Rate limiting deshabilitado."
}
```

**Solución**:
```bash
# Verificar Redis
docker-compose ps redis

# Ver logs
docker-compose logs redis

# Reiniciar
docker-compose restart redis

# Verificar conexión
docker-compose exec redis redis-cli -a <password> PING
```

### ❌ Rate limit demasiado estricto

**Solución 1**: Aumentar límite en configuración

```python
# backend/config/rate_limits.py
"sms_enviar": RateLimitConfig(
    limit=10,  # Cambiar de 5 a 10
    period=60,
    description="Envío de SMS de verificación"
),
```

**Solución 2**: Agregar IP a whitelist

```python
WHITELIST_IPS = [
    "192.168.1.50",  # IP del usuario
]
```

**Solución 3**: Resetear límite manualmente

```bash
curl -X POST http://localhost:8000/admin/rate-limits/reset \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{
    "identifier": "user:operador1",
    "limit_key": "sms_enviar"
  }'
```

### ❌ Usuario bloqueado injustamente

```bash
# Ver estado actual
curl http://localhost:8000/admin/rate-limits/status/user:operador1/sms_enviar \
  -b cookies.txt

# Resetear límite
curl -X POST http://localhost:8000/admin/rate-limits/reset \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{"identifier":"user:operador1","limit_key":"sms_enviar"}'
```

### ⚠️ Rate limiting no funciona

1. **Verificar Redis**:
   ```bash
   curl http://localhost:8000/admin/rate-limits/redis-status -b cookies.txt
   ```

2. **Ver logs de la app**:
   ```bash
   docker-compose logs app | grep -i "rate\|redis\|limit"
   ```

3. **Verificar variable de entorno**:
   ```bash
   docker-compose exec app printenv | grep REDIS
   ```

---

## 💡 Best Practices

### 1. Configuración por Ambiente

```python
# Desarrollo - Límites relajados
if settings.ENVIRONMENT == "development":
    RATE_LIMITS["sms_enviar"].limit = 100  # Sin límite real

# Producción - Límites estrictos
elif settings.ENVIRONMENT == "production":
    RATE_LIMITS["sms_enviar"].limit = 5
```

### 2. Monitoring

Monitorear rate limits alcanzados:

```bash
# Ver estadísticas regularmente
curl http://localhost:8000/admin/rate-limits/stats -b cookies.txt
```

### 3. Alertas

Configurar alertas si muchos usuarios alcanzan límites:

```python
if stats["by_type"]["sms_enviar"]["count"] > 50:
    send_alert("Muchos usuarios alcanzando límite de SMS")
```

### 4. Ajuste Gradual

- Empezar con límites conservadores
- Monitorear por 1-2 semanas
- Ajustar según datos reales

### 5. Comunicación a Usuarios

Informar límites en la UI:

```html
<div class="info">
  ℹ️ Límite: 5 SMS por minuto, 30 por hora
</div>
```

---

## 📈 Casos de Uso

### Caso 1: Prevenir Spam de SMS

**Problema**: Usuario intenta enviar 100 SMS en 1 minuto.

**Solución**: Rate limiting detiene después del 5to SMS.

**Resultado**: Se ahorran 95 SMS = $X de costo evitado.

### Caso 2: Protección Brute Force

**Problema**: Atacante intenta 1000 contraseñas en el login.

**Solución**: Se bloquea después de 5 intentos por 5 minutos.

**Resultado**: Login protegido contra ataques automatizados.

### Caso 3: Sobrecarga del Sistema

**Problema**: Bot realiza 10,000 requests/segundo.

**Solución**: Rate limit general de 100/minuto lo detiene.

**Resultado**: Servidor protegido de DoS.

---

## 🔧 Personalización

### Agregar Nuevo Límite

```python
# backend/config/rate_limits.py
RATE_LIMITS["mi_endpoint"] = RateLimitConfig(
    limit=10,
    period=60,
    description="Mi endpoint personalizado"
)
```

### Usar en Endpoint

```python
# backend/routes/mi_ruta.py
from backend.middleware.rate_limiting import limiter
from backend.config.rate_limits import get_rate_limit_string

@router.post("/mi-endpoint")
@limiter.limit(get_rate_limit_string("mi_endpoint"))
def mi_funcion(request: Request):
    pass
```

---

## 📚 Referencias

- [slowapi Documentation](https://slowapi.readthedocs.io/)
- [Redis Rate Limiting](https://redis.io/docs/reference/patterns/rate-limiter/)
- [HTTP 429 Status Code](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/429)

---

## ✅ Checklist de Implementación

- [x] Redis configurado y corriendo
- [x] Variables de entorno configuradas
- [x] Límites definidos en rate_limits.py
- [x] Middleware integrado en main.py
- [x] Endpoints protegidos (SMS, login, etc)
- [x] Panel admin funcional
- [x] Tests ejecutados
- [x] Whitelist configurada si necesario
- [x] Documentación leída por el equipo
- [ ] Monitoring configurado
- [ ] Alertas configuradas
- [ ] Usuarios informados de límites

---

**Implementado**: 24 de Diciembre, 2025  
**Estado**: ✅ Completo y funcional  
**Próximo paso**: Logging estructurado
