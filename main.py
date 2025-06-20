from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, constr
from dotenv import load_dotenv
from datetime import date
from db import Verificacion, SessionLocal, init_db

import os
import random
import requests
import unicodedata

# Cargar variables de entorno
load_dotenv()

# Inicializar app y base de datos
app = FastAPI()
init_db()

# Leer API KEY desde .env
API_KEY = os.getenv("SMS_API_KEY")

# Esquema de datos del formulario
class SmsRequest(BaseModel):
    personId: constr(min_length=7, max_length=15)
    phoneNumber: constr(min_length=10, max_length=15)
    merchantCode: constr(min_length=3, max_length=3)
    verificationCode: str | None = None

# Generar código de verificación manual
def generate_code() -> str:
    return str(random.randint(1000, 9999))

# Eliminar tildes
def limpiar_mensaje(texto: str) -> str:
    return unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode("ascii")

# Mapear nombre de sucursal
def nombre_sucursal(codigo: str) -> str:
    mapa = {
        "776": "Alberdi",
        "777": "Lules",
        "778": "Famailla",
        "779": "Alderetes",
        "781": "Banda de Rio Sali"
    }
    return mapa.get(codigo, "Sucursal desconocida")

# Enviar SMS
def send_sms(phone: str, message: str):
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

        if "OK" in response.text.upper():
            return True, response.text
        else:
            return False, response.text

    except Exception as e:
        return False, str(e)

# Endpoint principal
@app.post("/send-sms")
def handle_sms(data: SmsRequest):
    code = data.verificationCode or generate_code()

    mensaje_original = f"{data.merchantCode} Limite Deportes {nombre_sucursal(data.merchantCode)} - DNI: {data.personId} - Su Codigo es: {code}"
    message = limpiar_mensaje(mensaje_original)

    success, result = send_sms(data.phoneNumber, message)

    if not success:
        raise HTTPException(status_code=400, detail=str(result))

    db = SessionLocal()
    try:
        registro = Verificacion(
            person_id=data.personId,
            merchant_code=data.merchantCode,
            verification_code=code,
            fecha=date.today()
        )
        db.add(registro)
        db.commit()
    finally:
        db.close()

    return {
        "message": "SMS enviado correctamente",
        "verificationCode": code,
        "personId": data.personId,
        "merchantCode": data.merchantCode,
        "smsBody": message
    }

# Servir HTML
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/formulario")
def show_form():
    return FileResponse(os.path.join("static", "formulario.html"))