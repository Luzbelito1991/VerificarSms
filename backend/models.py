from sqlalchemy import Column, Integer, String
from backend.database import Base

class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    usuario = Column(String(50), unique=True, index=True, nullable=False)
    hash_password = Column(String(64), nullable=False)
    rol = Column(String(20), nullable=False)

from sqlalchemy import Column, Integer, String, Date
from datetime import date
from backend.database import Base

class Verificacion(Base):
    __tablename__ = "verificaciones"

    id = Column(Integer, primary_key=True, index=True)
    person_id = Column(String, index=True)
    merchant_code = Column(String, index=True)
    verification_code = Column(String, index=True)
    fecha = Column(Date, default=date.today)