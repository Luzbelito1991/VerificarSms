from fastapi import FastAPI, Request, Depends, HTTPException, status, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse, HTMLResponse
from sqlalchemy.orm import Session
from starlette.middleware.sessions import SessionMiddleware

# 🆕 Importar configuración centralizada
from backend.config import settings, get_db
from backend.models import Usuario, Verificacion
from backend.core import get_current_user
from backend.middleware import LoggingMiddleware

# --- Inicializar app FastAPI ---
app = FastAPI(
    title="VerificarSms API",
    description="Sistema de verificación SMS para Los Quilmes S.A.",
    version="2.0.0"
)

# --- Middlewares ---
app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"]
)
# 🆕 Agregar middleware de logging
if settings.DEBUG:
    app.add_middleware(LoggingMiddleware)

# --- Archivos estáticos y plantillas ---
app.mount("/static", StaticFiles(directory=str(settings.STATIC_DIR)), name="static")
templates = Jinja2Templates(directory=str(settings.TEMPLATES_DIR))

# --- Inicializar base de datos ---
from backend.init_db import init_db
init_db()

# --- Routers (módulo routes) ---
from backend.routes.usuarios import router as usuarios_router
from backend.routes.sms import router as sms_router
from backend.routes.admin_sms import admin_router
from backend.routes.registros import router as registros_router
from backend.routes.password_reset import router as password_reset_router
from backend.routes.sucursales import router as sucursales_router
from backend.routes.sesiones import router as sesiones_router

app.include_router(usuarios_router)
app.include_router(sms_router)
app.include_router(admin_router)
app.include_router(registros_router)
app.include_router(password_reset_router)
app.include_router(sucursales_router)
app.include_router(sesiones_router)

# ============================
# 💡 AUXILIAR PARA PLANTILLAS
# ============================
def render_template_protegido(template_name: str, request: Request, context: dict):
    if "user" in context and "current_user" not in context:
        context["current_user"] = context["user"]
    return templates.TemplateResponse(template_name, {
        "request": request,
        **context
    })

# ============================
# 🌐 RUTAS HTML PÚBLICAS
# ============================
@app.get("/")
def mostrar_login(request: Request):
    return templates.TemplateResponse("index.html", {
        "request": request,
        "user": None
    })

@app.get("/logout")
def logout(request: Request):
    from backend.services.session_service import session_store
    
    # Eliminar sesión de Redis si existe
    session_id = request.session.get("session_id")
    if session_id:
        session_store.delete_session(session_id)
    
    # Limpiar cookies
    request.session.clear()
    return RedirectResponse(url="/", status_code=302)

@app.get("/debug/routes")
def debug_routes():
    """Endpoint temporal para debug - listar todas las rutas"""
    routes = []
    for route in app.routes:
        if hasattr(route, 'path') and hasattr(route, 'methods'):
            routes.append({
                "path": route.path,
                "methods": list(route.methods),
                "name": route.name if hasattr(route, 'name') else None
            })
    return {"total": len(routes), "routes": routes}

# ============================
# 🔐 RUTAS HTML PROTEGIDAS
# ============================
@app.get("/home")
def home(request: Request, user = Depends(get_current_user), db: Session = Depends(get_db)):
    from sqlalchemy import func
    from datetime import datetime, timedelta
    
    enviados = db.query(Verificacion).filter(Verificacion.verification_code != None).count()
    no_enviados = db.query(Verificacion).filter(Verificacion.verification_code == None).count()
    
    # SMS por sucursal (top 5)
    sms_por_sucursal = db.query(
        Verificacion.merchant_code,
        func.count(Verificacion.id).label('total')
    ).filter(
        Verificacion.verification_code != None  # Solo exitosos
    ).group_by(
        Verificacion.merchant_code
    ).order_by(
        func.count(Verificacion.id).desc()
    ).limit(5).all()
    
    # Últimos 7 días
    hoy = datetime.now()
    hace_7_dias = hoy - timedelta(days=6)  # 6 días atrás + hoy = 7 días
    sms_ultimos_7_dias = []
    
    for i in range(7):
        fecha = hace_7_dias + timedelta(days=i)
        inicio_dia = datetime(fecha.year, fecha.month, fecha.day)
        fin_dia = inicio_dia + timedelta(days=1)
        
        count = db.query(Verificacion).filter(
            Verificacion.fecha >= inicio_dia,
            Verificacion.fecha < fin_dia,
            Verificacion.verification_code != None  # Solo exitosos
        ).count()
        
        sms_ultimos_7_dias.append({
            "fecha": fecha.strftime("%d/%m"),
            "cantidad": count
        })

    return render_template_protegido("home.html", request, {
        "user": user,
        "enviados": enviados,
        "no_enviados": no_enviados,
        "sms_por_sucursal": [{"sucursal": s.merchant_code, "total": s.total} for s in sms_por_sucursal],
        "ultimos_7_dias": sms_ultimos_7_dias,
        "total_exitosos": enviados  # Para calcular porcentajes en el template
    })

@app.get("/verificar")
def mostrar_verificar(request: Request, user = Depends(get_current_user)):
    return render_template_protegido("formVerificadorsms.html", request, {
        "user": user,
        "active_page": "verificar"
    })

@app.get("/mantenimiento/gestion")
def mantenimiento_unificado(request: Request, user = Depends(get_current_user)):
    return render_template_protegido("usuarios/gestion_usuarios.html", request, {
        "user": user,
        "active_page": "usuarios"  # ← AGREGAR ESTO
    })


# ============================
# 📊 API JSON PROTEGIDA
# ============================
@app.get("/usuarios")
def obtener_usuarios(
    search: str = Query("", alias="search"),
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    query = db.query(Usuario)

    if search.strip():
        palabras = search.strip().lower().split()[:2]
        patron = " ".join(palabras)
        query = query.filter(Usuario.usuario.ilike(f"{patron}%"))

    usuarios = query.all()
    return [{"usuario": u.usuario, "rol": u.rol, "email": u.email or ""} for u in usuarios]

# ============================
# ✉️ VISTA ADMIN - PANEL DE SMS
# ============================
@app.get("/admin/sms", response_class=HTMLResponse)
def vista_sms_admin(request: Request, user = Depends(get_current_user)):
    if user.rol.lower() not in ["admin", "operador"]:
       raise HTTPException(status_code=403, detail="Acceso denegado")

    return render_template_protegido("admin/vista_admin_sms.html", request, {
        "user": user,
        "active_page": "sms"
    })








