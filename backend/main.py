from fastapi import FastAPI, Request, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from starlette.middleware.sessions import SessionMiddleware  # 🆕 Middleware de sesión
from backend.database import SessionLocal
from backend.models import Usuario

from dotenv import load_dotenv
import os

# --- 📦 Inicializar app y base de datos ---
from backend.init_db import init_db       # Inicializa la base si no existe
from backend.usuarios import router as usuarios_router
from backend.sms import router as sms_router

# 🚀 Crear instancia de la app
app = FastAPI()
init_db()                                 # Ejecuta creación de tablas
load_dotenv()                             # Carga .env para API Keys u otros datos

# --- 🔐 Activar sesión segura ---
app.add_middleware(SessionMiddleware, secret_key=os.getenv("SECRET_KEY", "clave_super_segura"))

# --- 🧩 Motor de plantillas con Jinja2 ---
templates = Jinja2Templates(directory="templates")  # Carpeta de vistas HTML

# --- 🔌 Routers modularizados ---
app.include_router(usuarios_router)      # API login y usuarios
app.include_router(sms_router)           # API SMS

# --- 🔐 Middleware CORS para desarrollo ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],                 # Permitir cualquier origen (dev)
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 📂 Archivos estáticos como CSS, JS, imágenes ---
app.mount("/static", StaticFiles(directory="static"), name="static")

# --- 🌐 RUTAS DE INTERFAZ HTML ---

# 🟢 Login principal
@app.get("/")
def mostrar_login(request: Request):
    return templates.TemplateResponse("index.html", {
        "request": request,
        "user": None
    })

# 🔒 Formulario de verificación SMS
@app.get("/verificar")
def mostrar_verificar(request: Request):
    return templates.TemplateResponse("formVerificadorsms.html", {
        "request": request,
        "user": "fernando"
    })

# 🏠 Página HOME dinámica según sesión
@app.get("/home")
def home(request: Request):
    nombre = request.session.get("usuario", "Invitado")
    return templates.TemplateResponse("home.html", {
        "request": request,
        "user": nombre
    })

# 🔁 Cerrar sesión: borra y redirige
@app.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/", status_code=302)

# ⚙️ Panel de gestión de usuarios (muestra lista)
@app.get("/mantenimiento/gestion")
def mantenimiento_unificado(request: Request):
    usuario = request.session.get("usuario", "fernando")

    db = SessionLocal()
    usuarios_db = db.query(Usuario).all()
    db.close()

    usuarios = [{"nombre": u.usuario, "rol": u.rol} for u in usuarios_db]

    return templates.TemplateResponse("usuarios/gestion_usuarios.html", {
        "request": request,
        "user": usuario,
        "usuarios": usuarios
    })