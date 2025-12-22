# 🚀 FASE 0: Migración a Multi-Usuario

**Fecha inicio:** 22 de diciembre de 2025  
**Estado actual:** Backup completo realizado ✅  
**Commit de respaldo:** d2f2b26

---

## 📋 CHECKLIST DE MIGRACIÓN

### **Paso 1: Preparación (15 min)**
- [x] Backup de base de datos SQLite
- [x] Commit en git de estado actual
- [x] Backup completo del proyecto
- [ ] Documentar configuración actual
- [ ] Exportar datos de SQLite a JSON (por seguridad)

### **Paso 2: Instalar PostgreSQL (30 min)**
- [ ] Descargar PostgreSQL para Windows
- [ ] Instalar PostgreSQL
- [ ] Crear base de datos `verificarsms`
- [ ] Crear usuario `verificarsms_user`
- [ ] Probar conexión

### **Paso 3: Migrar Esquema y Datos (45 min)**
- [ ] Instalar `psycopg2-binary` y `alembic`
- [ ] Crear script de migración de datos
- [ ] Ejecutar migración SQLite → PostgreSQL
- [ ] Verificar integridad de datos
- [ ] Probar aplicación con PostgreSQL

### **Paso 4: Redis para Sesiones (30 min)**
- [ ] Instalar Redis (Memurai para Windows)
- [ ] Instalar `redis` y `fastapi-sessions`
- [ ] Configurar SessionMiddleware con Redis
- [ ] Probar login y persistencia de sesiones

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

### Paso 2 - EN PROGRESO
...

