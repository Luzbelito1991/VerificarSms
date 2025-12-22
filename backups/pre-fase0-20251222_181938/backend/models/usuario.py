"""Modelo de Usuario"""
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from backend.config.database import Base


class Usuario(Base):
    """Usuario del sistema que puede enviar SMS"""
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    usuario = Column(String(50), unique=True, index=True, nullable=False)
    hash_password = Column(String(128), nullable=False)
    rol = Column(String(20), nullable=False)
    email = Column(String(255), nullable=True, index=True)  # Sin unique por limitación de SQLite en ALTER TABLE

    # Relación con verificaciones
    verificaciones = relationship(
        "Verificacion",
        back_populates="usuario",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Usuario(id={self.id}, usuario='{self.usuario}', rol='{self.rol}')>"
