"""Modelo de Sucursal"""
from sqlalchemy import Column, String
from backend.config.database import Base


class Sucursal(Base):
    """Sucursal/Tienda del sistema"""
    __tablename__ = "sucursales"

    codigo = Column(String(10), primary_key=True, index=True)  # Ej: "389", "561"
    nombre = Column(String(100), nullable=False)  # Ej: "Los Quilmes - Casa Central"

    def __repr__(self):
        return f"<Sucursal(codigo='{self.codigo}', nombre='{self.nombre}')>"
