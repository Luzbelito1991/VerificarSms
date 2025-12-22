"""
📊 Rutas para Registros del Sistema y Configuración
"""
from fastapi import APIRouter, Request, Depends, HTTPException, File, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import func, case
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv, set_key

from backend.database import get_db
from backend.models import Usuario, Verificacion
from backend.auth_utils import get_current_user

load_dotenv()

router = APIRouter()

# ============================================================
# 📱 VISTA: Uso de SMS
# ============================================================
@router.get("/registros/uso", response_class=HTMLResponse)
async def vista_uso_sms(
    request: Request,
    user = Depends(get_current_user)
):
    """Vista para ver el uso de SMS disponibles"""
    if user.rol.lower() != "admin":
        raise HTTPException(status_code=403, detail="Acceso denegado")
    
    from backend.main import templates
    
    return templates.TemplateResponse(
        "registros/uso_sms.html",
        {
            "request": request,
            "user": user,
            "active_page": "uso"
        }
    )


@router.get("/api/registros/uso")
async def obtener_uso_sms(
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    """Obtener estadísticas de uso de SMS"""
    if user.rol.lower() != "admin":
        raise HTTPException(status_code=403, detail="Acceso denegado")
    
    try:
        # Total de SMS enviados
        total_enviados = db.query(Verificacion).count()
        
        # SMS del mes actual
        hoy = datetime.now()
        primer_dia_mes = datetime(hoy.year, hoy.month, 1)
        sms_mes_actual = db.query(Verificacion).filter(
            Verificacion.fecha >= primer_dia_mes
        ).count()
        
        # SMS de hoy
        inicio_hoy = datetime(hoy.year, hoy.month, hoy.day)
        sms_hoy = db.query(Verificacion).filter(
            Verificacion.fecha >= inicio_hoy
        ).count()
        
        # SMS por sucursal (top 5)
        sms_por_sucursal = db.query(
            Verificacion.merchant_code,
            func.count(Verificacion.id).label('total')
        ).group_by(
            Verificacion.merchant_code
        ).order_by(
            func.count(Verificacion.id).desc()
        ).limit(5).all()
        
        # Últimos 7 días
        hace_7_dias = hoy - timedelta(days=7)
        sms_ultimos_7_dias = []
        for i in range(7):
            fecha = hace_7_dias + timedelta(days=i)
            inicio_dia = datetime(fecha.year, fecha.month, fecha.day)
            fin_dia = inicio_dia + timedelta(days=1)
            
            count = db.query(Verificacion).filter(
                Verificacion.fecha >= inicio_dia,
                Verificacion.fecha < fin_dia
            ).count()
            
            sms_ultimos_7_dias.append({
                "fecha": fecha.strftime("%d/%m"),
                "cantidad": count
            })
        
        return {
            "ok": True,
            "datos": {
                "total_enviados": total_enviados,
                "sms_mes_actual": sms_mes_actual,
                "sms_hoy": sms_hoy,
                "sms_por_sucursal": [
                    {"sucursal": s.merchant_code, "total": s.total}
                    for s in sms_por_sucursal
                ],
                "ultimos_7_dias": sms_ultimos_7_dias,
                # Datos simulados del plan (se pueden ajustar según API real)
                "plan_contratado": {
                    "nombre": "Plan Empresarial",
                    "sms_incluidos": 10000,
                    "sms_usados": total_enviados,
                    "sms_disponibles": max(0, 10000 - total_enviados),
                    "porcentaje_uso": min(100, (total_enviados / 10000) * 100) if total_enviados > 0 else 0
                }
            }
        }
    except Exception as e:
        return {"ok": False, "mensaje": f"Error al obtener datos de uso: {str(e)}"}


# ============================================================
# 📊 VISTA: Métricas
# ============================================================
@router.get("/registros/metricas", response_class=HTMLResponse)
async def vista_metricas(
    request: Request,
    user = Depends(get_current_user)
):
    """Vista para ver métricas del sistema"""
    if user.rol.lower() != "admin":
        raise HTTPException(status_code=403, detail="Acceso denegado")
    
    from backend.main import templates
    
    return templates.TemplateResponse(
        "registros/metricas.html",
        {
            "request": request,
            "user": user,
            "active_page": "metricas"
        }
    )


@router.get("/api/registros/metricas")
async def obtener_metricas(
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    """Obtener métricas del sistema"""
    if user.rol.lower() != "admin":
        raise HTTPException(status_code=403, detail="Acceso denegado")
    
    try:
        # SMS por usuario operador
        sms_por_usuario = db.query(
            Usuario.usuario,
            func.count(Verificacion.id).label('total')
        ).join(
            Verificacion, Usuario.id == Verificacion.usuario_id
        ).group_by(
            Usuario.usuario
        ).order_by(
            func.count(Verificacion.id).desc()
        ).all()
        
        # Tasa de éxito/fallo
        total_sms = db.query(Verificacion).count()
        
        # Simulamos éxitos/fallos basándonos en si tienen código
        # (ajustar según tu lógica real)
        exitosos = db.query(Verificacion).filter(
            Verificacion.verification_code.isnot(None)
        ).count()
        
        fallidos = total_sms - exitosos
        
        tasa_exito = (exitosos / total_sms * 100) if total_sms > 0 else 0
        tasa_fallo = (fallidos / total_sms * 100) if total_sms > 0 else 0
        
        # SMS por hora del día (últimas 24 horas)
        ahora = datetime.now()
        hace_24h = ahora - timedelta(hours=24)
        
        sms_por_hora = db.query(
            func.strftime('%H', Verificacion.fecha).label('hora'),
            func.count(Verificacion.id).label('total')
        ).filter(
            Verificacion.fecha >= hace_24h
        ).group_by(
            func.strftime('%H', Verificacion.fecha)
        ).all()
        
        return {
            "ok": True,
            "datos": {
                "sms_por_usuario": [
                    {"usuario": s.usuario, "total": s.total}
                    for s in sms_por_usuario
                ],
                "tasa_exito_fallo": {
                    "exitosos": exitosos,
                    "fallidos": fallidos,
                    "tasa_exito": round(tasa_exito, 2),
                    "tasa_fallo": round(tasa_fallo, 2),
                    "total": total_sms
                },
                "sms_por_hora": [
                    {"hora": f"{s.hora}:00", "total": s.total}
                    for s in sms_por_hora
                ]
            }
        }
    except Exception as e:
        return {"ok": False, "mensaje": f"Error al obtener métricas: {str(e)}"}


# ============================================================
# ⚙️ VISTA: Configuración
# ============================================================
@router.get("/configuracion", response_class=HTMLResponse)
async def vista_configuracion(
    request: Request,
    user = Depends(get_current_user)
):
    """Vista de configuración del sistema"""
    if user.rol.lower() != "admin":
        raise HTTPException(status_code=403, detail="Acceso denegado")
    
    from backend.main import templates
    
    # Leer configuración actual
    sms_modo_simulado = os.getenv("SMS_MODO_SIMULADO", "false").lower() == "true"
    sms_api_key = os.getenv("SMS_API_KEY", "")
    
    return templates.TemplateResponse(
        "registros/configuracion.html",
        {
            "request": request,
            "user": user,
            "active_page": "configuracion",
            "sms_modo_simulado": sms_modo_simulado,
            "sms_api_key": sms_api_key
        }
    )


@router.post("/api/configuracion/modo-simulado")
async def cambiar_modo_simulado(
    request: Request,
    user = Depends(get_current_user)
):
    """Activar/desactivar modo simulado de SMS"""
    if user.rol.lower() != "admin":
        raise HTTPException(status_code=403, detail="Acceso denegado")
    
    try:
        data = await request.json()
        activar = data.get("activar", False)
        
        # Actualizar archivo .env
        env_path = ".env"
        if os.path.exists(env_path):
            set_key(env_path, "SMS_MODO_SIMULADO", str(activar).lower())
            
            # Recargar variables de entorno
            load_dotenv(override=True)
            
            return {
                "ok": True,
                "mensaje": f"Modo simulado {'activado' if activar else 'desactivado'} correctamente",
                "modo_simulado": activar
            }
        else:
            return {"ok": False, "mensaje": "Archivo .env no encontrado"}
    except Exception as e:
        return {"ok": False, "mensaje": f"Error al cambiar configuración: {str(e)}"}


@router.post("/api/configuracion/api-key")
async def actualizar_api_key(
    request: Request,
    user = Depends(get_current_user)
):
    """Actualizar API Key de SMS Masivos"""
    if user.rol.lower() != "admin":
        raise HTTPException(status_code=403, detail="Acceso denegado")
    
    try:
        data = await request.json()
        nueva_api_key = data.get("api_key", "")
        
        if not nueva_api_key:
            return {"ok": False, "mensaje": "La API Key no puede estar vacía"}
        
        # Actualizar archivo .env
        env_path = ".env"
        if os.path.exists(env_path):
            set_key(env_path, "SMS_API_KEY", nueva_api_key)
            
            # Recargar variables de entorno
            load_dotenv(override=True)
            
            return {
                "ok": True,
                "mensaje": "API Key actualizada correctamente"
            }
        else:
            return {"ok": False, "mensaje": "Archivo .env no encontrado"}
    except Exception as e:
        return {"ok": False, "mensaje": f"Error al actualizar API Key: {str(e)}"}


@router.get("/api/configuracion/descargar-backup")
async def descargar_backup(
    request: Request,
    user = Depends(get_current_user)
):
    """Descargar copia de seguridad de la base de datos"""
    if user.rol.lower() != "admin":
        raise HTTPException(status_code=403, detail="Acceso denegado")
    
    from pathlib import Path
    from datetime import datetime
    from fastapi.responses import FileResponse
    
    try:
        db_path = Path("usuarios.db")
        
        if not db_path.exists():
            raise HTTPException(status_code=404, detail="Base de datos no encontrada")
        
        # Nombre con timestamp para el archivo descargado
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"verificarsms_backup_{timestamp}.db"
        
        print(f"📥 Descargando backup: {filename}")
        
        # Devolver archivo para descarga
        return FileResponse(
            path=str(db_path),
            filename=filename,
            media_type="application/octet-stream"
        )
        
    except Exception as e:
        print(f"❌ Error al descargar backup: {e}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.post("/api/configuracion/restaurar-backup")
async def restaurar_backup(
    file: bytes = File(...),
    user = Depends(get_current_user)
):
    """Restaurar base de datos desde un archivo subido"""
    if user.rol.lower() != "admin":
        raise HTTPException(status_code=403, detail="Acceso denegado")
    
    import shutil
    from pathlib import Path
    from datetime import datetime
    
    try:
        db_path = Path("usuarios.db")
        backup_dir = Path("backups")
        backup_dir.mkdir(exist_ok=True)
        
        # Crear backup de seguridad antes de restaurar
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        seguridad_path = backup_dir / f"usuarios_pre_restore_{timestamp}.db"
        shutil.copy2(db_path, seguridad_path)
        
        print(f"✅ Backup de seguridad creado: {seguridad_path.name}")
        
        # Guardar el archivo subido como nueva base de datos
        with open(db_path, 'wb') as f:
            f.write(file)
        
        print(f"✅ Base de datos restaurada desde archivo subido")
        
        return JSONResponse(
            content={
                "ok": True,
                "mensaje": "Base de datos restaurada correctamente"
            },
            status_code=200
        )
        
    except Exception as e:
        print(f"❌ Error al restaurar backup: {e}")
        import traceback
        traceback.print_exc()
        
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
