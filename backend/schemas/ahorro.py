from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, computed_field

from backend.schemas.comunes import MontoNoNegativo, MontoPositivo

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

    @computed_field  # type: ignore[prop-decorator]
    @property
    def progreso(self) -> float | None:
        """Porcentaje de la meta alcanzado (0 a 100); nulo si el ahorro no tiene meta."""
        if not (self.es_meta and self.monto_objetivo):
            return None
        return round(min(self.monto_actual / self.monto_objetivo * 100, 100.0), 1)
