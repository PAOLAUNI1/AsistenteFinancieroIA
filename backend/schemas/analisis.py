from pydantic import BaseModel

from backend.schemas.perfil import Monto


class AnalisisIn(BaseModel):
    """
    Único dato que no vive en el perfil persistido: "Compras no esenciales"
    (app.py, sección inferior del prototipo) se ingresa al momento de pedir
    el análisis, igual que hoy en Streamlit.
    """

    compras_no_esenciales: Monto = 0.0


class AnalisisOut(BaseModel):
    ingresos_totales: float
    gastos_totales: float
    saldo_disponible: float
    porcentaje_gasto: float
    score_financiero: int
    nivel_gasto: str
    deuda_total: float
    pago_sugerido_deuda: float
    ahorro_semanal_sugerido: float
    ahorro_mensual_sugerido: float
    ahorro_anual_proyectado: float
    meta_ahorro_anual: float
    # None cuando no hay una meta de ahorro definida.
    meta_alcanzable: bool | None
