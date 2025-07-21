from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models import Usuario, Verificacion
from backend.routes.sms import nombre_sucursal

admin_router = APIRouter()

# 🎛️ Lista de usuarios para el filtro del panel
@admin_router.get("/api/usuarios")
def listar_usuarios(db: Session = Depends(get_db)):
    usuarios = db.query(Usuario).all()
    return [{"id": u.id, "nombre": u.usuario} for u in usuarios]


# 📊 Lista de SMS enviados con filtros + paginación
@admin_router.get("/api/admin/sms")
def obtener_sms(
    usuario_id: int | None = None,
    fecha_inicio: str | None = None,
    fecha_fin: str | None = None,
    estado: str | None = None,  # aún no implementado en modelo
    skip: int = 0,
    limit: int = 5,
    db: Session = Depends(get_db)
):
    query = db.query(Verificacion)

    # 🔍 Filtros opcionales
    if usuario_id:
        query = query.filter(Verificacion.usuario_id == usuario_id)
    if fecha_inicio:
        query = query.filter(Verificacion.fecha >= fecha_inicio)
    if fecha_fin:
        query = query.filter(Verificacion.fecha <= fecha_fin)
    # 🟡 Estado no implementado aún: si se agrega, usar filtro aquí

    # 🔁 Paginación y orden descendente
    verifs = query.order_by(Verificacion.fecha.desc()).offset(skip).limit(limit).all()

    # 💡 Optimización: obtener nombres de usuarios de una sola vez
    usuarios_dict = {u.id: u.usuario for u in db.query(Usuario).all()}

    resultado = []
    for v in verifs:
        nombre_usuario = usuarios_dict.get(v.usuario_id, "desconocido")

        resultado.append({
            "dni": v.person_id,
            "celular": v.phone_number,
            "sucursal": nombre_sucursal(v.merchant_code),
            "codigo": v.verification_code,
            "usuario_nombre": nombre_usuario,
            "fecha": v.fecha.isoformat(),  # ej: "2025-07-21T11:56:32"
            "estado": "enviado"  # 🔄 reemplazar por v.estado cuando se implemente
        })

    return resultado


# 🔢 Obtener el total de registros con filtros activos
@admin_router.get("/api/admin/sms/total")
def contar_sms(
    usuario_id: int | None = None,
    fecha_inicio: str | None = None,
    fecha_fin: str | None = None,
    estado: str | None = None,  # aún no implementado en modelo
    db: Session = Depends(get_db)
):
    query = db.query(Verificacion)

    if usuario_id:
        query = query.filter(Verificacion.usuario_id == usuario_id)
    if fecha_inicio:
        query = query.filter(Verificacion.fecha >= fecha_inicio)
    if fecha_fin:
        query = query.filter(Verificacion.fecha <= fecha_fin)
    # estado aún no implementado

    total = query.count()
    return {"total": total}


# 📤 Exportar todos los registros filtrados sin paginación
@admin_router.get("/api/admin/sms/todos")
def obtener_todos_sms(
    usuario_id: int | None = None,
    fecha_inicio: str | None = None,
    fecha_fin: str | None = None,
    estado: str | None = None,
    db: Session = Depends(get_db)
):
    query = db.query(Verificacion)

    if usuario_id:
        query = query.filter(Verificacion.usuario_id == usuario_id)
    if fecha_inicio:
        query = query.filter(Verificacion.fecha >= fecha_inicio)
    if fecha_fin:
        query = query.filter(Verificacion.fecha <= fecha_fin)
    # estado aún no implementado

    verifs = query.order_by(Verificacion.fecha.desc()).all()
    usuarios_dict = {u.id: u.usuario for u in db.query(Usuario).all()}

    resultado = []
    for v in verifs:
        resultado.append({
            "dni": v.person_id,
            "celular": v.phone_number,
            "sucursal": nombre_sucursal(v.merchant_code),
            "codigo": v.verification_code,
            "usuario_nombre": usuarios_dict.get(v.usuario_id, "desconocido"),
            "fecha": v.fecha.strftime("%Y-%m-%d"),
            "estado": "enviado"
        })

    return resultado