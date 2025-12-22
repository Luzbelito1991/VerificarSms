# 📧 Guía de Configuración de Email - Sistema de Recuperación de Contraseñas

## 🎯 Pasos para Configurar Gmail

### 1. Preparar tu cuenta de Gmail

1. Ve a https://myaccount.google.com/security
2. En "Cómo inicias sesión en Google", hacé clic en "Verificación en 2 pasos"
3. Si no está activada, activala siguiendo los pasos de Google

### 2. Crear Contraseña de Aplicación

1. Una vez activada la verificación en 2 pasos, volvé a https://myaccount.google.com/security
2. Buscá "Contraseñas de aplicaciones" (puede estar abajo de todo)
3. Hacé clic y Google te pedirá verificar tu identidad
4. En "Selecciona la app", elegí "Correo"
5. En "Selecciona el dispositivo", elegí "Otra (nombre personalizado)" y escribí "VerificarSMS"
6. Hacé clic en "Generar"
7. **IMPORTANTE:** Copiá la contraseña de 16 caracteres que te muestra (formato: xxxx xxxx xxxx xxxx)

### 3. Configurar el archivo .env

Abrí el archivo `.env` en la raíz del proyecto y completá estos datos:

```env
# Reemplazá estos valores con los tuyos:
MAIL_USERNAME=tu-email@gmail.com
MAIL_PASSWORD=xxxx xxxx xxxx xxxx  # ← Pegá la contraseña de 16 caracteres que copiaste
MAIL_FROM=tu-email@gmail.com
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
```

**Ejemplo real:**
```env
MAIL_USERNAME=ejemplo@gmail.com
MAIL_PASSWORD=xxxx xxxx xxxx xxxx  # Reemplazar con tu contraseña de aplicación
MAIL_FROM=ejemplo@gmail.com
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
```

### 4. Reiniciar el Servidor

Después de guardar el `.env`, reiniciá el servidor:

```powershell
# Detener con Ctrl+C
# Iniciar nuevamente
python-dotenv\Scripts\python.exe -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

## 🧪 Cómo Probar

### 1. Agregar Email a un Usuario

1. Iniciá sesión como admin
2. Andá a "Gestión de Usuarios"
3. Hacé clic en "Editar" en cualquier usuario
4. Completá el campo "Email" con un email real tuyo
5. Guardá los cambios

### 2. Probar Recuperación de Contraseña

1. Cerrá sesión (Logout)
2. En el login, hacé clic en "¿Olvidaste tu contraseña?"
3. Ingresá el email que agregaste al usuario
4. Hacé clic en "Enviar Instrucciones"
5. **Revisá tu casilla de email** (puede tardar unos segundos)
6. Abrí el email y hacé clic en el botón "Restablecer Contraseña"
7. Ingresá tu nueva contraseña
8. Iniciá sesión con la nueva contraseña

## 🔧 Para Outlook/Hotmail

Si preferís usar Outlook en lugar de Gmail:

```env
MAIL_USERNAME=ejemplo@outlook.com
MAIL_PASSWORD=tu-contraseña-aqui
MAIL_FROM=ejemplo@outlook.com
MAIL_SERVER=smtp-mail.outlook.com
MAIL_PORT=587
```

**Nota:** Outlook no requiere contraseña de aplicación, usás tu contraseña normal.

## ❌ Problemas Comunes

### Email no llega

1. **Revisá spam/correo no deseado** - A veces los emails caen ahí
2. **Verificá el .env** - Asegurate de que no haya espacios extra
3. **Email incorrecto** - Verificá que el email del usuario esté bien escrito
4. **Contraseña incorrecta** - Si usás Gmail, asegurate de usar la contraseña de aplicación (16 caracteres), no tu contraseña normal

### Error al enviar

Si en la consola ves "❌ Error al enviar email", revisá:

1. Que tengas internet
2. Que el MAIL_SERVER sea correcto
3. Que la contraseña sea válida

## 📝 Notas Importantes

- El link de recuperación **expira en 2 horas**
- Cada link solo se puede usar **una vez**
- Si un usuario no tiene email configurado, no podrá recuperar su contraseña (tendrá que pedirle al admin que se la resetee)
- Los usuarios creados antes de esta actualización NO tienen email - agregáselos desde Gestión de Usuarios

## 🎉 ¡Listo!

Una vez configurado, el sistema de recuperación funciona automáticamente. Los usuarios podrán recuperar sus contraseñas sin intervención del admin.
