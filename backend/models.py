# models.py
from sqlalchemy import Column, Integer, String
from backend.database import Base

class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    usuario = Column(String, unique=True, index=True, nullable=False)
    hash_password = Column(String, nullable=False)
    rol = Column(String, nullable=False)