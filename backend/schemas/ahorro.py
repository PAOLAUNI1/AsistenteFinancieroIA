from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, computed_field

from backend.schemas.comunes import MontoNoNegativo, MontoPositivo, TasaNoNegativa, TasaPositiva

# Subtipos del flujo "Otro tipo de ahorro" (pantalla 3 del diseño).
SubtipoOtro = Literal[
    "EFECTIVO", "DOLARES", "PLAN", "PENSION", "VIAJE", "VIVIENDA", "EMERGENCIAS", "PERSONALIZADO"
]
# Subtipos de alcancía: el propósito que se le da (pantalla 3 del diseño de alcancía).
SubtipoAlcancia = Literal[
    "META_PERSONALIZADA", "VACACIONES", "EMERGENCIAS", "EDUCACION", "VIVIENDA", "OTRO"
]
# Subtipos de ahorro programado: el objetivo de la meta (pantalla 3 del diseño de ahorro programado).
SubtipoProgramado = Literal["META_PERSONALIZADA", "VIAJES", "ESTUDIOS", "EMERGENCIAS", "OTRO_OBJETIVO"]
Moneda = Literal["COP", "USD", "EUR"]
MetodoAhorro = Literal["MANUAL", "PROGRAMADO", "AUTOMATICO"]
# La alcancía admite además ahorrar el cambio de los gastos.
MetodoAlcancia = Literal["MANUAL", "PROGRAMADO", "REDONDEO", "AUTOMATICO"]
# El ahorro programado se cumple con una transferencia automática o con un recordatorio.
MetodoProgramado = Literal["AUTOMATICO", "RECORDATORIO"]
PeriodicidadAhorro = Literal["SEMANAL", "QUINCENAL", "MENSUAL"]
# Subtipos de fondo de inversión: el tipo de fondo (pantalla de información básica del diseño).
SubtipoFondo = Literal["RENTA_FIJA", "RENTA_VARIABLE", "MIXTO", "OTRO"]
PlazoFondo = Literal["CORTO", "MEDIANO", "LARGO"]
TipoRentabilidad = Literal["FIJA", "VARIABLE"]
# CDT: el tipo de tasa es el subtipo del ahorro; las instrucciones dicen qué se renueva al vencer.
TipoTasaCdt = Literal["FIJA", "VARIABLE"]
InstruccionRenovacion = Literal["MISMO_MONTO", "CAPITAL_E_INTERESES", "SOLO_CAPITAL"]
# Cuenta de ahorro: el tipo de cuenta es el subtipo del ahorro.
TipoCuenta = Literal["AHORROS", "NOMINA", "DIGITAL", "OTRA"]


class AhorroOtroIn(BaseModel):
    subtipo: SubtipoOtro
    nombre: str = Field(max_length=100)
    descripcion: str | None = Field(default=None, max_length=200)
    monto_actual: MontoNoNegativo = 0.0
    moneda: Moneda = "COP"
    # Meta opcional: solo se usa cuando es_meta es verdadero.
    es_meta: bool = False
    meta_nombre: str | None = Field(default=None, max_length=100)
    monto_objetivo: MontoPositivo | None = None
    fecha_objetivo: date | None = None
    metodo: MetodoAhorro = "MANUAL"


class AhorroAlcanciaIn(BaseModel):
    subtipo: SubtipoAlcancia
    nombre: str = Field(max_length=100)
    descripcion: str | None = Field(default=None, max_length=200)
    # Una alcancía siempre tiene meta: el monto objetivo es obligatorio.
    monto_objetivo: MontoPositivo
    moneda: Moneda = "COP"
    fecha_objetivo: date | None = None
    metodo: MetodoAlcancia = "MANUAL"
    # Con cuánto se abre la alcancía (será el monto actual).
    aporte_inicial: MontoNoNegativo = 0.0


class AhorroProgramadoIn(BaseModel):
    subtipo: SubtipoProgramado
    nombre: str = Field(max_length=100)
    descripcion: str | None = Field(default=None, max_length=200)
    # Siempre es una meta: el monto objetivo y la fecha objetivo son obligatorios.
    monto_objetivo: MontoPositivo
    monto_inicial: MontoNoNegativo = 0.0
    moneda: Moneda = "COP"
    monto_periodo: MontoPositivo
    periodicidad: PeriodicidadAhorro = "MENSUAL"
    fecha_inicio: date
    fecha_objetivo: date
    metodo: MetodoProgramado = "AUTOMATICO"


class AhorroFondoIn(BaseModel):
    # El tipo de fondo es el subtipo del ahorro.
    subtipo: SubtipoFondo
    entidad: str = Field(max_length=100)
    nombre: str = Field(max_length=100)
    descripcion: str | None = Field(default=None, max_length=200)
    # Con cuánto se entra al fondo (será el monto actual).
    monto_inicial: MontoPositivo
    moneda: Moneda = "COP"
    fecha_inversion: date
    plazo_sugerido: PlazoFondo | None = None
    # Tasa de rendimiento esperada, efectiva anual (porcentaje).
    tasa_rendimiento: TasaNoNegativa
    tipo_rentabilidad: TipoRentabilidad = "VARIABLE"
    reinversion: bool = False


class AhorroCuentaIn(BaseModel):
    tipo_cuenta: TipoCuenta = "AHORROS"
    entidad: str = Field(max_length=100)
    nombre: str = Field(max_length=100)
    descripcion: str | None = Field(default=None, max_length=200)
    monto_actual: MontoNoNegativo = 0.0
    moneda: Moneda = "COP"
    # Meta opcional: solo se usa cuando es_meta es verdadero.
    es_meta: bool = False
    meta_nombre: str | None = Field(default=None, max_length=100)
    monto_objetivo: MontoPositivo | None = None
    fecha_objetivo: date | None = None


class AhorroCdtIn(BaseModel):
    tipo_tasa: TipoTasaCdt = "FIJA"
    entidad: str = Field(max_length=100)
    nombre: str = Field(max_length=100)
    descripcion: str | None = Field(default=None, max_length=200)
    # Lo invertido en el CDT (será el monto actual).
    monto: MontoPositivo
    moneda: Moneda = "COP"
    # Tasa de interés anual (porcentaje).
    tasa_interes: TasaPositiva
    plazo_meses: int = Field(ge=1, le=600)
    fecha_apertura: date
    fecha_vencimiento: date
    renovacion_automatica: bool = False
    # Solo se guarda si la renovación es automática; sin indicarla, se renueva con el mismo monto.
    instruccion_renovacion: InstruccionRenovacion | None = None


class AhorroOut(BaseModel):
    # Se arma directo desde el modelo SQLAlchemy (los Decimal de MySQL pasan a float).
    model_config = ConfigDict(from_attributes=True)

    id: int
    categoria: str
    subtipo: str
    nombre: str
    descripcion: str | None
    monto_actual: float
    moneda: str
    es_meta: bool
    meta_nombre: str | None
    monto_objetivo: float | None
    fecha_objetivo: date | None
    metodo: str
    estado: str
    fecha_registro: datetime
    # Solo en los ahorros programados; nulos en las demás categorías.
    monto_periodo: float | None = None
    periodicidad: str | None = None
    fecha_inicio: date | None = None
    # Solo en los fondos de inversión.
    entidad: str | None = None
    tasa_rendimiento: float | None = None
    tipo_rentabilidad: str | None = None
    reinversion: bool | None = None
    plazo_sugerido: str | None = None
    fecha_inversion: date | None = None
    # Solo en los CDT.
    tasa_interes: float | None = None
    plazo_meses: int | None = None
    fecha_apertura: date | None = None
    fecha_vencimiento: date | None = None
    renovacion_automatica: bool | None = None
    instruccion_renovacion: str | None = None

    @computed_field  # type: ignore[prop-decorator]
    @property
    def progreso(self) -> float | None:
        """Porcentaje de la meta alcanzado (0 a 100); nulo si el ahorro no tiene meta."""
        if not (self.es_meta and self.monto_objetivo):
            return None
        return round(min(self.monto_actual / self.monto_objetivo * 100, 100.0), 1)
