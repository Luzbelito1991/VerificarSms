"""Servicio para envío de emails"""
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from pydantic import EmailStr
from typing import List, Dict, Any
from backend.config import settings


class EmailService:
    """Servicio para gestionar envío de correos electrónicos"""
    
    @staticmethod
    def get_mail_config() -> ConnectionConfig:
        """Obtiene la configuración de email desde settings"""
        return ConnectionConfig(
            MAIL_USERNAME=settings.MAIL_USERNAME or "",
            MAIL_PASSWORD=settings.MAIL_PASSWORD or "",
            MAIL_FROM=settings.MAIL_FROM or settings.MAIL_USERNAME or "",
            MAIL_FROM_NAME=settings.MAIL_FROM_NAME,
            MAIL_PORT=settings.MAIL_PORT,
            MAIL_SERVER=settings.MAIL_SERVER or "",
            MAIL_STARTTLS=settings.MAIL_STARTTLS,
            MAIL_SSL_TLS=settings.MAIL_SSL_TLS,
            USE_CREDENTIALS=settings.USE_CREDENTIALS,
            VALIDATE_CERTS=settings.VALIDATE_CERTS
        )
    
    @staticmethod
    async def send_email(
        recipients: List[EmailStr],
        subject: str,
        body: str,
        template_body: Dict[str, Any] = None
    ) -> bool:
        """
        Envía un email
        
        Args:
            recipients: Lista de destinatarios
            subject: Asunto del correo
            body: Cuerpo del mensaje en HTML
            template_body: Datos para template (opcional)
            
        Returns:
            True si se envió correctamente, False en caso contrario
        """
        try:
            conf = EmailService.get_mail_config()
            
            message = MessageSchema(
                subject=subject,
                recipients=recipients,
                body=body,
                subtype=MessageType.html
            )
            
            fm = FastMail(conf)
            await fm.send_message(message)
            
            return True
        except Exception as e:
            print(f"❌ Error al enviar email: {str(e)}")
            return False
    
    @staticmethod
    async def send_password_reset_email(email: str, username: str, reset_token: str) -> bool:
        """
        Envía email de recuperación de contraseña
        
        Args:
            email: Email del destinatario
            username: Nombre de usuario
            reset_token: Token de recuperación
            
        Returns:
            True si se envió correctamente
        """
        # URL de reset (ajustar según tu dominio)
        reset_url = f"http://127.0.0.1:8000/reset-password?token={reset_token}"
        
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .header {{
                    background: linear-gradient(135deg, #10b981 0%, #059669 100%);
                    color: white;
                    padding: 30px;
                    text-align: center;
                    border-radius: 10px 10px 0 0;
                }}
                .content {{
                    background: #f9fafb;
                    padding: 30px;
                    border: 1px solid #e5e7eb;
                }}
                .button {{
                    display: inline-block;
                    background: #10b981;
                    color: white;
                    padding: 12px 30px;
                    text-decoration: none;
                    border-radius: 6px;
                    margin: 20px 0;
                    font-weight: bold;
                }}
                .footer {{
                    text-align: center;
                    padding: 20px;
                    color: #6b7280;
                    font-size: 12px;
                }}
                .warning {{
                    background: #fef3c7;
                    border-left: 4px solid #f59e0b;
                    padding: 15px;
                    margin: 20px 0;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🔐 Recuperación de Contraseña</h1>
            </div>
            <div class="content">
                <p>Hola <strong>{username}</strong>,</p>
                
                <p>Recibimos una solicitud para restablecer la contraseña de tu cuenta en <strong>{settings.EMPRESA_NOMBRE}</strong>.</p>
                
                <p>Hacé clic en el siguiente botón para crear una nueva contraseña:</p>
                
                <div style="text-align: center;">
                    <a href="{reset_url}" class="button">Restablecer Contraseña</a>
                </div>
                
                <p>O copiá y pegá este enlace en tu navegador:</p>
                <p style="word-break: break-all; color: #10b981;">{reset_url}</p>
                
                <div class="warning">
                    <strong>⚠️ Importante:</strong><br>
                    • Este enlace es válido por <strong>{settings.RESET_TOKEN_EXPIRE_HOURS} horas</strong><br>
                    • Si no solicitaste este cambio, ignorá este correo<br>
                    • Tu contraseña actual seguirá funcionando
                </div>
                
                <p>Si tenés problemas, contactá al administrador del sistema.</p>
            </div>
            <div class="footer">
                <p>Sistema de Verificación SMS - {settings.EMPRESA_NOMBRE}</p>
                <p>Este es un correo automático, por favor no respondas.</p>
            </div>
        </body>
        </html>
        """
        
        return await EmailService.send_email(
            recipients=[email],
            subject=f"Recuperación de Contraseña - {settings.EMPRESA_NOMBRE}",
            body=html_body
        )
