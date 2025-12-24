"""Middleware para logging de requests"""
import time
import logging
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware para registrar todas las peticiones HTTP"""
    
    async def dispatch(self, request: Request, call_next):
        # Registrar inicio de la petición
        start_time = time.time()
        
        # Información básica de la petición
        logger.info(f"🔵 {request.method} {request.url.path}")
        
        try:
            # Procesar la petición
            response = await call_next(request)
            
            # Calcular tiempo de procesamiento
            process_time = time.time() - start_time
            
            # Registrar respuesta
            logger.info(
                f"✅ {request.method} {request.url.path} - "
                f"Status: {response.status_code} - "
                f"Time: {process_time:.3f}s"
            )
            
            # Agregar header con tiempo de procesamiento
            response.headers["X-Process-Time"] = str(process_time)
            
            return response
        except Exception as e:
            # Capturar y registrar cualquier excepción
            process_time = time.time() - start_time
            logger.error(
                f"❌ {request.method} {request.url.path} - "
                f"Error: {type(e).__name__}: {str(e)} - "
                f"Time: {process_time:.3f}s",
                exc_info=True
            )
            raise
