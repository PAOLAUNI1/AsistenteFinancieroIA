from datetime import datetime

from typing import Annotated

from pydantic import BaseModel, ConfigDict, EmailStr, Field, StringConstraints, field_validator

from backend.services.seguridad import MAX_BYTES_CONTRASENA


class UsuarioIn(BaseModel):
    nombre: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=100)]
    correo: EmailStr
    contrasena: str = Field(min_length=8, max_length=MAX_BYTES_CONTRASENA)
    cantidad_hijos: int = Field(ge=0, le=30, default=0)
    acepta_terminos: bool
    acepta_tratamiento_datos: bool

    @field_validator("contrasena")
    @classmethod
    def _contrasena_cabe_en_bcrypt(cls, valor: str) -> str:
        if len(valor.encode("utf-8")) > MAX_BYTES_CONTRASENA:
            raise ValueError(f"La contraseña no puede superar {MAX_BYTES_CONTRASENA} bytes.")
        return valor


class LoginIn(BaseModel):
    correo: EmailStr
    contrasena: str = Field(min_length=1, max_length=128)


class UsuarioOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    correo: str
    cantidad_hijos: int
    acepto_terminos_en: datetime | None
    acepto_tratamiento_datos_en: datetime | None
    estado: str


class SesionOut(UsuarioOut):
    """Respuesta de registro e inicio de sesión: el usuario y su token para las demás llamadas."""

    token: str
    token_type: str = "bearer"
