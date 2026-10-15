"""Tipos de monto compartidos por los contratos de deudas, ahorros y perfil."""

from typing import Annotated

from pydantic import Field

# Alineados con las columnas decimal(15,2) de MySQL: un monto fuera de rango da 422 y no un error de base.
MAX_MONTO = 9_999_999_999_999

MontoPositivo = Annotated[float, Field(gt=0, le=MAX_MONTO, allow_inf_nan=False)]
MontoNoNegativo = Annotated[float, Field(ge=0, le=MAX_MONTO, allow_inf_nan=False)]
