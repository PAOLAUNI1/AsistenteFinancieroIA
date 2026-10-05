from datetime import date
from typing import Literal

from pydantic import BaseModel, Field

PeriodicidadTasa = Literal["EA", "MENSUAL"]
TipoTasa = Literal["FIJA", "VARIABLE"]


class HipotecarioIn(BaseModel):
    entidad: str
    monto_inicial: float = Field(gt=0)
    saldo_actual: float = Field(gt=0)
    tasa: float = Field(gt=0)
    periodicidad_tasa: PeriodicidadTasa = "EA"
    tipo_tasa: TipoTasa = "FIJA"
    anos: int = Field(ge=0, default=0)
    meses: int = Field(ge=0, le=11, default=0)
    valor_cuota: float = Field(gt=0)
    cuota_proxima: int = Field(ge=1, default=1)
    proximo_pago: date
    nombre: str | None = Field(default=None, max_length=100)
    fecha_inicio: date | None = None
    descripcion: str | None = Field(default=None, max_length=200)
    # False deja la deuda en estado CANCELADA: no cuenta en el análisis.
    activa: bool = True


class TarjetaIn(BaseModel):
    entidad: str
    franquicia: str = "Visa"
    ultimos_digitos: str | None = Field(default=None, max_length=4)
    cupo_total: float = Field(gt=0)
    saldo_actual: float = Field(gt=0)
    tasa: float = Field(ge=0)
    periodicidad_tasa: PeriodicidadTasa = "MENSUAL"
    pago_minimo: float = Field(gt=0)
    cuota_manejo: float = 0.0
    dia_corte: int = Field(ge=1, le=31, default=15)
    dia_pago: int = Field(ge=1, le=31, default=5)
    proximo_pago: date


class VehiculoIn(BaseModel):
    entidad: str
    monto_inicial: float = Field(gt=0)
    saldo_actual: float = Field(gt=0)
    tasa: float = Field(ge=0)
    periodicidad_tasa: PeriodicidadTasa = "EA"
    anos: int = Field(ge=0, default=0)
    meses: int = Field(ge=0, le=11, default=0)
    valor_cuota: float = Field(gt=0)
    cuota_proxima: int = Field(ge=1, default=1)
    proximo_pago: date
    tipo_vehiculo: Literal["AUTOMOVIL", "MOTOCICLETA", "CAMIONETA", "OTRO"] = "AUTOMOVIL"
    marca: str | None = None
    modelo: str | None = None
    anio: int | None = Field(default=None, ge=1950, le=2100)
    placa: str | None = None


class EducativoIn(BaseModel):
    entidad: str
    carrera: str = ""
    modalidad: str = "En amortización"
    cuotas_pendientes: int = Field(ge=1, le=360, default=24)
    monto_inicial: float = Field(ge=0, default=0)
    saldo_actual: float = Field(gt=0)
    tasa: float = Field(ge=0)
    periodicidad_tasa: PeriodicidadTasa = "EA"
    valor_cuota: float = Field(gt=0)
    proximo_pago: date


class LibreInversionIn(BaseModel):
    entidad: str
    monto_inicial: float = Field(gt=0)
    saldo_actual: float = Field(gt=0)
    tasa: float = Field(ge=0)
    periodicidad_tasa: PeriodicidadTasa = "EA"
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
    periodicidad_tasa: PeriodicidadTasa = "MENSUAL"
    total_cuotas: int = Field(ge=1, le=72, default=12)
    cuota_proxima: int = Field(ge=1, default=1)
    valor_cuota: float = Field(gt=0)
    proximo_pago: date


class DeudaOut(BaseModel):
    id: int
    tipo_codigo: str
    tipo_nombre: str
    icono: str | None
    entidad: str
    monto_inicial: float | None
    saldo_actual: float
    tiene_intereses: bool
    tasa_interes: float | None
    periodicidad_tasa: str | None
    tipo_tasa: str | None
    plazo_meses: int | None
    valor_cuota: float | None
    proxima_cuota: int | None
    cuotas_pendientes: int | None
    fecha_proximo_pago: date | None
    estado: str
    nombre: str | None = None
    fecha_inicio: date | None = None
    descripcion: str | None = None
    detalle: dict
