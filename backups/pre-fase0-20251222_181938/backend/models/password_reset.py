"""Modelo para tokens de recuperación de contraseña"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta
from backend.config.database import Base


class PasswordResetToken(Base):
    """Token de recuperación de contraseña con expiración"""
    __tablename__ = "password_reset_tokens"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False)
    token = Column(String(100), unique=True, index=True, nullable=False)
    expiracion = Column(DateTime, nullable=False)
    usado = Column(Integer, default=0)  # 0 = no usado, 1 = usado
    fecha_creacion = Column(DateTime, default=datetime.utcnow)

    # Relación con usuario
    usuario = relationship("Usuario")

    def __repr__(self):
        return f"<PasswordResetToken(usuario_id={self.usuario_id}, usado={self.usado})>"

    def is_valid(self) -> bool:
        """Verifica si el token es válido (no expirado y no usado)"""
        return self.usado == 0 and datetime.utcnow() < self.expiracion
