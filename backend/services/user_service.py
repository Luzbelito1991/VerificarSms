"""Servicio de gestión de usuarios"""
from sqlalchemy.orm import Session
from sqlalchemy import or_
from backend.models import Usuario
from backend.core.security import hash_password
from typing import List, Optional, Tuple


class UserService:
    """Servicio para gestión de usuarios"""
    
    @staticmethod
    def get_all_users(db: Session, skip: int = 0, limit: int = 100) -> List[Usuario]:
        """Obtiene todos los usuarios con paginación"""
        return db.query(Usuario).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> Optional[Usuario]:
        """Obtiene un usuario por su ID"""
        return db.query(Usuario).filter(Usuario.id == user_id).first()
    
    @staticmethod
    def get_user_by_username(db: Session, username: str) -> Optional[Usuario]:
        """Obtiene un usuario por su nombre de usuario"""
        return db.query(Usuario).filter(Usuario.usuario == username).first()
    
    @staticmethod
    def search_users(
        db: Session, 
        search_term: str = "", 
        rol_filter: str = "",
        skip: int = 0,
        limit: int = 100
    ) -> Tuple[List[Usuario], int]:
        """
        Busca usuarios con filtros
        
        Returns:
            Tupla de (lista de usuarios, total de usuarios que coinciden)
        """
        query = db.query(Usuario)
        
        # Aplicar filtro de búsqueda
        if search_term:
            query = query.filter(
                or_(
                    Usuario.usuario.contains(search_term),
                    Usuario.rol.contains(search_term)
                )
            )
        
        # Aplicar filtro de rol
        if rol_filter and rol_filter.lower() != "todos":
            query = query.filter(Usuario.rol == rol_filter)
        
        # Obtener total antes de paginar
        total = query.count()
        
        # Aplicar paginación
        users = query.offset(skip).limit(limit).all()
        
        return users, total
    
    @staticmethod
    def update_user(
        db: Session, 
        user_id: int, 
        username: Optional[str] = None,
        password: Optional[str] = None,
        rol: Optional[str] = None
    ) -> Optional[Usuario]:
        """Actualiza un usuario"""
        user = db.query(Usuario).filter(Usuario.id == user_id).first()
        
        if not user:
            return None
        
        if username:
            user.usuario = username
        if password:
            user.hash_password = hash_password(password)
        if rol:
            user.rol = rol
        
        db.commit()
        db.refresh(user)
        
        return user
    
    @staticmethod
    def delete_user(db: Session, user_id: int) -> bool:
        """Elimina un usuario"""
        user = db.query(Usuario).filter(Usuario.id == user_id).first()
        
        if not user:
            return False
        
        db.delete(user)
        db.commit()
        
        return True
    
    @staticmethod
    def count_users(db: Session) -> int:
        """Cuenta el total de usuarios"""
        return db.query(Usuario).count()
