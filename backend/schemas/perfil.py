from pydantic import BaseModel, ConfigDict, Field


class PerfilIn(BaseModel):
    salario_mensual: float = Field(ge=0, default=0.0)
    otros_ingresos: float = Field(ge=0, default=0.0)
    cantidad_hijos: int = Field(ge=0, default=0)
    pago_colegio: float = Field(ge=0, default=0.0)
    pago_universidad: float = Field(ge=0, default=0.0)
    alimentacion: float = Field(ge=0, default=0.0)
    transporte: float = Field(ge=0, default=0.0)
    vestimenta: float = Field(ge=0, default=0.0)
    entretenimiento: float = Field(ge=0, default=0.0)
    arriendo_hipoteca: float = Field(ge=0, default=0.0)
    servicios_publicos: float = Field(ge=0, default=0.0)


class PerfilOut(PerfilIn):
    model_config = ConfigDict(from_attributes=True)

    id: int


class MetaAhorroIn(BaseModel):
    monto_objetivo: float = Field(ge=0, default=0.0)


class MetaAhorroOut(MetaAhorroIn):
    model_config = ConfigDict(from_attributes=True)

    id: int
