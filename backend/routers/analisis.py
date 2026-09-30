from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.deps import usuario_actual
from backend.models import Deuda, Usuario
from backend.services.analisis import calcular_analisis
from backend.services.perfil import obtener_meta_principal, obtener_perfil

router = APIRouter(tags=["analisis"])


class AnalisisIn(BaseModel):
    """
    Único dato que no vive en el perfil persistido: "Compras no esenciales"
    (app.py, sección inferior del prototipo) se ingresa al momento de pedir
    el análisis, igual que hoy en Streamlit.
    """

    compras_no_esenciales: float = Field(ge=0, default=0.0)


@router.post("/analisis")
def obtener_analisis(
    payload: AnalisisIn,
    usuario: Usuario = Depends(usuario_actual),
    db: Session = Depends(get_db),
):
    perfil = obtener_perfil(db, usuario)
    meta = obtener_meta_principal(db, usuario)

    saldos = (
        db.query(Deuda.saldo_actual)
        .filter(Deuda.usuario_id == usuario.id, Deuda.estado == "ACTIVA")
        .all()
    )
    total_deuda = sum(float(saldo) for (saldo,) in saldos)

    return calcular_analisis(
        salario=perfil["salario_mensual"],
        otros_ingresos=perfil["otros_ingresos"],
        alimentacion=perfil["alimentacion"],
        transporte=perfil["transporte"],
        vestimenta=perfil["vestimenta"],
        entretenimiento=perfil["entretenimiento"],
        arriendo=perfil["arriendo_hipoteca"],
        servicios=perfil["servicios_publicos"],
        colegio=perfil["pago_colegio"],
        universidad=perfil["pago_universidad"],
        compras=payload.compras_no_esenciales,
        meta_ahorro_anual=float(meta.monto_objetivo) if meta else 0.0,
        deuda_total=total_deuda,
    )
