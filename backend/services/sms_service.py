"""Servicio de envío y gestión de SMS"""
import requests
import random
import unicodedata
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from typing import Dict, List, Optional, Tuple
from backend.models import Verificacion, Usuario
from backend.config.settings import settings


class SMSService:
    """Servicio para manejo de SMS y verificaciones"""
    
    @staticmethod
    def generar_codigo() -> str:
        """Genera un código de verificación de 4 dígitos"""
        return str(random.randint(1000, 9999))
    
    @staticmethod
    def normalizar_texto(texto: str) -> str:
        """
        Elimina acentos y caracteres especiales del texto
        para compatibilidad con SMS
        """
        texto_nfkd = unicodedata.normalize("NFKD", texto)
        return "".join([c for c in texto_nfkd if not unicodedata.combining(c)])
    
    @staticmethod
    def get_nombre_sucursal(codigo: str) -> str:
        """Obtiene el nombre de la sucursal por su código"""
        return settings.SUCURSALES.get(codigo, f"Sucursal {codigo}")
    
    @staticmethod
    def enviar_sms(
        phone_number: str,
        mensaje: str,
        modo_simulado: Optional[bool] = None
    ) -> Dict:
        """
        Envía un SMS a través de la API
        
        Args:
            phone_number: Número de teléfono destino
            mensaje: Texto del mensaje
            modo_simulado: Si es True, simula el envío sin llamar a la API
            
        Returns:
            Dict con el resultado del envío
        """
        if modo_simulado is None:
            modo_simulado = settings.SMS_MODO_SIMULADO
        
        # Normalizar mensaje
        mensaje_limpio = SMSService.normalizar_texto(mensaje)
        
        # Modo simulado para desarrollo/testing
        if modo_simulado:
            print(f"\n📱 MODO SIMULADO - SMS a {phone_number}:")
            print(f"📝 Mensaje: {mensaje_limpio}")
            return {
                "ok": True,
                "mensaje": "SMS simulado enviado correctamente",
                "detalles": f"📱 {phone_number}: {mensaje_limpio}"
            }
        
        # Envío real a la API
        try:
            # Parámetros correctos según documentación: APIKEY, TOS, TEXTO
            data = {
                "APIKEY": settings.SMS_API_KEY,
                "TOS": phone_number,
                "TEXTO": mensaje_limpio
            }
            
            response = requests.post(settings.SMS_API_URL, data=data, timeout=10)
            
            print(f"✅ Respuesta HTTP {response.status_code}")
            print(f"📄 Contenido: {response.text}")
            
            if response.status_code == 200:
                return {
                    "ok": True,
                    "mensaje": "SMS enviado exitosamente",
                    "detalles": response.text
                }
            else:
                return {
                    "ok": False,
                    "mensaje": f"Error HTTP {response.status_code}",
                    "detalles": response.text
                }
        
        except requests.RequestException as e:
            return {
                "ok": False,
                "mensaje": "Error al conectar con API SMS",
                "detalles": str(e)
            }
    
    @staticmethod
    def registrar_verificacion(
        db: Session,
        person_id: str,
        phone_number: str,
        merchant_code: str,
        verification_code: str,
        usuario_id: int,
        estado: str = "enviado",
        error_mensaje: Optional[str] = None
    ) -> Verificacion:
        """Registra una verificación SMS en la base de datos"""
        merchant_name = SMSService.get_nombre_sucursal(merchant_code)
        
        verificacion = Verificacion(
            person_id=person_id,
            phone_number=phone_number,
            merchant_code=merchant_code,
            merchant_name=merchant_name,
            verification_code=verification_code,
            usuario_id=usuario_id,
            estado=estado,
            error_mensaje=error_mensaje
        )
        
        db.add(verificacion)
        db.commit()
        db.refresh(verificacion)
        
        return verificacion
    
    @staticmethod
    def get_verificaciones(
        db: Session,
        usuario_id: Optional[int] = None,
        fecha_inicio: Optional[datetime] = None,
        fecha_fin: Optional[datetime] = None,
        estado: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> Tuple[List[Verificacion], int]:
        """
        Obtiene verificaciones con filtros y paginación
        
        Returns:
            Tupla de (lista de verificaciones, total)
        """
        query = db.query(Verificacion)
        
        # Filtrar por usuario
        if usuario_id:
            query = query.filter(Verificacion.usuario_id == usuario_id)
        
        # Filtrar por rango de fechas
        if fecha_inicio:
            query = query.filter(Verificacion.fecha >= fecha_inicio)
        if fecha_fin:
            query = query.filter(Verificacion.fecha <= fecha_fin)
        
        # Obtener total
        total = query.count()
        
        # Ordenar y paginar
        verificaciones = query.order_by(Verificacion.fecha.desc()).offset(skip).limit(limit).all()
        
        return verificaciones, total
    
    @staticmethod
    def get_estadisticas(db: Session, usuario_id: Optional[int] = None) -> Dict:
        """
        Obtiene estadísticas de SMS enviados
        
        Args:
            db: Sesión de base de datos
            usuario_id: Si se proporciona, filtra por usuario específico
            
        Returns:
            Dict con estadísticas
        """
        query = db.query(Verificacion)
        
        if usuario_id:
            query = query.filter(Verificacion.usuario_id == usuario_id)
        
        total = query.count()
        
        # Aquí puedes agregar más métricas según necesites
        return {
            "total_sms": total,
            "sms_hoy": query.filter(
                func.date(Verificacion.fecha) == datetime.now().date()
            ).count()
        }
