# 🌐 Acceso desde la Red Local

## 📋 Configuración (Una sola vez)

### 1. Configurar Firewall
1. Click derecho en `configurar_firewall.ps1`
2. Seleccionar **"Ejecutar con PowerShell como Administrador"**
3. Si pregunta, permitir la ejecución
4. Esperar mensaje de éxito ✅

### 2. Iniciar Servidor
```powershell
.\iniciar_servidor_red.ps1
```

O simplemente doble click en `iniciar_servidor_red.ps1`

## 🚀 Uso

### En tu PC (servidor)
Después de ejecutar `iniciar_servidor_red.ps1` verás algo como:

```
📡 Tu IP en la red: 128.8.9.116
🌐 El servidor estará accesible en:
   http://128.8.9.116:8000
```

### En la PC de tu compañero
1. Abrir navegador (Chrome, Edge, Firefox)
2. Ir a: `http://128.8.9.116:8000`
3. Hacer login con su usuario y contraseña
4. ¡Listo! Pueden trabajar simultáneamente

## 🔍 Verificar Conexión

### Desde la PC del compañero:
```powershell
# Probar si el servidor está accesible
Test-NetConnection -ComputerName 128.8.9.116 -Port 8000
```

Si dice **TcpTestSucceeded: True** → ✅ Todo bien

## ⚠️ Solución de Problemas

### "No se puede acceder"
1. **Verificar firewall**: Ejecutaste `configurar_firewall.ps1` como administrador?
2. **Verificar servidor**: Está corriendo `iniciar_servidor_red.ps1`?
3. **Verificar IP**: La IP cambió? (ejecuta nuevamente `iniciar_servidor_red.ps1` para ver la actual)
4. **Antivirus**: Algunos antivirus bloquean conexiones, temporalmente deshabilitar

### "Sesión expiró"
- Normal si el servidor se reinició
- Volver a hacer login

### Múltiples usuarios
- ✅ PostgreSQL soporta escrituras concurrentes
- ✅ Redis mantiene sesiones separadas
- ✅ Cada usuario tiene su propia sesión

## 📊 Monitoreo

### Ver sesiones activas (solo admin):
```
http://128.8.9.116:8000/api/sesiones/activas
```

## 🔒 Seguridad

- ✅ El servidor solo es accesible en tu red local (no en internet)
- ✅ Requiere login para acceder
- ✅ Sesiones con expiración de 8 horas
- ⚠️ No uses en redes públicas (cafeterías, aeropuertos)

## 📝 Notas

- **IP fija recomendada**: Configura IP estática en el servidor para que no cambie
- **Router**: Si tienen router, asegúrate de estar en la misma red
- **VPN**: Si usan VPN corporativa, puede interferir

---

**Tu IP actual**: 128.8.9.116  
**Puerto**: 8000  
**URL para compartir**: http://128.8.9.116:8000
