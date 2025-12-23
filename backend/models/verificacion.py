"""Modelo de Verificación SMS"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.config.database import Base


class Verificacion(Base):
    """Registro de SMS de verificación enviado"""
    __tablename__ = "verificaciones"

    id = Column(Integer, primary_key=True, index=True)
    person_id = Column(String, index=True)              # DNI del cliente
    phone_number = Column(String, nullable=False)       # Número de celular
    merchant_code = Column(String, index=True)          # Código de sucursal
    merchant_name = Column(String, nullable=True)       # Nombre de sucursal
    verification_code = Column(String, index=True)      # Código de verificación
    fecha = Column(DateTime, default=datetime.now)      # Fecha de envío
    estado = Column(String(20), default="enviado")      # Estado: enviado, fallido
    error_mensaje = Column(String, nullable=True)       # Mensaje de error si falló

    # Relación con usuario
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    usuario = relationship("Usuario", back_populates="verificaciones")

    def __repr__(self):
        return f"<Verificacion(id={self.id}, phone='{self.phone_number}', code='{self.verification_code}')>"
