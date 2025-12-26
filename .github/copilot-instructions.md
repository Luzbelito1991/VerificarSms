# Copilot Instructions - VerificarSms

## Project Overview
FastAPI-based SMS verification system for "Los Quilmes S.A." retail stores. Sends verification codes to customers via SMS API, with role-based access control (admin/operador) and comprehensive tracking.

## Architecture

### Backend Structure
- **Entry Point**: `backend/main.py` - FastAPI app with session middleware, static files, and router registration
- **Database**: PostgreSQL using SQLAlchemy ORM with models:
  - `Usuario`: user accounts with SHA-256 hashed passwords and roles
  - `Verificacion`: SMS records linked to users via ForeignKey
- **Auth**: Session-based (not JWT) via `SessionMiddleware`. `get_current_user()` dependency checks `request.session["usuario"]`
- **Routes Modularization**:
  - `routes/usuarios.py`: login, CRUD for users, session management
  - `routes/sms.py`: send SMS endpoint with external API integration
  - `routes/admin_sms.py`: admin panel API for SMS history with filters/pagination

### Frontend Architecture
- **Templates**: Jinja2 with `layout.html` base template containing sidebar navigation
- **Styling**: Tailwind CSS compiled via npm scripts (`npm run dev` watches changes)
- **JavaScript**: Vanilla JS modules in `static/js/` using `fetch()` for API calls
- **Pattern**: Form validation happens client-side before submission; server returns JSON responses

## Key Conventions

### Password Hashing
Always use `hashlib.sha256(password.encode()).hexdigest()` - consistent across `auth_utils.py` and `usuarios.py`

### Session Management
```python
# Setting session
request.session["usuario"] = user.usuario
request.session["rol"] = user.rol

# Protected routes use Depends(get_current_user)
def route(user: Usuario = Depends(get_current_user)):
```

### SMS Integration
- Uses external API: `http://servicio.smsmasivos.com.ar/enviar_sms.asp`
- Simulated mode via env var `SMS_MODO_SIMULADO=true` for testing
- Always strip accents with `unicodedata.normalize("NFKD", texto)` before sending
- Merchant codes map to store names via `nombre_sucursal()` helper

### Database Sessions
Use FastAPI's dependency injection pattern:
```python
def endpoint(db: Session = Depends(get_db)):
    # Always query/commit within the route
    db.add(obj)
    db.commit()
```

### Template Rendering Helper
Use `render_template_protegido()` in `main.py` for protected routes - ensures `current_user` context

## Development Workflow

### Running the Application
```bash
# Activate venv (Windows)
python-dotenv\Scripts\activate

# Start FastAPI dev server
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

# Watch Tailwind CSS changes (separate terminal)
npm run dev
```

### Environment Variables Required
Create `.env` in root:
```
SECRET_KEY=your-secret-key-here
SMS_API_KEY=your-sms-api-key
SMS_MODO_SIMULADO=false
```

### Database Initialization
```python
# Run once or after model changes
python -m backend.init_db
```

## Important Patterns

### Merchant Codes
Fixed list of 7 store codes (389, 561, 776-779, 781) - validate against `nombre_sucursal()` mapping

### Verification Code Generation
4-digit random codes: `str(random.randint(1000, 9999))`

### Frontend Form Validation
Client-side regex patterns:
- DNI: `/^\d{8}$/` (exactly 8 digits)
- Phone: `/^\d{10}$/` (exactly 10 digits)

### API Response Pattern
JSON responses follow: `{"ok": True/False, "mensaje": "...", ...data}`

### Error Handling in Routes
```python
if not condition:
    raise HTTPException(status_code=400, detail="Spanish error message")
```

### Emoji Comments
Code uses emoji comments for clarity: 🔐 auth, 📱 phone, 🗂️ database, etc.

## Testing & Debugging

### Simulated SMS Mode
Set `SMS_MODO_SIMULADO=true` to print SMS to console instead of sending

### Utility Scripts
- `listar_usuarios.py`: Query all users (run outside web server)
- `verificar_tabla.py`, `reset_verificaciones.py`: Database maintenance scripts

## Frontend Integration

### Static Files
- CSS: `/static/css/style.css` (compiled from `input.css`)
- JS: `/static/js/` - modules load via `<script>` tags in templates
- Icons: Lucide icons via CDN - initialize with `lucide.createIcons()`

### Alpine.js
Loaded via CDN for reactive components (e.g., dropdown menus, modals)

### Page-Specific Assets
Each feature has dedicated JS: `login.js`, `verificarSms.js`, `sms_admin.js`, `gestionUsuarios.js`

## Role-Based Access
- **Admin**: full access to user management (`/mantenimiento/gestion`) and SMS history (`/admin/sms`)
- **Operador**: can only send SMS (`/verificar`)
- Check: `{% if user.rol|lower == "admin" %}` in templates

## Common Tasks

### Adding a New Route
1. Create endpoint in appropriate `routes/*.py` router
2. Import and `app.include_router()` in `main.py` if new router
3. Add navigation link in `templates/layout.html` sidebar
4. Create template in `templates/` if rendering HTML

### Adding Database Column
1. Update model in `backend/models.py`
2. Create and run Alembic migration (production)
3. For dev: drop tables and run `python -m backend.init_db`

### Styling Updates
Edit `static/css/input.css` → `npm run dev` auto-compiles → refresh browser
