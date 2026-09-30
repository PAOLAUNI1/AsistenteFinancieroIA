from pydantic import BaseModel, ConfigDict


class TipoDeudaOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    codigo: str
    nombre: str
    icono: str | None


class CategoriaGastoOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    codigo: str
    nombre: str
    grupo: str
