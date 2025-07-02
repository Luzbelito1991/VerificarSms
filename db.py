from sqlalchemy import create_engine, Column, String, Date, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import date

# Creamos el motor para SQLite
engine = create_engine("sqlite:///verificaciones.db", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Modelo de la tabla
class Verificacion(Base):
    __tablename__ = "verificaciones"

    id = Column(Integer, primary_key=True, index=True)
    person_id = Column(String, index=True)
    merchant_code = Column(String, index=True)
    verification_code = Column(String, index=True)
    fecha = Column(Date, default=date.today)

# Crear la tabla si no existe
def init_db():
    Base.metadata.create_all(bind=engine)