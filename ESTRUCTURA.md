# Estructura del Proyecto - VerificarSms v2.0

## 📁 Organización de Carpetas

```
backend/
├── config/              # ⚙️ Configuración centralizada
│   ├── __init__.py
│   ├── settings.py      # Variables de entorno y constantes
│   └── database.py      # Configuración SQLAlchemy
│
├── core/                # 🔐 Funcionalidades centrales
│   ├── __init__.py
│   └── security.py      # Autenticación y hashing
│
├── models/              # 📊 Modelos de base de datos
│   ├── __init__.py
│   ├── usuario.py
│   └── verificacion.py
│
├── routes/              # 🛣️ Endpoints API
│   ├── __init__.py
│   ├── usuarios.py      # CRUD usuarios
│   ├── sms.py           # Envío SMS
│   ├── admin_sms.py     # Panel admin
│   └── registros.py     # Métricas
│
├── services/            # 💼 Lógica de negocio
│   ├── __init__.py
│   ├── auth_service.py  # Autenticación
│   ├── user_service.py  # Gestión usuarios
│   └── sms_service.py   # Envío y registro SMS
│
├── middleware/          # 🔄 Middlewares
│   ├── __init__.py
│   └── logging_middleware.py
│
├── utils/               # 🛠️ Utilidades
│   ├── __init__.py
│   └── helpers.py
│
└── scripts/             # 📜 Scripts auxiliares
    └── listar_usuarios.py

requirements/
├── base.txt             # Dependencias base
├── dev.txt              # Dependencias desarrollo
└── prod.txt             # Dependencias producción

static/                  # 🎨 Archivos estáticos
├── css/
├── js/
└── images/

templates/               # 📄 Plantillas Jinja2
├── layout.html
├── index.html
├── formVerificadorsms.html
├── home.html
├── admin/
├── usuarios/
└── registros/

tests/                   # 🧪 Tests unitarios

.env                     # 🔐 Variables de entorno (no subir a git)
usuarios.db             # 📦 Base de datos SQLite
```

## 🎯 Principios de Diseño

### 1. **Separación de Responsabilidades**
- **Routes**: Solo manejan peticiones HTTP y respuestas
- **Services**: Contienen toda la lógica de negocio
- **Models**: Definen la estructura de datos
- **Config**: Centralizan configuración

### 2. **Inyección de Dependencias**
Usar `Depends()` de FastAPI para:
- Sesiones de BD (`get_db`)
- Usuario autenticado (`get_current_user`)
- Configuración (`settings`)

### 3. **Tipado Fuerte**
Usar type hints en todas las funciones para mejor IDE support y documentación.

### 4. **Configuración por Entorno**
Variables en `.env`, cargadas por `pydantic-settings`.

## 🚀 Próximos Pasos

1. ✅ Estructura de carpetas creada
2. ⏳ Actualizar imports en routes
3. ⏳ Migrar a PostgreSQL
4. ⏳ Implementar multi-tenancy
5. ⏳ Agregar tests
6. ⏳ Docker y CI/CD
