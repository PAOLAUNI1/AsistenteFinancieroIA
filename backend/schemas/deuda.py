from datetime import date

from pydantic import BaseModel, ConfigDict, Field


class HipotecarioIn(BaseModel):
    entidad: str
    monto_inicial: float = Field(gt=0)
    saldo_actual: float = Field(gt=0)
    tasa: float = Field(gt=0)
    periodicidad_tasa: str = "Efectiva anual (EA)"
    tipo_tasa: str = "Fija"
    anos: int = Field(ge=0, default=0)
    meses: int = Field(ge=0, le=11, default=0)
    valor_cuota: float = Field(gt=0)
    cuota_proxima: int = Field(ge=1, default=1)
    proximo_pago: date


class TarjetaIn(BaseModel):
    entidad: str
    franquicia: str = "Visa"
    cupo_total: float = Field(gt=0)
    saldo_actual: float = Field(gt=0)
    tasa: float = Field(ge=0)
    periodicidad_tasa: str = "Mensual vencido (MV)"
    pago_minimo: float = Field(gt=0)
    cuota_manejo: float = 0.0
    dia_corte: int = Field(ge=1, le=31, default=15)
    proximo_pago: date


class VehiculoIn(BaseModel):
    entidad: str
    monto_inicial: float = Field(gt=0)
    saldo_actual: float = Field(gt=0)
    tasa: float = Field(ge=0)
    periodicidad_tasa: str = "Efectiva anual (EA)"
    anos: int = Field(ge=0, default=0)
    meses: int = Field(ge=0, le=11, default=0)
    valor_cuota: float = Field(gt=0)
    cuota_proxima: int = Field(ge=1, default=1)
    proximo_pago: date


class EducativoIn(BaseModel):
    entidad: str
    carrera: str = ""
    estado_credito: str = "En amortización (Pagando cuota completa)"
    cuotas_pendientes: int = Field(ge=1, le=360, default=24)
    monto_inicial: float = Field(ge=0, default=0)
    saldo_actual: float = Field(gt=0)
    tasa: float = Field(ge=0)
    periodicidad_tasa: str = "Efectiva anual (EA)"
    valor_cuota: float = Field(gt=0)
    proximo_pago: date


class LibreInversionIn(BaseModel):
    entidad: str
    monto_inicial: float = Field(gt=0)
    saldo_actual: float = Field(gt=0)
    tasa: float = Field(ge=0)
    periodicidad_tasa: str = "Efectiva anual (EA)"
    total_meses: int = Field(ge=1, le=120, default=36)
    cuota_proxima: int = Field(ge=1, default=1)
    valor_cuota: float = Field(gt=0)
    proximo_pago: date


class PrestamoPersonalIn(BaseModel):
    prestamista: str
    tipo_relacion: str = "Familiar"
    monto_inicial: float = Field(ge=0, default=0)
    saldo_actual: float = Field(gt=0)
    tasa: float = Field(ge=0, default=0)
    valor_cuota: float = Field(gt=0)
    proximo_pago: date


class ConsumoIn(BaseModel):
    entidad: str
    articulo: str = ""
    monto_inicial: float = Field(ge=0, default=0)
    saldo_actual: float = Field(gt=0)
    tasa: float = Field(ge=0)
    periodicidad_tasa: str = "Mensual"
    total_cuotas: int = Field(ge=1, le=72, default=12)
    cuota_proxima: int = Field(ge=1, default=1)
    valor_cuota: float = Field(gt=0)
    proximo_pago: date


class DeudaOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    tipo: str
    icono: str
    entidad: str
    monto_inicial: float
    saldo_actual: float
    tasa: float
    periodicidad_tasa: str
    tipo_tasa: str
    anos: int
    meses: int
    total_cuotas: str
    cuota_proxima: int
    cuotas_pendientes: str
    valor_cuota: float
    proximo_pago: str
    detalle: dict
