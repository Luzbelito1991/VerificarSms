"""Servicio de autenticación"""
from sqlalchemy.orm import Session
from backend.models import Usuario
from backend.core.security import hash_password, verify_password
from typing import Optional


class AuthService:
    """Servicio para manejar autenticación de usuarios"""
    
    @staticmethod
    def authenticate_user(db: Session, username: str, password: str) -> Optional[Usuario]:
        """
        Autentica un usuario con username y password
        
        Args:
            db: Sesión de base de datos
            username: Nombre de usuario
            password: Contraseña en texto plano
            
        Returns:
            Usuario si las credenciales son válidas, None en caso contrario
        """
        user = db.query(Usuario).filter(Usuario.usuario == username).first()
        
        if not user:
            return None
            
        if not verify_password(password, user.hash_password):
            return None
            
        return user
    
    @staticmethod
    def create_user(db: Session, username: str, password: str, rol: str) -> Usuario:
        """
        Crea un nuevo usuario
        
        Args:
            db: Sesión de base de datos
            username: Nombre de usuario único
            password: Contraseña en texto plano
            rol: Rol del usuario (admin, operador)
            
        Returns:
            Usuario creado
        """
        hashed_password = hash_password(password)
        
        new_user = Usuario(
            usuario=username,
            hash_password=hashed_password,
            rol=rol
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        return new_user
    
    @staticmethod
    def change_password(db: Session, user_id: int, new_password: str) -> bool:
        """
        Cambia la contraseña de un usuario
        
        Args:
            db: Sesión de base de datos
            user_id: ID del usuario
            new_password: Nueva contraseña en texto plano
            
        Returns:
            True si se cambió exitosamente, False en caso contrario
        """
        user = db.query(Usuario).filter(Usuario.id == user_id).first()
        
        if not user:
            return False
        
        user.hash_password = hash_password(new_password)
        db.commit()
        
        return True
