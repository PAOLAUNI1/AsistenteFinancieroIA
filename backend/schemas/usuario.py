from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UsuarioIn(BaseModel):
    nombre: str = Field(min_length=1, max_length=100)
    correo: EmailStr
    cantidad_hijos: int = Field(ge=0, default=0)
    acepta_terminos: bool
    acepta_tratamiento_datos: bool


class UsuarioOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    correo: str
    cantidad_hijos: int
    acepto_terminos_en: datetime | None
    acepto_tratamiento_datos_en: datetime | None
    estado: str
