# 🎯 Guía de Uso - Nueva Estructura

## ✅ Lo que se ha hecho

### 1. **Nueva Estructura de Carpetas**
```
backend/
├── config/          ✅ Configuración centralizada
├── core/            ✅ Funcionalidades centrales
├── models/          ✅ Modelos separados
├── routes/          ✅ Ya existía
├── services/        ✅ Lógica de negocio
├── middleware/      ✅ Middlewares personalizados
└── utils/           ✅ Utilidades generales

requirements/        ✅ Dependencias organizadas
tests/              ✅ Estructura de tests
```

### 2. **Archivos Creados**

**Configuración:**
- `backend/config/settings.py` - Todas las variables de entorno
- `backend/config/database.py` - Configuración SQLAlchemy
- `.env.example` - Plantilla de variables

**Servicios (Lógica de Negocio):**
- `backend/services/auth_service.py` - Autenticación
- `backend/services/user_service.py` - Gestión de usuarios
- `backend/services/sms_service.py` - Envío y registro de SMS

**Modelos:**
- `backend/models/usuario.py` - Modelo Usuario
- `backend/models/verificacion.py` - Modelo Verificación

**Core:**
- `backend/core/security.py` - Hash y verificación de passwords

**Utils:**
- `backend/utils/helpers.py` - Funciones auxiliares

**Requirements:**
- `requirements/base.txt` - Dependencias base
- `requirements/dev.txt` - Desarrollo + testing
- `requirements/prod.txt` - Producción + PostgreSQL

## 🚀 Cómo Usar los Nuevos Servicios

### Ejemplo: Usar SMSService en un route

**❌ ANTES (todo mezclado en el route):**
```python
@router.post("/enviar-sms")
def enviar_sms(request: Request, db: Session = Depends(get_db)):
    # Generar código
    codigo = str(random.randint(1000, 9999))
    
    # Enviar SMS (lógica mezclada)
    resultado = requests.get(...)
    
    # Guardar en BD
    verificacion = Verificacion(...)
    db.add(verificacion)
    db.commit()
```

**✅ AHORA (usando servicios):**
```python
from backend.services import SMSService

@router.post("/enviar-sms")
def enviar_sms(request: Request, db: Session = Depends(get_db)):
    # Generar código
    codigo = SMSService.generar_codigo()
    
    # Construir mensaje
    mensaje = f"Tu código es: {codigo}"
    
    # Enviar SMS
    resultado = SMSService.enviar_sms(phone_number, mensaje)
    
    # Registrar en BD
    if resultado["ok"]:
        SMSService.registrar_verificacion(
            db, person_id, phone_number, 
            merchant_code, codigo, usuario.id
        )
```

### Ejemplo: Usar AuthService

**✅ Login usando AuthService:**
```python
from backend.services import AuthService

@router.post("/login")
def login(form_data: LoginForm, request: Request, db: Session = Depends(get_db)):
    # Autenticar usuario
    user = AuthService.authenticate_user(db, form_data.username, form_data.password)
    
    if not user:
        raise HTTPException(status_code=401, detail="Credenciales inválidas")
    
    # Crear sesión
    request.session["usuario"] = user.usuario
    request.session["rol"] = user.rol
    
    return {"ok": True}
```

### Ejemplo: Usar UserService

**✅ Buscar usuarios con filtros:**
```python
from backend.services import UserService

@router.get("/usuarios")
def listar_usuarios(
    search: str = "",
    rol: str = "",
    page: int = 1,
    db: Session = Depends(get_db)
):
    skip = (page - 1) * 10
    
    usuarios, total = UserService.search_users(
        db, search_term=search, rol_filter=rol,
        skip=skip, limit=10
    )
    
    return {
        "usuarios": usuarios,
        "total": total,
        "page": page
    }
```

## 🔧 Configuración

### 1. **Copiar archivo de entorno**
```bash
cp .env.example .env
```

### 2. **Editar .env con tus valores**
```env
SECRET_KEY=tu-clave-segura
SMS_API_KEY=tu-api-key
SMS_MODO_SIMULADO=true  # false para producción
```

### 3. **Usar settings en el código**
```python
from backend.config import settings

# Acceder a cualquier configuración
api_key = settings.SMS_API_KEY
sucursal = settings.SUCURSALES.get("776")
```

## 📦 Instalar Dependencias

### Desarrollo:
```bash
pip install -r requirements/dev.txt
```

### Producción:
```bash
pip install -r requirements/prod.txt
```

## 🔄 Próximos Pasos

1. **Actualizar los routes existentes** para usar los servicios
2. **Migrar a PostgreSQL** cuando esté listo
3. **Agregar tests** en `tests/`
4. **Implementar logging** con el middleware
5. **Crear modelos multi-tenant** para el SaaS

## 📚 Ventajas de Esta Estructura

✅ **Separación clara** de responsabilidades
✅ **Fácil de testear** - servicios independientes
✅ **Reutilización** de código
✅ **Escalabilidad** - fácil agregar features
✅ **Mantenimiento** simplificado
✅ **Configuración centralizada**
✅ **Type hints** en todo el código

## ❓ Preguntas Frecuentes

**P: ¿Debo borrar los archivos antiguos?**
R: No todavía. Primero actualizaremos los imports, luego los borraremos.

**P: ¿Cómo migro mis routes actuales?**
R: Gradualmente. Empezamos route por route usando los servicios.

**P: ¿Funciona con la BD actual?**
R: Sí, sigue usando SQLite. Cuando quieras, cambiamos a PostgreSQL.
