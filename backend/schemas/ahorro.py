from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, Field

from backend.schemas.deuda import MontoNoNegativo, MontoPositivo

# Subtipos del flujo "Otro tipo de ahorro" (pantalla 3 del diseño).
SubtipoOtro = Literal[
    "EFECTIVO", "DOLARES", "PLAN", "PENSION", "VIAJE", "VIVIENDA", "EMERGENCIAS", "PERSONALIZADO"
]
Moneda = Literal["COP", "USD", "EUR"]
MetodoAhorro = Literal["MANUAL", "PROGRAMADO", "AUTOMATICO"]


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


class AhorroOut(BaseModel):
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
    # Porcentaje de la meta alcanzado (0 a 100); nulo si el ahorro no tiene meta.
    progreso: float | None
    fecha_registro: datetime

    @classmethod
    def desde_modelo(cls, ahorro) -> "AhorroOut":
        actual = float(ahorro.monto_actual)
        objetivo = float(ahorro.monto_objetivo) if ahorro.monto_objetivo is not None else None
        progreso = None
        if ahorro.es_meta and objetivo:
            progreso = round(min(actual / objetivo * 100, 100.0), 1)
        return cls(
            id=ahorro.id,
            categoria=ahorro.categoria,
            subtipo=ahorro.subtipo,
            nombre=ahorro.nombre,
            descripcion=ahorro.descripcion,
            monto_actual=actual,
            moneda=ahorro.moneda,
            es_meta=bool(ahorro.es_meta),
            meta_nombre=ahorro.meta_nombre,
            monto_objetivo=objetivo,
            fecha_objetivo=ahorro.fecha_objetivo,
            metodo=ahorro.metodo,
            estado=ahorro.estado,
            progreso=progreso,
            fecha_registro=ahorro.fecha_registro,
        )
