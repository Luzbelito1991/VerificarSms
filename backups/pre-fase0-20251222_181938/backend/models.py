from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.database import Base

# 👤 Usuario que envía SMS
class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    usuario = Column(String(50), unique=True, index=True, nullable=False)
    hash_password = Column(String(128), nullable=False)  # 🔐 Ampliado para bcrypt
    rol = Column(String(20), nullable=False)

    verificaciones = relationship("Verificacion", back_populates="usuario", cascade="all, delete-orphan")

# ✅ Verificación de SMS
class Verificacion(Base):
    __tablename__ = "verificaciones"

    id = Column(Integer, primary_key=True, index=True)
    person_id = Column(String, index=True)             # DNI
    phone_number = Column(String, nullable=False)      # 📱 Número celular
    merchant_code = Column(String, index=True)
    merchant_name = Column(String, nullable=True)      # 🏪 Nombre de sucursal
    verification_code = Column(String, index=True)
    fecha = Column(DateTime, default=datetime.now)

    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)

    usuario = relationship("Usuario", back_populates="verificaciones")