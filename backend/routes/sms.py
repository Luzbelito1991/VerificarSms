from fastapi import APIRouter, HTTPException, Request, Depends
from pydantic import BaseModel, constr
from sqlalchemy.orm import Session

# 🆕 Usar configuración y servicios centralizados
from backend.config import get_db, settings
from backend.models import Usuario
from backend.core import get_current_user
from backend.services import SMSService

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
def handle_sms(
    request: Request,
    data: SmsRequest,
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    # Generar código si no se proporciona
    code = data.verificationCode or SMSService.generar_codigo()
    
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

    return {
        "message": "SMS enviado correctamente",
        "verificationCode": code,
        "personId": data.personId,
        "merchantCode": data.merchantCode,
        "smsBody": SMSService.normalizar_texto(texto),
        "modoSimulado": settings.SMS_MODO_SIMULADO,
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