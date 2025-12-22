# 🚀 FASE 0: Migración a Multi-Usuario

**Fecha inicio:** 22 de diciembre de 2025  
**Estado actual:** Backup completo realizado ✅  
**Commit de respaldo:** d2f2b26

---

## 📋 CHECKLIST DE MIGRACIÓN

### **Paso 1: Preparación (15 min)** ✅ COMPLETADO
- [x] Backup de base de datos SQLite
- [x] Commit en git de estado actual
- [x] Backup completo del proyecto
- [x] Documentar configuración actual
- [x] Exportar datos de SQLite a JSON (por seguridad)

### **Paso 2: Instalar PostgreSQL (30 min)** ✅ COMPLETADO
- [x] Descargar PostgreSQL para Windows
- [x] Instalar PostgreSQL
- [x] Crear base de datos `verificarsms`
- [x] Crear usuario `verificarsms_user`
- [x] Probar conexión

### **Paso 3: Migrar Esquema y Datos (45 min)** ✅ COMPLETADO
- [x] Instalar `psycopg2-binary` y `alembic`
- [x] Crear script de migración de datos
- [x] Ejecutar migración SQLite → PostgreSQL
- [x] Verificar integridad de datos
- [x] Probar aplicación con PostgreSQL

### **Paso 4: Redis para Sesiones (30 min)** ✅ COMPLETADO
- [x] Instalar Redis (Memurai para Windows)
- [x] Instalar `redis` y `fastapi-sessions`
- [x] Configurar SessionMiddleware con Redis
- [x] Probar login y persistencia de sesiones

### **Paso 5: Sistema de Auditoría (60 min)**
- [ ] Crear modelo `LogAuditoria`
- [ ] Crear middleware de auditoría
- [ ] Registrar acciones críticas
- [ ] Crear endpoint para consultar logs
- [ ] Crear vista admin de logs

### **Paso 6: Panel de Sesiones Activas (45 min)**
- [ ] Crear modelo `SesionActiva`
- [ ] Registrar sesiones en login
- [ ] Actualizar última actividad
- [ ] Crear endpoint de sesiones activas
- [ ] Crear vista admin de sesiones

### **Paso 7: Testing Final (30 min)**
- [ ] Probar login simultáneo desde 2 PCs
- [ ] Probar envío de SMS concurrente
- [ ] Verificar logs de auditoría
- [ ] Verificar sesiones activas
- [ ] Probar backup/restore con PostgreSQL

### **Paso 8: Configuración de Red Local (30 min)**
- [ ] Cambiar `--host` a `0.0.0.0`
- [ ] Configurar firewall
- [ ] Probar acceso desde otro PC
- [ ] Documentar IP del servidor

---

## 🔄 PLAN DE ROLLBACK

Si algo sale mal en cualquier paso:

```bash
# 1. Restaurar código desde git
git reset --hard d2f2b26

# 2. Restaurar base de datos
Copy-Item "usuarios.db.backup_20251222_181930" -Destination "usuarios.db" -Force

# 3. O restaurar backup completo
Copy-Item "backups/pre-fase0-20251222_181938/*" -Destination "." -Recurse -Force
```

---

## 📝 NOTAS DE PROGRESO

### Paso 1 - ✅ COMPLETADO
- Backup de git creado: commit d2f2b26
- Backup de BD: usuarios.db.backup_20251222_181930
- Backup completo: backups/pre-fase0-20251222_181938/
- Datos exportados a JSON: backups/sqlite_backup_20251222_182016.json

### Paso 2 - ✅ COMPLETADO
- PostgreSQL 18.1-2 instalado
- Base de datos `verificarsms` creada
- Usuario `verificarsms_user` con permisos completos
- Contraseña postgres reseteada para resolver problema de autenticación
- Conexión verificada con test_postgres.py

### Paso 3 - ✅ COMPLETADO
- psycopg2-binary instalado en virtualenv
- Script migrate_sqlite_to_postgres.py creado
- Migración ejecutada exitosamente:
  - 5 usuarios migrados ✅
  - 6 SMS verificaciones migradas ✅
  - 2 tokens de reset migrados ✅
  - 23 sucursales migradas ✅
- backend/database.py actualizado para usar PostgreSQL
- backend/config/database.py actualizado
- .env actualizado con DATABASE_URL
- Aplicación funcionando correctamente con PostgreSQL

### Paso 4 - ✅ COMPLETADO
- Memurai Developer instalado y corriendo como servicio
- Paquete redis instalado en virtualenv
- backend/config/redis_config.py creado
- backend/services/session_service.py implementado
- Sistema de sesiones con Redis funcionando:
  - Sessions persisten entre reinicios ✅
  - TTL de 8 horas configurado ✅
  - Actualización automática de última actividad ✅
- Endpoint /api/sesiones/activas creado (solo admin)
- get_current_user actualizado para leer desde Redis
- Login/logout integrados con Redis
- test_redis.py creado y funcionando correctamente

