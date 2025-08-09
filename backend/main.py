from fastapi import FastAPI, Request, Depends, HTTPException, status, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse, HTMLResponse
from sqlalchemy.orm import Session
from starlette.middleware.sessions import SessionMiddleware

from dotenv import load_dotenv
import os

# --- Cargar variables de entorno ---
load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError("Falta SECRET_KEY en el entorno")

# --- Inicializar app FastAPI ---
app = FastAPI()

# --- Middlewares ---
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# --- Archivos estáticos y plantillas ---
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# --- Inicializar base de datos ---
from backend.init_db import init_db
from backend.database import get_db
from backend.models import Usuario, Verificacion
from backend.auth_utils import get_current_user

init_db()

# --- Routers (módulo routes) ---
from backend.routes.usuarios import router as usuarios_router
from backend.routes.sms import router as sms_router
from backend.routes.admin_sms import admin_router

app.include_router(usuarios_router)
app.include_router(sms_router)
app.include_router(admin_router)

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
    request.session.clear()
    return RedirectResponse(url="/", status_code=302)

# ============================
# 🔐 RUTAS HTML PROTEGIDAS
# ============================
@app.get("/home")
def home(request: Request, user: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    enviados = db.query(Verificacion).filter(Verificacion.verification_code != None).count()
    no_enviados = db.query(Verificacion).filter(Verificacion.verification_code == None).count()

    return render_template_protegido("home.html", request, {
        "user": user,
        "enviados": enviados,
        "no_enviados": no_enviados
    })

@app.get("/verificar")
def mostrar_verificar(request: Request, user: Usuario = Depends(get_current_user)):
    return render_template_protegido("formVerificadorsms.html", request, {
        "user": user
    })

@app.get("/mantenimiento/gestion")
def mantenimiento_unificado(request: Request, user: Usuario = Depends(get_current_user)):
    return render_template_protegido("usuarios/gestion_usuarios.html", request, {
        "user": user
    })

# ============================
# 📊 API JSON PROTEGIDA
# ============================
@app.get("/usuarios")
def obtener_usuarios(
    search: str = Query("", alias="search"),
    db: Session = Depends(get_db),
    user: Usuario = Depends(get_current_user)
):
    query = db.query(Usuario)

    if search.strip():
        palabras = search.strip().lower().split()[:2]
        patron = " ".join(palabras)
        query = query.filter(Usuario.usuario.ilike(f"{patron}%"))

    usuarios = query.all()
    return [{"usuario": u.usuario, "rol": u.rol} for u in usuarios]

# ============================
# ✉️ VISTA ADMIN - PANEL DE SMS
# ============================
@app.get("/admin/sms", response_class=HTMLResponse)
def vista_sms_admin(request: Request, user: Usuario = Depends(get_current_user)):
    if user.rol.lower() not in ["admin", "operador"]:
       raise HTTPException(status_code=403, detail="Acceso denegado")

    return render_template_protegido("admin/vista_admin_sms.html", request, {
        "user": user
    })








