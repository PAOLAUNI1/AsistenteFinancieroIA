"""Tipos de monto y de tasa compartidos por los contratos de deudas, ahorros y perfil."""

from typing import Annotated

from pydantic import AfterValidator, Field

# Alineados con las columnas decimal(15,2) de MySQL: un monto fuera de rango da 422 y no un error de base.
MAX_MONTO = 9_999_999_999_999

MontoPositivo = Annotated[float, Field(gt=0, le=MAX_MONTO, allow_inf_nan=False)]
MontoNoNegativo = Annotated[float, Field(ge=0, le=MAX_MONTO, allow_inf_nan=False)]

# Tasa en porcentaje, alineada con la columna decimal(7,4).
MAX_TASA = 100.0


def _a_cuatro_decimales(valor: float) -> float:
    # La columna guarda 4 decimales: una tasa como 0,00001 quedaría en 0 con "intereses".
    return round(valor, 4)


TasaPositiva = Annotated[
    float, AfterValidator(_a_cuatro_decimales), Field(gt=0, le=MAX_TASA, allow_inf_nan=False)
]
TasaNoNegativa = Annotated[
    float, AfterValidator(_a_cuatro_decimales), Field(ge=0, le=MAX_TASA, allow_inf_nan=False)
]
