from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime

# 🆕 Usar configuración y servicios centralizados
from backend.config import get_db
from backend.models import Usuario, Verificacion
from backend.core import get_current_user
from backend.services import SMSService, UserService

admin_router = APIRouter()

# 🎛️ Lista de usuarios para el filtro del panel
@admin_router.get("/api/usuarios")
def listar_usuarios(
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    if user.rol.lower() not in ["admin", "operador"]:
        raise HTTPException(status_code=403, detail="Acceso denegado")
    
    usuarios = UserService.get_all_users(db, limit=1000)
    return [{"id": u.id, "nombre": u.usuario} for u in usuarios]


# 📊 Lista de SMS enviados con filtros + paginación
@admin_router.get("/api/admin/sms")
def obtener_sms(
    usuario_id: int | None = None,
    fecha_inicio: str | None = None,
    fecha_fin: str | None = None,
    estado: str | None = None,
    skip: int = 0,
    limit: int = 5,
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    if user.rol.lower() not in ["admin", "operador"]:
        raise HTTPException(status_code=403, detail="Acceso denegado")
    
    # Convertir fechas string a datetime si existen
    fecha_inicio_dt = datetime.fromisoformat(fecha_inicio) if fecha_inicio else None
    fecha_fin_dt = datetime.fromisoformat(fecha_fin) if fecha_fin else None
    
    # 🆕 Usar servicio para obtener verificaciones
    verifs, total = SMSService.get_verificaciones(
        db=db,
        usuario_id=usuario_id,
        fecha_inicio=fecha_inicio_dt,
        fecha_fin=fecha_fin_dt,
        estado=estado,
        skip=skip,
        limit=limit
    )

    # 💡 Obtener nombres de usuarios de una sola vez
    usuarios_dict = {u.id: u.usuario for u in UserService.get_all_users(db, limit=1000)}

    resultado = []
    for v in verifs:
        nombre_usuario = usuarios_dict.get(v.usuario_id, "desconocido")

        resultado.append({
            "dni": v.person_id,
            "celular": v.phone_number,
            "sucursal": v.merchant_code,
            "codigo": v.verification_code,
            "usuario_nombre": nombre_usuario,
            "fecha": v.fecha.isoformat(),
            "estado": v.estado if v.estado else "enviado"
        })

    return {"sms": resultado, "total": total}


# 🔢 Obtener el total de registros con filtros activos
@admin_router.get("/api/admin/sms/total")
def contar_sms(
    usuario_id: int | None = None,
    fecha_inicio: str | None = None,
    fecha_fin: str | None = None,
    estado: str | None = None,
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    if user.rol.lower() not in ["admin", "operador"]:
        raise HTTPException(status_code=403, detail="Acceso denegado")
    
    # Convertir fechas
    fecha_inicio_dt = datetime.fromisoformat(fecha_inicio) if fecha_inicio else None
    fecha_fin_dt = datetime.fromisoformat(fecha_fin) if fecha_fin else None
    
    # 🆕 Usar servicio
    _, total = SMSService.get_verificaciones(
        db=db,
        usuario_id=usuario_id,
        fecha_inicio=fecha_inicio_dt,
        fecha_fin=fecha_fin_dt,
        estado=estado,
        skip=0,
        limit=1
    )
    
    return {"total": total}


# 📤 Exportar todos los registros filtrados sin paginación
@admin_router.get("/api/admin/sms/todos")
def obtener_todos_sms(
    usuario_id: int | None = None,
    fecha_inicio: str | None = None,
    fecha_fin: str | None = None,
    estado: str | None = None,
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    if user.rol.lower() not in ["admin", "operador"]:
        raise HTTPException(status_code=403, detail="Acceso denegado")
    
    # Convertir fechas
    fecha_inicio_dt = datetime.fromisoformat(fecha_inicio) if fecha_inicio else None
    fecha_fin_dt = datetime.fromisoformat(fecha_fin) if fecha_fin else None
    
    # 🆕 Obtener todos (sin límite)
    verifs, total = SMSService.get_verificaciones(
        db=db,
        usuario_id=usuario_id,
        fecha_inicio=fecha_inicio_dt,
        fecha_fin=fecha_fin_dt,
        estado=estado,
        skip=0,
        limit=10000
    )
    
    usuarios_dict = {u.id: u.usuario for u in UserService.get_all_users(db, limit=1000)}

    resultado = []
    for v in verifs:
        resultado.append({
            "dni": v.person_id,
            "celular": v.phone_number,
            "sucursal": v.merchant_code,
            "codigo": v.verification_code,
            "usuario_nombre": usuarios_dict.get(v.usuario_id, "desconocido"),
            "fecha": v.fecha.strftime("%Y-%m-%d"),
            "estado": "enviado"
        })

    return resultado

