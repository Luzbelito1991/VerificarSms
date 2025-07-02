# backend/main.py

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from dotenv import load_dotenv
import os

# --- 📦 Inicializar app y base de datos ---
from backend.database import init_db
from backend.usuarios import router as usuarios_router
from backend.sms import router as sms_router

app = FastAPI()
init_db()
load_dotenv()

# --- 🧩 Motor de plantillas (Jinja2) ---
templates = Jinja2Templates(directory="templates")

# --- 🔌 Routers separados para modularizar ---
app.include_router(usuarios_router)
app.include_router(sms_router)

# --- 🔐 CORS: habilitado para todos los orígenes (ajustar en prod) ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 📂 Archivos estáticos (CSS, JS, etc.) ---
app.mount("/static", StaticFiles(directory="static"), name="static")

# --- 🌍 RUTAS QUE RENDERIZAN HTML USANDO PLANTILLAS ---

# 🟢 Login principal
@app.get("/")
def mostrar_login(request: Request):
    return templates.TemplateResponse("index.html", {
        "request": request
    })

# 📲 Página de verificación SMS (requiere sesión)
@app.get("/verificar")
def mostrar_verificar(request: Request):
    return templates.TemplateResponse("formVerificadorsms.html", {
        "request": request,
        "user": "fernando"  # en el futuro: valor dinámico desde sesión
    })

# 🛠️ Mantenimiento de usuarios
@app.get("/mantenimiento")
def mostrar_mantenimiento(request: Request):
    return templates.TemplateResponse("mantenimientoUsuarios.html", {
        "request": request,
        "user": "fernando"
    })

# 🔁 Logout (redirige al login)
@app.get("/logout")
def logout():
    return RedirectResponse(url="/", status_code=302)


@app.get("/home")
def home(request: Request):
    return templates.TemplateResponse("home.html", {
        "request": request,
        "user": "fernando"
    })

# 👥 Vista protegida: Usuarios del sistema (solo admin)
@app.get("/mantenimiento/usuarios")
def mostrar_usuarios_sistema(request: Request):
    # ⚠️ En el futuro: validar sesión y rol dinámicamente
    return templates.TemplateResponse("usuarios_sistema.html", {
        "request": request,
        "user": "fernando"  # reemplazar por session.get("usuario") cuando tengas login
    })





