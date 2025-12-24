# 🚀 Guía de Instalación en Nuevas Máquinas

Esta guía te ayudará a clonar y configurar VerificarSms en cualquier máquina nueva para que funcione idéntico en todos los equipos.

## ⚡ Instalación Rápida (Recomendada)

### 1. Clonar el Repositorio

```bash
git clone <url-del-repositorio>
cd VerificarSms
```

### 2. Ejecutar Setup Automático

```bash
python setup.py
```

Este script hace **TODO** automáticamente:
- ✅ Verifica Python 3.8+
- ✅ Crea entorno virtual `python-dotenv/`
- ✅ Instala dependencias de `requirements.txt`
- ✅ Crea archivo `.env` con SECRET_KEY única
- ✅ Inicializa base de datos `usuarios.db`
- ✅ Crea usuario admin por defecto (admin/admin123)
- ✅ Instala y compila Tailwind CSS

### 3. Iniciar el Servidor

**Windows:**
```bash
python-dotenv\Scripts\activate
uvicorn backend.main:app --reload
```

**Linux/Mac:**
```bash
source python-dotenv/bin/activate
uvicorn backend.main:app --reload
```

### 4. Acceder a la Aplicación

Abre tu navegador en: **http://localhost:8000**

**Login:**
- Usuario: `admin`
- Contraseña: `admin123`

⚠️ **IMPORTANTE:** Cambia la contraseña después del primer login.

---

## 🔍 Verificar Configuración

Si ya ejecutaste `setup.py` pero quieres verificar que todo esté correcto:

```bash
python verify_setup.py
```

Este script verifica:
- ✅ Entorno virtual existe
- ✅ Archivo `.env` existe y tiene SECRET_KEY
- ✅ Base de datos `usuarios.db` existe
- ✅ Todas las carpetas necesarias
- ⚠️ CSS compilado (opcional)
- ⚠️ SMS_API_KEY configurada (opcional)

---

## 📋 ¿Por Qué Ahora Funciona Igual en Todas las Máquinas?

### Problema Anterior
- ❌ `.env` no estaba en el repo (necesario para SECRET_KEY)
- ❌ `usuarios.db` no estaba en el repo (diferentes usuarios en cada máquina)
- ❌ No había proceso de inicialización estándar
- ❌ Cada persona configuraba diferente

### Solución Implementada

1. **`.env.example` mejorado**: Template con valores por defecto funcionales
2. **`setup.py`**: Script que configura TODO automáticamente
3. **`backend/init_db.py` mejorado**: Crea usuario admin por defecto
4. **`verify_setup.py`**: Verifica que todo esté bien configurado
5. **README.md actualizado**: Documentación clara paso a paso

### Archivos que NO están en Git (por seguridad)
- `.env` - Variables de entorno con credenciales
- `usuarios.db` - Base de datos con usuarios (se crea automáticamente)
- `python-dotenv/` - Entorno virtual (se crea automáticamente)

### Archivos que SÍ están en Git
- `.env.example` - Template para crear `.env`
- `setup.py` - Script de inicialización
- `backend/init_db.py` - Script que crea BD y usuario admin
- Todo el código fuente

---

## 🔄 Flujo Completo en Nueva Máquina

```
1. git clone <repo>
   ↓
2. cd VerificarSms
   ↓
3. python setup.py
   ↓
   - Crea entorno virtual
   - Instala dependencias
   - Copia .env.example → .env (con SECRET_KEY única)
   - Crea usuarios.db vacía
   - Crea usuario admin por defecto
   - Compila CSS
   ↓
4. python-dotenv\Scripts\activate
   ↓
5. uvicorn backend.main:app --reload
   ↓
6. Login: admin/admin123
   ↓
7. ¡Listo! Sistema funcionando idéntico en todas las máquinas
```

---

## 🛠️ Instalación Manual (Alternativa)

Si prefieres hacerlo paso a paso sin `setup.py`:

### 1. Clonar Repositorio
```bash
git clone <url-del-repositorio>
cd VerificarSms
```

### 2. Crear Entorno Virtual
```bash
python -m venv python-dotenv
```

### 3. Activar Entorno Virtual

**Windows:**
```bash
python-dotenv\Scripts\activate
```

**Linux/Mac:**
```bash
source python-dotenv/bin/activate
```

### 4. Instalar Dependencias
```bash
pip install -r requirements.txt
```

### 5. Configurar Variables de Entorno

**Windows:**
```bash
copy .env.example .env
```

**Linux/Mac:**
```bash
cp .env.example .env
```

Edita `.env` y genera una SECRET_KEY única (puedes usar: https://djecrety.ir/)

### 6. Inicializar Base de Datos
```bash
python -m backend.init_db
```

Esto crea:
- `usuarios.db` con todas las tablas
- Usuario administrador: admin/admin123

### 7. Compilar CSS (Opcional)

Si tienes Node.js instalado:
```bash
npm install
npm run build
```

### 8. Iniciar Servidor
```bash
uvicorn backend.main:app --reload
```

---

## 🔧 Configuración Adicional

### SMS API (Envíos Reales)

Para enviar SMS reales, edita `.env`:

```env
SMS_API_KEY=tu-api-key-real-aqui
SMS_MODO_SIMULADO=false
```

Si `SMS_MODO_SIMULADO=true`, los SMS se imprimen en consola (útil para desarrollo).

### Email (Recuperación de Contraseñas)

Configura en `.env`:

```env
MAIL_USERNAME=tu-email@gmail.com
MAIL_PASSWORD=xxxx xxxx xxxx xxxx  # Contraseña de aplicación de Gmail
MAIL_FROM=tu-email@gmail.com
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
```

Para Gmail necesitas crear una "Contraseña de Aplicación": https://myaccount.google.com/apppasswords

---

## 🚨 Solución de Problemas

### Error: "ModuleNotFoundError: No module named 'backend'"

**Causa:** No estás en la raíz del proyecto o el entorno no está activado.

**Solución:**
```bash
cd VerificarSms  # Ir a la raíz
python-dotenv\Scripts\activate  # Activar entorno
```

### Error: "SECRET_KEY environment variable not set"

**Causa:** No existe `.env` o está mal configurado.

**Solución:**
```bash
# Opción 1: Ejecutar setup completo
python setup.py

# Opción 2: Crear .env manualmente
copy .env.example .env
# Edita .env y cambia SECRET_KEY por un valor único
```

### Login No Funciona (Usuario No Existe)

**Causa:** La base de datos no se inicializó correctamente o no tiene el usuario admin.

**Solución:**
```bash
# Opción 1: Reinicializar (CUIDADO: borra datos)
del usuarios.db
python -m backend.init_db

# Opción 2: Solo crear admin (conserva datos)
python -c "from backend.init_db import create_default_admin; create_default_admin()"
```

### Diferencias entre Máquinas

**Causa:** Archivos que no están sincronizados (`.env`, `usuarios.db`).

**Solución:**
1. Cada máquina debe tener su propio `.env` (no se comparte)
2. Cada máquina debe tener su propia `usuarios.db` (no se comparte)
3. Ejecutar `python setup.py` en CADA máquina nueva

---

## ✅ Checklist de Verificación

Antes de reportar problemas, verifica:

- [ ] Clonaste el repositorio con la última versión
- [ ] Ejecutaste `python setup.py` en esta máquina
- [ ] Existe el archivo `.env` en la raíz del proyecto
- [ ] Existe el archivo `usuarios.db` en la raíz del proyecto
- [ ] El entorno virtual `python-dotenv/` existe
- [ ] Activaste el entorno virtual antes de ejecutar comandos
- [ ] Estás en la carpeta raíz del proyecto (donde está `backend/`)

---

## 📊 Comandos Útiles

```bash
# Verificar instalación
python verify_setup.py

# Reinstalar todo desde cero
python setup.py

# Ver usuarios en la base de datos
python backend/scripts/listar_usuarios.py

# Iniciar en otro puerto
uvicorn backend.main:app --reload --port 8001

# Ver logs del servidor en tiempo real
uvicorn backend.main:app --reload --log-level debug
```

---

## 🔐 Seguridad

### Archivos que NUNCA deben estar en Git:
- `.env` - Contiene credenciales
- `usuarios.db` - Contiene datos de usuarios con contraseñas
- `python-dotenv/` - Entorno virtual (muy pesado)
- `*.log` - Archivos de log

Estos están en `.gitignore` para proteger tu información.

---

## 🆘 Soporte

Si después de seguir esta guía aún tienes problemas:

1. Ejecuta `python verify_setup.py` y comparte el resultado
2. Verifica los mensajes de error en la consola
3. Asegúrate de estar usando Python 3.8 o superior: `python --version`

---

**Última actualización:** Diciembre 2025  
**Responsable:** Desarrollo VerificarSms
