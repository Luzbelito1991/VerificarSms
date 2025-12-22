"""Rutas para recuperación de contraseña"""
from fastapi import APIRouter, HTTPException, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import secrets

from backend.config import get_db, settings
from backend.models import Usuario, PasswordResetToken
from backend.services import EmailService, AuthService

router = APIRouter()
templates = Jinja2Templates(directory=str(settings.TEMPLATES_DIR))


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str


# 📧 Solicitar recuperación de contraseña
@router.post("/api/forgot-password")
async def forgot_password(data: ForgotPasswordRequest, db: Session = Depends(get_db)):
    """
    Genera token de recuperación y envía email al usuario
    """
    # Buscar usuario por email
    user = db.query(Usuario).filter(Usuario.email == data.email).first()
    
    if not user:
        # Por seguridad, siempre responder OK aunque no exista el usuario
        return {
            "ok": True,
            "mensaje": "Si el email existe en el sistema, recibirás un correo con instrucciones"
        }
    
    # Generar token único
    token = secrets.token_urlsafe(32)
    expiration = datetime.utcnow() + timedelta(hours=settings.RESET_TOKEN_EXPIRE_HOURS)
    
    # Guardar token en base de datos
    reset_token = PasswordResetToken(
        usuario_id=user.id,
        token=token,
        expiracion=expiration,
        usado=0
    )
    
    db.add(reset_token)
    db.commit()
    
    # Enviar email
    try:
        await EmailService.send_password_reset_email(
            email=data.email,
            username=user.usuario,
            reset_token=token
        )
        
        return {
            "ok": True,
            "mensaje": "Si el email existe en el sistema, recibirás un correo con instrucciones"
        }
    except Exception as e:
        print(f"❌ Error al enviar email: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Error al enviar el correo. Contactá al administrador."
        )


# 🔄 Restablecer contraseña con token
@router.post("/api/reset-password")
def reset_password(data: ResetPasswordRequest, db: Session = Depends(get_db)):
    """
    Valida token y cambia la contraseña del usuario
    """
    # Buscar token
    reset_token = db.query(PasswordResetToken).filter(
        PasswordResetToken.token == data.token
    ).first()
    
    if not reset_token:
        raise HTTPException(status_code=400, detail="Token inválido")
    
    # Verificar si está usado o expirado
    if not reset_token.is_valid():
        raise HTTPException(
            status_code=400,
            detail="El token ha expirado o ya fue utilizado"
        )
    
    # Buscar usuario
    user = db.query(Usuario).filter(Usuario.id == reset_token.usuario_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    # Cambiar contraseña
    AuthService.change_password(db, user.id, data.new_password)
    
    # Marcar token como usado
    reset_token.usado = 1
    db.commit()
    
    return {
        "ok": True,
        "mensaje": "Contraseña restablecida correctamente. Ya podés iniciar sesión."
    }


# 📄 Vista HTML para solicitar reset
@router.get("/forgot-password", response_class=HTMLResponse)
def show_forgot_password(request: Request):
    """Muestra formulario para solicitar recuperación"""
    return templates.TemplateResponse("forgot_password.html", {
        "request": request
    })


# 📄 Vista HTML para restablecer contraseña
@router.get("/reset-password", response_class=HTMLResponse)
def show_reset_password(request: Request, token: str):
    """Muestra formulario para establecer nueva contraseña"""
    return templates.TemplateResponse("reset_password.html", {
        "request": request,
        "token": token
    })
