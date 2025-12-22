"""
🏢 Rutas para Gestión de Sucursales
"""
from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel

from backend.config.database import get_db
from backend.auth_utils import get_current_user
from backend.services.sucursal_service import SucursalService

router = APIRouter()


# 📋 Schemas
class SucursalCreate(BaseModel):
    codigo: str
    nombre: str


class SucursalUpdate(BaseModel):
    nombre: str


# ============================================================
# 🏢 VISTA: Gestión de Sucursales
# ============================================================
@router.get("/mantenimiento/sucursales", response_class=HTMLResponse)
async def vista_sucursales(
    request: Request,
    user=Depends(get_current_user)
):
    """Vista para gestionar sucursales"""
    if user.rol.lower() != "admin":
        raise HTTPException(status_code=403, detail="Acceso denegado")
    
    from backend.main import templates
    
    return templates.TemplateResponse(
        "sucursales/gestion_sucursales.html",
        {
            "request": request,
            "user": user,
            "active_page": "sucursales"
        }
    )


# ============================================================
# 📊 API: Sucursales
# ============================================================
@router.get("/api/sucursales")
def obtener_sucursales(
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    """Obtener todas las sucursales"""
    sucursales = SucursalService.get_all(db)
    return [{"codigo": s.codigo, "nombre": s.nombre} for s in sucursales]


@router.post("/api/sucursales")
def crear_sucursal(
    data: SucursalCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    """Crear nueva sucursal"""
    if user.rol.lower() != "admin":
        raise HTTPException(status_code=403, detail="Acceso denegado")
    
    # Verificar si ya existe
    if SucursalService.get_by_codigo(db, data.codigo):
        raise HTTPException(status_code=400, detail="El código de sucursal ya existe")
    
    try:
        sucursal = SucursalService.create(db, data.codigo, data.nombre)
        return {
            "ok": True,
            "mensaje": "Sucursal creada correctamente",
            "sucursal": {"codigo": sucursal.codigo, "nombre": sucursal.nombre}
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al crear sucursal: {str(e)}")


@router.put("/api/sucursales/{codigo}")
def editar_sucursal(
    codigo: str,
    data: SucursalUpdate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    """Editar sucursal existente"""
    if user.rol.lower() != "admin":
        raise HTTPException(status_code=403, detail="Acceso denegado")
    
    sucursal = SucursalService.update(db, codigo, data.nombre)
    if not sucursal:
        raise HTTPException(status_code=404, detail="Sucursal no encontrada")
    
    return {
        "ok": True,
        "mensaje": "Sucursal actualizada correctamente",
        "sucursal": {"codigo": sucursal.codigo, "nombre": sucursal.nombre}
    }


@router.delete("/api/sucursales/{codigo}")
def eliminar_sucursal(
    codigo: str,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    """Eliminar sucursal"""
    if user.rol.lower() != "admin":
        raise HTTPException(status_code=403, detail="Acceso denegado")
    
    # Verificar si hay verificaciones asociadas
    from backend.models.verificacion import Verificacion
    verificaciones_count = db.query(Verificacion).filter(Verificacion.merchant_code == codigo).count()
    
    if verificaciones_count > 0:
        raise HTTPException(
            status_code=400,
            detail=f"No se puede eliminar. Hay {verificaciones_count} SMS asociados a esta sucursal"
        )
    
    if SucursalService.delete(db, codigo):
        return {"ok": True, "mensaje": "Sucursal eliminada correctamente"}
    else:
        raise HTTPException(status_code=404, detail="Sucursal no encontrada")
