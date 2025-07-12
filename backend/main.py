from fastapi import FastAPI, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from starlette.middleware.sessions import SessionMiddleware

from dotenv import load_dotenv
import os

# Cargar variables de entorno antes de todo
load_dotenv()

# Validar SECRET_KEY
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError("Falta SECRET_KEY en el entorno")

# --- Inicialización de la app ---
app = FastAPI()

# --- Middleware ---
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

# --- Base de datos y modelos ---
from backend.init_db import init_db
from backend.database import get_db
from backend.models import Usuario

# Inicializar DB (solo si es seguro hacerlo aquí)
init_db()

# --- Routers modularizados ---
from backend.usuarios import router as usuarios_router
from backend.sms import router as sms_router

app.include_router(usuarios_router)
app.include_router(sms_router)

# --- Función auxiliar para verificación de sesión ---
def login_required(request: Request):
    user = request.session.get("usuario")
    if not user:
        return None
    return user

# --- Rutas HTML ---
@app.get("/")
def mostrar_login(request: Request):
    return templates.TemplateResponse("index.html", {
        "request": request,
        "user": None
    })

@app.get("/verificar")
def mostrar_verificar(request: Request):
    user = login_required(request)
    if not user:
        return RedirectResponse("/", status_code=302)
    return templates.TemplateResponse("formVerificadorsms.html", {
        "request": request,
        "user": user
    })

@app.get("/home")
def home(request: Request):
    user = login_required(request)
    if not user:
        return RedirectResponse("/", status_code=302)
    return templates.TemplateResponse("home.html", {
        "request": request,
        "user": user
    })

@app.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/", status_code=302)

# --- API: Lista de usuarios (protegida) ---
@app.get("/usuarios")
def obtener_usuarios(request: Request, db: Session = Depends(get_db)):
    user = login_required(request)
    if not user:
        return RedirectResponse("/", status_code=302)

    usuarios = db.query(Usuario).all()
    return [{"usuario": u.usuario, "rol": u.rol} for u in usuarios]

# --- Ruta HTML protegida ---
@app.get("/mantenimiento/gestion")
def mantenimiento_unificado(request: Request):
    user = login_required(request)
    if not user:
        return RedirectResponse("/", status_code=302)
    return templates.TemplateResponse("usuarios/gestion_usuarios.html", {
        "request": request,
        "user": user
    })
