# 🚀 Instalación de Redis para Windows

## Opción 1: Memurai (Recomendado)

### Descargar
1. Ir a: https://www.memurai.com/get-memurai
2. Descargar: **Memurai Developer** (gratis)
3. Instalar con opciones por defecto

### Configuración
- **Puerto:** 6379 (estándar)
- **Servicio:** Se instala como servicio de Windows
- **Password:** (opcional, lo configuraremos después)

## Opción 2: Redis Stack (Alternativa)

### Descargar
1. Ir a: https://redis.io/download
2. Descargar: **Redis Stack for Windows**
3. O usar WSL2: `wsl sudo apt install redis-server`

## Verificar Instalación

### Desde PowerShell:
```powershell
# Verificar servicio
Get-Service *redis* -or Get-Service *memurai*

# Debería mostrar:
Status   Name           DisplayName
------   ----           -----------
Running  Memurai        Memurai
```

### Desde terminal Redis:
```bash
redis-cli ping
# Respuesta: PONG
```

## Próximos Pasos Después de Instalar

1. Instalar paquetes Python: `redis`, `aioredis`
2. Configurar connection string en `.env`
3. Actualizar SessionMiddleware para usar Redis
4. Probar conexión con test_redis.py

---

**Nota:** Una vez instalado, vuelve y te ayudo con la configuración en FastAPI.
