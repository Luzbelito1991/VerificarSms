from fastapi import APIRouter, HTTPException, Request, Depends, Response
from pydantic import BaseModel, constr
from sqlalchemy.orm import Session

# 🆕 Usar configuración y servicios centralizados
from backend.config import get_db, settings
from backend.models import Usuario
from backend.core import get_current_user
from backend.services import SMSService
from backend.middleware.rate_limiting import limiter
from backend.config.rate_limits import get_rate_limit_string

router = APIRouter()

# 📦 Datos del frontend para enviar un SMS
class SmsRequest(BaseModel):
    personId: constr(min_length=7, max_length=15)
    phoneNumber: constr(min_length=10, max_length=15)  # ✅ número celular
    merchantCode: constr(min_length=3, max_length=3)
    merchantName: str | None = None  # 🏪 Nombre de sucursal
    verificationCode: str | None = None


# 📲 Enviar y registrar SMS en la base
@router.post("/send-sms", response_model=None)
@limiter.limit(get_rate_limit_string("sms_enviar"))  # 🚦 5 SMS por minuto
@limiter.limit(get_rate_limit_string("sms_enviar_por_hora"))  # 🚦 30 SMS por hora
@limiter.limit(get_rate_limit_string("sms_enviar_por_dia"))  # 🚦 200 SMS por día
def handle_sms(
    request: Request,
    response: Response,  # Required by slowapi
    data: SmsRequest,
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    # Generar código PRIMERO (antes de validar saldo)
    code = data.verificationCode or SMSService.generar_codigo()
    
    # 🔍 Validar saldo antes de enviar (solo si no está en modo simulado)
    if not settings.SMS_MODO_SIMULADO:
        try:
            import requests as req
            url = "https://servicio.smsmasivos.com.ar/obtener_saldo.asp"
            params = {"apikey": settings.SMS_API_KEY}
            response_saldo = req.get(url, params=params, timeout=5)
            
            if response_saldo.status_code == 200:
                try:
                    saldo = int(response_saldo.text.strip())
                    if saldo <= 0:
                        # Registrar como fallido CON EL CÓDIGO GENERADO
                        SMSService.registrar_verificacion(
                            db=db,
                            person_id=data.personId,
                            phone_number=data.phoneNumber,
                            merchant_code=data.merchantCode,
                            verification_code=code,
                            usuario_id=user.id,
                            estado="fallido",
                            error_mensaje="Saldo insuficiente"
                        )
                        raise HTTPException(
                            status_code=402,
                            detail="❌ MENSAJE NO ENVIADO - Saldo insuficiente. Contacte con su proveedor para recargar."
                        )
                except ValueError:
                    pass  # Si no es un número, continuar con el envío
        except HTTPException:
            raise  # Re-lanzar la excepción 402
        except Exception as e:
            # Si falla la validación de saldo, continuar de todos modos
            print(f"⚠️ No se pudo validar saldo: {e}")
    
    # Obtener nombre de sucursal desde los datos o desde la configuración
    merchant_name = data.merchantName or SMSService.get_nombre_sucursal(data.merchantCode)
    
    # Construir mensaje con el formato correcto
    texto = f"{data.merchantCode} - {merchant_name} - DNI: {data.personId} - Su Codigo es: {code}"
    
    # Enviar SMS usando el servicio
    resultado = SMSService.enviar_sms(data.phoneNumber, texto)
    
    # ✅ Registrar SIEMPRE en base de datos (exitoso o fallido)
    # 🟡 Si está en modo simulado, usar estado "test"
    # 🟢 Si se envió exitosamente, usar estado "enviado"
    # 🔴 Si falló, usar estado "fallido"
    if settings.SMS_MODO_SIMULADO:
        estado = "test"
        error_msg = None
    else:
        estado = "enviado" if resultado["ok"] else "fallido"
        error_msg = None if resultado["ok"] else resultado.get("mensaje", "Error desconocido")
    
    verif = SMSService.registrar_verificacion(
        db=db,
        person_id=data.personId,
        phone_number=data.phoneNumber,
        merchant_code=data.merchantCode,
        verification_code=code,
        usuario_id=user.id,
        estado=estado,
        error_mensaje=error_msg
    )

    print(f"📦 Verificación guardada: {verif.person_id}, {verif.phone_number}, {verif.verification_code}, Estado: {estado}")

    # ❌ Si falló, lanzar excepción DESPUÉS de registrar
    if not resultado["ok"]:
        raise HTTPException(status_code=500, detail=resultado["mensaje"])

    # Determinar mensaje según el modo
    if settings.SMS_MODO_SIMULADO:
        mensaje_respuesta = "SMS Test enviado correctamente"
    else:
        mensaje_respuesta = "SMS enviado correctamente"

    return {
        "message": mensaje_respuesta,
        "verificationCode": code,
        "personId": data.personId,
        "merchantCode": data.merchantCode,
        "smsBody": SMSService.normalizar_texto(texto),
        "modoSimulado": settings.SMS_MODO_SIMULADO,
        "esTest": settings.SMS_MODO_SIMULADO,
        "detalles": resultado.get("detalles", "")
    }


# 📅 Consultar vencimiento del paquete prepago
@router.get("/obtener-vencimiento")
def obtener_vencimiento_paquete(user = Depends(get_current_user)):
    """
    Consulta la fecha de vencimiento del paquete prepago de SMS Masivos.
    Solo disponible para usuarios con rol admin.
    """
    if user.rol.lower() != "admin":
        raise HTTPException(status_code=403, detail="Acceso denegado. Solo administradores.")
    
    if settings.SMS_MODO_SIMULADO:
        return {
            "ok": True,
            "mensaje": "Modo simulado activado",
            "fecha_vencimiento": "2025-12-31",
            "simulado": True
        }
    
    try:
        import requests
        url = "http://servicio.smsmasivos.com.ar/obtener_vencimiento_paquete.asp"
        params = {"apikey": settings.SMS_API_KEY}
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        return {
            "ok": True,
            "fecha_vencimiento": response.text.strip(),
            "mensaje": "Fecha de vencimiento obtenida correctamente",
            "simulado": False
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al consultar vencimiento: {str(e)}"
        )


# 📊 Consultar saldo de SMS disponibles
@router.get("/obtener-saldo")
def obtener_saldo_sms(user = Depends(get_current_user)):
    """
    Consulta el saldo de SMS disponibles en la cuenta de SMS Masivos.
    Disponible para todos los usuarios autenticados.
    """
    if settings.SMS_MODO_SIMULADO:
        return {
            "ok": True,
            "mensaje": "Modo simulado activado",
            "saldo": 9999,
            "simulado": True
        }
    
    try:
        import requests
        url = "https://servicio.smsmasivos.com.ar/obtener_saldo.asp"
        params = {"apikey": settings.SMS_API_KEY}
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        # La respuesta debería ser un número
        saldo_texto = response.text.strip()
        
        # Intentar convertir a número
        try:
            saldo = int(saldo_texto)
            return {
                "ok": True,
                "saldo": saldo,
                "mensaje": f"Saldo: {saldo} SMS disponibles",
                "simulado": False,
                "alerta": saldo < 10  # Alerta si quedan menos de 10 SMS
            }
        except ValueError:
            # Si no es un número, puede ser un mensaje de error
            return {
                "ok": False,
                "mensaje": f"Respuesta inesperada: {saldo_texto}",
                "saldo": 0,
                "simulado": False
            }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al consultar saldo: {str(e)}"
        )
