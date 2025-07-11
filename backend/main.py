from fastapi import FastAPI, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from starlette.middleware.sessions import SessionMiddleware

from dotenv import load_dotenv
import os

# --- Backend y base de datos ---
from backend.init_db import init_db
from backend.database import SessionLocal, get_db
from backend.models import Usuario
from backend.usuarios import router as usuarios_router
from backend.sms import router as sms_router

# --- Inicialización app ---
app = FastAPI()
init_db()
load_dotenv()

# --- Seguridad y CORS ---
app.add_middleware(SessionMiddleware, secret_key=os.getenv("SECRET_KEY", "clave_super_segura"))
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# --- Archivos estáticos y plantillas ---
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# --- Routers modularizados ---
app.include_router(usuarios_router)
app.include_router(sms_router)

# --- Rutas HTML ---
@app.get("/")
def mostrar_login(request: Request):
    return templates.TemplateResponse("index.html", { "request": request, "user": None })

@app.get("/verificar")
def mostrar_verificar(request: Request):
    return templates.TemplateResponse("formVerificadorsms.html", { "request": request, "user": "fernando" })

@app.get("/home")
def home(request: Request):
    nombre = request.session.get("usuario", "Invitado")
    return templates.TemplateResponse("home.html", { "request": request, "user": nombre })

@app.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/", status_code=302)

# ✅ Ruta para frontend: lista de usuarios
@app.get("/usuarios")
def obtener_usuarios(db: Session = Depends(get_db)):
    usuarios = db.query(Usuario).all()
    return [{"usuario": u.usuario, "rol": u.rol} for u in usuarios]

@app.get("/mantenimiento/gestion")
def mantenimiento_unificado(request: Request):
    return templates.TemplateResponse("usuarios/gestion_usuarios.html", {
        "request": request,
        "user": request.session.get("usuario", "Invitado")
    })
