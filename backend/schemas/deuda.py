from datetime import date
from typing import Annotated, Literal

from pydantic import AfterValidator, BaseModel, Field

# Límites alineados con las columnas de MySQL (decimal(15,2), decimal(7,4), varchar, ...)
# para que un dato fuera de rango dé 422 y no un error de base de datos.
MAX_MONTO = 9_999_999_999_999
MAX_TASA = 100.0
MAX_ANOS = 40


def _a_cuatro_decimales(valor: float) -> float:
    # La columna guarda 4 decimales: una tasa como 0,00001 quedaría en 0 con "intereses".
    return round(valor, 4)


MontoPositivo = Annotated[float, Field(gt=0, le=MAX_MONTO, allow_inf_nan=False)]
MontoNoNegativo = Annotated[float, Field(ge=0, le=MAX_MONTO, allow_inf_nan=False)]
TasaPositiva = Annotated[
    float, AfterValidator(_a_cuatro_decimales), Field(gt=0, le=MAX_TASA, allow_inf_nan=False)
]
TasaNoNegativa = Annotated[
    float, AfterValidator(_a_cuatro_decimales), Field(ge=0, le=MAX_TASA, allow_inf_nan=False)
]

PeriodicidadTasa = Literal["EA", "MENSUAL"]
TipoTasa = Literal["FIJA", "VARIABLE"]


class HipotecarioIn(BaseModel):
    entidad: str = Field(max_length=100)
    monto_inicial: MontoPositivo
    saldo_actual: MontoPositivo
    tasa: TasaPositiva
    periodicidad_tasa: PeriodicidadTasa = "EA"
    tipo_tasa: TipoTasa = "FIJA"
    anos: int = Field(ge=0, le=MAX_ANOS, default=0)
    meses: int = Field(ge=0, le=11, default=0)
    valor_cuota: MontoPositivo
    cuota_proxima: int = Field(ge=1, default=1)
    proximo_pago: date
    nombre: str | None = Field(default=None, max_length=100)
    fecha_inicio: date | None = None
    descripcion: str | None = Field(default=None, max_length=200)
    # False deja la deuda en estado CANCELADA: no cuenta en el análisis.
    activa: bool = True


class TarjetaIn(BaseModel):
    entidad: str = Field(max_length=100)
    franquicia: str | None = Field(default=None, max_length=30)
    ultimos_digitos: str | None = Field(default=None, max_length=4)
    cupo_total: MontoPositivo
    saldo_actual: MontoPositivo
    tasa: TasaNoNegativa
    periodicidad_tasa: PeriodicidadTasa = "MENSUAL"
    # Opcionales: la app móvil no los pide al registrar; si no llegan, el pago mínimo
    # queda sin definir (0) y la fecha del próximo pago se calcula con el día de pago.
    pago_minimo: MontoNoNegativo = 0.0
    cuota_manejo: MontoNoNegativo = 0.0
    dia_corte: int = Field(ge=1, le=31, default=15)
    dia_pago: int = Field(ge=1, le=31, default=5)
    proximo_pago: date | None = None
    nombre: str | None = Field(default=None, max_length=100)
    descripcion: str | None = Field(default=None, max_length=200)
    # False deja la tarjeta en estado CANCELADA: no cuenta en el análisis.
    activa: bool = True


class VehiculoIn(BaseModel):
    entidad: str = Field(max_length=100)
    monto_inicial: MontoPositivo
    saldo_actual: MontoPositivo
    tasa: TasaNoNegativa
    periodicidad_tasa: PeriodicidadTasa = "EA"
    anos: int = Field(ge=0, le=MAX_ANOS, default=0)
    meses: int = Field(ge=0, le=11, default=0)
    valor_cuota: MontoPositivo
    cuota_proxima: int = Field(ge=1, default=1)
    proximo_pago: date
    # "OTRO" cuando no se indica: la app móvil no pregunta por el tipo de vehículo.
    tipo_vehiculo: Literal["AUTOMOVIL", "MOTOCICLETA", "CAMIONETA", "OTRO"] = "OTRO"
    marca: str | None = Field(default=None, max_length=50)
    modelo: str | None = Field(default=None, max_length=50)
    anio: int | None = Field(default=None, ge=1950, le=2100)
    placa: str | None = Field(default=None, max_length=10)
    nombre: str | None = Field(default=None, max_length=100)
    fecha_inicio: date | None = None
    descripcion: str | None = Field(default=None, max_length=200)
    # False deja la deuda en estado CANCELADA: no cuenta en el análisis.
    activa: bool = True


class EducativoIn(BaseModel):
    entidad: str = Field(max_length=100)
    carrera: str | None = Field(default=None, max_length=120)  # programa o concepto
    modalidad: str = Field(default="En amortización", max_length=80)
    # Contrato anterior: solo cuotas por pagar (el plazo total era igual a ese valor).
    cuotas_pendientes: int | None = Field(ge=1, le=360, default=None)
    # Contrato de la app: plazo total en meses y la próxima cuota a pagar.
    plazo_meses: int | None = Field(ge=1, le=360, default=None)
    cuota_proxima: int = Field(ge=1, default=1)
    monto_inicial: MontoNoNegativo = 0
    saldo_actual: MontoPositivo
    tasa: TasaNoNegativa
    periodicidad_tasa: PeriodicidadTasa = "EA"
    valor_cuota: MontoPositivo
    proximo_pago: date
    nombre: str | None = Field(default=None, max_length=100)
    fecha_inicio: date | None = None
    descripcion: str | None = Field(default=None, max_length=200)
    # False deja la deuda en estado CANCELADA: no cuenta en el análisis.
    activa: bool = True


TipoCreditoOtro = Literal["PRESTAMO_FAMILIAR", "PRESTAMO_AMIGO", "CREDITO_COMERCIO", "OTRO"]


class OtrosIn(BaseModel):
    # Entidad o persona a quien se le debe.
    entidad: str = Field(max_length=100)
    tipo_credito: TipoCreditoOtro = "OTRO"
    nombre: str | None = Field(default=None, max_length=100)
    monto_inicial: MontoPositivo
    saldo_actual: MontoPositivo
    tasa: TasaNoNegativa = 0.0
    periodicidad_tasa: PeriodicidadTasa = "EA"
    plazo_meses: int = Field(ge=1, le=360)
    cuota_proxima: int = Field(ge=1, default=1)
    valor_cuota: MontoPositivo
    fecha_inicio: date | None = None
    proximo_pago: date
    descripcion: str | None = Field(default=None, max_length=200)
    # False deja la deuda en estado CANCELADA: no cuenta en el análisis.
    activa: bool = True


class LibreInversionIn(BaseModel):
    entidad: str = Field(max_length=100)
    monto_inicial: MontoPositivo
    saldo_actual: MontoPositivo
    tasa: TasaNoNegativa
    periodicidad_tasa: PeriodicidadTasa = "EA"
    total_meses: int = Field(ge=1, le=120, default=36)
    cuota_proxima: int = Field(ge=1, default=1)
    valor_cuota: MontoPositivo
    proximo_pago: date


class PrestamoPersonalIn(BaseModel):
    prestamista: str = Field(max_length=60)
    tipo_relacion: str = Field(default="Familiar", max_length=30)
    monto_inicial: MontoNoNegativo = 0
    saldo_actual: MontoPositivo
    tasa: TasaNoNegativa = 0
    valor_cuota: MontoPositivo
    proximo_pago: date


class ConsumoIn(BaseModel):
    entidad: str = Field(max_length=100)
    articulo: str = Field(default="", max_length=30)
    monto_inicial: MontoNoNegativo = 0
    saldo_actual: MontoPositivo
    tasa: TasaNoNegativa
    periodicidad_tasa: PeriodicidadTasa = "MENSUAL"
    total_cuotas: int = Field(ge=1, le=72, default=12)
    cuota_proxima: int = Field(ge=1, default=1)
    valor_cuota: MontoPositivo
    proximo_pago: date


class DeudaOut(BaseModel):
    id: int
    tipo_codigo: str
    tipo_nombre: str
    icono: str | None
    entidad: str = Field(max_length=100)
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
