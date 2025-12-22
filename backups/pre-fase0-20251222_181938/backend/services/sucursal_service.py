"""Servicio para gestión de sucursales"""
from sqlalchemy.orm import Session
from backend.models.sucursal import Sucursal
from typing import List, Optional


class SucursalService:
    """Servicio para operaciones CRUD de sucursales"""
    
    @staticmethod
    def get_all(db: Session) -> List[Sucursal]:
        """Obtener todas las sucursales ordenadas por código"""
        return db.query(Sucursal).order_by(Sucursal.codigo).all()
    
    @staticmethod
    def get_by_codigo(db: Session, codigo: str) -> Optional[Sucursal]:
        """Obtener sucursal por código"""
        return db.query(Sucursal).filter(Sucursal.codigo == codigo).first()
    
    @staticmethod
    def create(db: Session, codigo: str, nombre: str) -> Sucursal:
        """Crear nueva sucursal"""
        sucursal = Sucursal(codigo=codigo, nombre=nombre)
        db.add(sucursal)
        db.commit()
        db.refresh(sucursal)
        return sucursal
    
    @staticmethod
    def update(db: Session, codigo: str, nuevo_nombre: str) -> Optional[Sucursal]:
        """Actualizar nombre de sucursal"""
        sucursal = SucursalService.get_by_codigo(db, codigo)
        if sucursal:
            sucursal.nombre = nuevo_nombre
            db.commit()
            db.refresh(sucursal)
        return sucursal
    
    @staticmethod
    def delete(db: Session, codigo: str) -> bool:
        """Eliminar sucursal"""
        sucursal = SucursalService.get_by_codigo(db, codigo)
        if sucursal:
            db.delete(sucursal)
            db.commit()
            return True
        return False
    
    @staticmethod
    def get_nombre_sucursal(db: Session, codigo: str) -> str:
        """Obtener nombre de sucursal por código (con fallback)"""
        sucursal = SucursalService.get_by_codigo(db, codigo)
        return sucursal.nombre if sucursal else f"Sucursal {codigo}"
