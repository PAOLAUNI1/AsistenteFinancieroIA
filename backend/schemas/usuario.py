from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UsuarioIn(BaseModel):
    nombre: str = Field(min_length=1, max_length=100)
    correo: EmailStr
    cantidad_hijos: int = Field(ge=0, default=0)


class UsuarioOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    correo: str
    cantidad_hijos: int
    estado: str
