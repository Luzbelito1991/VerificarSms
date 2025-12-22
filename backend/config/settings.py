"""Configuración centralizada de la aplicación"""
from pydantic_settings import BaseSettings
from typing import Optional
import os
from pathlib import Path


class Settings(BaseSettings):
    """Configuración de la aplicación usando Pydantic"""
    
    # 🔐 Seguridad
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 horas
    
    # 🗄️ Base de datos
    DATABASE_URL: str = "sqlite:///./usuarios.db"
    
    # 📱 SMS API
    SMS_API_URL: str = "http://servicio.smsmasivos.com.ar/enviar_sms.asp"
    SMS_API_KEY: Optional[str] = None
    SMS_MODO_SIMULADO: bool = False
    
    # 🏢 Información de la empresa
    EMPRESA_NOMBRE: str = "Los Quilmes S.A."
    
    # 📊 Códigos de sucursales
    SUCURSALES: dict = {
        "389": "Los Quilmes - Casa Central",
        "561": "Los Quilmes - Sucursal Centro",
        "776": "Limite Deportes Alberdi",
        "777": "Limite Deportes Lules",
        "778": "Limite Deportes Famaillá",
        "779": "Limite Deportes Alderetes",
        "781": "Limite Deportes Banda de Río Salí"
    }
    
    # 🌐 CORS
    CORS_ORIGINS: list = ["*"]
    
    # 📁 Paths
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
    STATIC_DIR: Path = BASE_DIR / "static"
    TEMPLATES_DIR: Path = BASE_DIR / "templates"
    
    # 🐞 Debug
    DEBUG: bool = True
    
    # 🔢 Paginación
    DEFAULT_PAGE_SIZE: int = 10
    MAX_PAGE_SIZE: int = 100
    
    # 📧 Configuración de Email
    MAIL_USERNAME: Optional[str] = None
    MAIL_PASSWORD: Optional[str] = None
    MAIL_FROM: Optional[str] = None
    MAIL_FROM_NAME: str = "Sistema VerificarSMS"
    MAIL_PORT: int = 587
    MAIL_SERVER: Optional[str] = None
    MAIL_STARTTLS: bool = True
    MAIL_SSL_TLS: bool = False
    USE_CREDENTIALS: bool = True
    VALIDATE_CERTS: bool = True
    
    # 🔑 Recuperación de contraseñas
    RESET_TOKEN_EXPIRE_HOURS: int = 2  # Token válido por 2 horas

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"  # Ignorar variables extra del .env


# Instancia global de configuración
settings = Settings()
