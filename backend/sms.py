# backend/sms.py

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, constr
from backend.database import SessionLocal
from backend.models import Verificacion
from datetime import date
from dotenv import load_dotenv
import unicodedata
import hashlib
import random
import requests
import os

load_dotenv()

API_KEY = os.getenv("SMS_API_KEY")
MODO_SIMULADO = os.getenv("SMS_MODO_SIMULADO", "false").lower() == "true"

router = APIRouter()

# 📦 Datos que se esperan del frontend para enviar un SMS
class SmsRequest(BaseModel):
    personId: constr(min_length=7, max_length=15)
    phoneNumber: constr(min_length=10, max_length=15)
    merchantCode: constr(min_length=3, max_length=3)
    verificationCode: str | None = None

# 🔢 Generar código aleatorio de 4 dígitos
def generate_code() -> str:
    return str(random.randint(1000, 9999))

# 🔤 Eliminar tildes del mensaje SMS
def limpiar_mensaje(texto: str) -> str:
    return unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode("ascii")

# 🏪 Traducir código de sucursal a nombre
def nombre_sucursal(codigo: str) -> str:
    mapa = {
        "776": "Alberdi",
        "777": "Lules",
        "778": "Famailla",
        "779": "Alderetes",
        "781": "Banda de Rio Sali"
    }
    return mapa.get(codigo, "Sucursal desconocida")

# 📡 Enviar el SMS real, o simulado si está activado
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

# 📲 Endpoint para manejar el envío y registrar en base
@router.post("/send-sms")
def handle_sms(data: SmsRequest):
    code = data.verificationCode or generate_code()
    texto = f"{data.merchantCode} Limite Deportes {nombre_sucursal(data.merchantCode)} - DNI: {data.personId} - Su Codigo es: {code}"
    mensaje = limpiar_mensaje(texto)

    ok, respuesta = send_sms(data.phoneNumber, mensaje)
    if not ok:
        raise HTTPException(status_code=400, detail=respuesta)

    db = SessionLocal()
    try:
        verif = Verificacion(
            person_id=data.personId,
            merchant_code=data.merchantCode,
            verification_code=code,
            fecha=date.today()
        )
        db.add(verif)
        db.commit()
    finally:
        db.close()

    return {
        "message": "SMS enviado correctamente",
        "verificationCode": code,
        "personId": data.personId,
        "merchantCode": data.merchantCode,
        "smsBody": mensaje,
        "modoSimulado": MODO_SIMULADO
    }