from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import Deuda, MetaAhorro, Perfil
from backend.services.analisis import calcular_analisis
from backend.services.perfil import obtener_o_crear_meta, obtener_o_crear_perfil

router = APIRouter(tags=["analisis"])


class AnalisisIn(BaseModel):
    """
    Único dato que no vive en el perfil persistido: "Compras no esenciales"
    (app.py, sección inferior del prototipo) se ingresa al momento de pedir
    el análisis, igual que hoy en Streamlit.
    """

    compras_no_esenciales: float = Field(ge=0, default=0.0)


@router.post("/analisis")
def obtener_analisis(payload: AnalisisIn, db: Session = Depends(get_db)):
    perfil: Perfil = obtener_o_crear_perfil(db)
    meta: MetaAhorro = obtener_o_crear_meta(db)
    deuda_total = db.query(Deuda).with_entities(Deuda.saldo_actual).all()
    total_deuda = sum(saldo for (saldo,) in deuda_total)

    return calcular_analisis(
        salario=perfil.salario_mensual,
        otros_ingresos=perfil.otros_ingresos,
        alimentacion=perfil.alimentacion,
        transporte=perfil.transporte,
        vestimenta=perfil.vestimenta,
        entretenimiento=perfil.entretenimiento,
        arriendo=perfil.arriendo_hipoteca,
        servicios=perfil.servicios_publicos,
        colegio=perfil.pago_colegio,
        universidad=perfil.pago_universidad,
        compras=payload.compras_no_esenciales,
        meta_ahorro_anual=meta.monto_objetivo,
        deuda_total=total_deuda,
    )
