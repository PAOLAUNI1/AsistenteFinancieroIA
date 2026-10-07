from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

from backend.schemas.deuda import MAX_MONTO, MontoPositivo

Monto = Annotated[float, Field(ge=0, le=MAX_MONTO, allow_inf_nan=False)]


class PerfilIn(BaseModel):
    salario_mensual: Monto = 0.0
    otros_ingresos: Monto = 0.0
    cantidad_hijos: int = Field(ge=0, le=30, default=0)
    pago_colegio: Monto = 0.0
    pago_universidad: Monto = 0.0
    alimentacion: Monto = 0.0
    transporte: Monto = 0.0
    vestimenta: Monto = 0.0
    entretenimiento: Monto = 0.0
    arriendo_hipoteca: Monto = 0.0
    servicios_publicos: Monto = 0.0


class PerfilOut(PerfilIn):
    usuario_id: int


class MetaAhorroIn(BaseModel):
    monto_objetivo: MontoPositivo


class MetaAhorroOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int | None
    usuario_id: int
    monto_objetivo: float
    monto_actual: float
