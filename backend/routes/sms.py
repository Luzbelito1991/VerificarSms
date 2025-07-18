from fastapi import APIRouter, HTTPException, Request, Depends
from pydantic import BaseModel, constr
from sqlalchemy.orm import Session
from datetime import date
from dotenv import load_dotenv
import unicodedata
import random
import requests
import os

from backend.database import get_db
from backend.models import Verificacion, Usuario
from backend.auth_utils import get_current_user


load_dotenv()

API_KEY = os.getenv("SMS_API_KEY")
MODO_SIMULADO = os.getenv("SMS_MODO_SIMULADO", "false").lower() == "true"

router = APIRouter()

# 📦 Datos del frontend para enviar un SMS
class SmsRequest(BaseModel):
    personId: constr(min_length=7, max_length=15)
    phoneNumber: constr(min_length=10, max_length=15)  # ✅ número celular
    merchantCode: constr(min_length=3, max_length=3)
    verificationCode: str | None = None

# 🔢 Generar código aleatorio
def generate_code() -> str:
    return str(random.randint(1000, 9999))

# 🔤 Eliminar tildes del mensaje
def limpiar_mensaje(texto: str) -> str:
    return unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode("ascii")

# 🏪 Nombre legible de sucursal
def nombre_sucursal(codigo: str) -> str:
    mapa = {
        "776": "776",
        "777": "777",
        "778": "778",
        "779": "779",
        "781": "781"
    }
    return mapa.get(codigo, "Sucursal desconocida")

# 📡 Envío real o simulado de SMS
def send_sms(phone: str, message: str):
    if MODO_SIMULADO:
        print(f"[SIMULADO] SMS a {phone}: {message}")
        return True, "SMS simulado correctamente"

    try:
        url = "http://servicio.smsmasivos.com.ar/enviar_sms.asp"
        params = {
            "api": "1",
            "apikey": API_KEY,
            "TOS": phone,
            "TEXTO": message
        }
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return ("OK" in response.text.upper(), response.text)
    except Exception as e:
        return False, str(e)

# 📲 Enviar y registrar SMS en la base
@router.post("/send-sms", response_model=None)
def handle_sms(
    request: Request,
    data: SmsRequest,
    db: Session = Depends(get_db),
    user: Usuario = Depends(get_current_user)
):
    code = data.verificationCode or generate_code()
    texto = f"{data.merchantCode} Limite Deportes {nombre_sucursal(data.merchantCode)} - DNI: {data.personId} - Su Codigo es: {code}"
    mensaje = limpiar_mensaje(texto)

    ok, respuesta = send_sms(data.phoneNumber, mensaje)
    if not ok:
        raise HTTPException(status_code=400, detail=respuesta)

    # ✅ Guardar celular en la verificación
    verif = Verificacion(
        person_id=data.personId,
        phone_number=data.phoneNumber,
        merchant_code=data.merchantCode,
        verification_code=code,
        fecha=date.today(),
        usuario_id=user.id
    )
    db.add(verif)
    db.commit()

    print("📦 Verificación guardada:", verif.person_id, verif.phone_number, verif.verification_code)

    return {
        "message": "SMS enviado correctamente",
        "verificationCode": code,
        "personId": data.personId,
        "merchantCode": data.merchantCode,
        "smsBody": mensaje,
        "modoSimulado": MODO_SIMULADO
    }