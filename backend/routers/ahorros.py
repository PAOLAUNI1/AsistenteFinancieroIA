from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.deps import usuario_actual
from backend.models import Usuario
from backend.schemas.ahorro import (
    AhorroAlcanciaIn,
    AhorroCdtIn,
    AhorroFondoIn,
    AhorroOtroIn,
    AhorroOut,
    AhorroProgramadoIn,
)
from backend.services import ahorros as servicio

router = APIRouter(prefix="/ahorros", tags=["ahorros"])

# Cuerpo que recibe cada POST /ahorros/<categoria>. Las llaves son las mismas de
# `servicio.VALIDADORES_POR_CATEGORIA` (que dice cómo se valida cada categoría).
ESQUEMAS_POR_CATEGORIA = {
    "otro": AhorroOtroIn,
    "alcancia": AhorroAlcanciaIn,
    "ahorro-programado": AhorroProgramadoIn,
    "fondo-inversion": AhorroFondoIn,
    "cdt": AhorroCdtIn,
}


@router.get("", response_model=list[AhorroOut])
def listar_ahorros(usuario: Usuario = Depends(usuario_actual), db: Session = Depends(get_db)):
    return [AhorroOut.model_validate(a) for a in servicio.listar_ahorros(db, usuario.id)]


@router.delete("/{ahorro_id}", status_code=204)
def eliminar_ahorro(
    ahorro_id: int, usuario: Usuario = Depends(usuario_actual), db: Session = Depends(get_db)
):
    if not servicio.eliminar_ahorro(db, usuario.id, ahorro_id):
        raise HTTPException(status_code=404, detail="Ahorro no encontrado.")


def _endpoint_de_registro(categoria: str, esquema):
    """Crea el endpoint POST /ahorros/<categoria>: validar con la regla de la categoría, guardar y responder."""
    validar = servicio.VALIDADORES_POR_CATEGORIA[categoria]

    def registrar(
        payload: esquema,
        usuario: Usuario = Depends(usuario_actual),
        db: Session = Depends(get_db),
    ):
        try:
            columnas = validar(**payload.model_dump())
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc))
        try:
            ahorro = servicio.registrar_ahorro(db, usuario.id, columnas)
        except servicio.AhorroNoGuardado:
            # Dato fuera de rango o regla de la base incumplida que la validación no cubrió.
            raise HTTPException(status_code=422, detail="Los datos del ahorro no son válidos.")
        return AhorroOut.model_validate(ahorro)

    return registrar


assert ESQUEMAS_POR_CATEGORIA.keys() == servicio.VALIDADORES_POR_CATEGORIA.keys()

for _categoria, _esquema in ESQUEMAS_POR_CATEGORIA.items():
    router.add_api_route(
        f"/{_categoria}",
        _endpoint_de_registro(_categoria, _esquema),
        methods=["POST"],
        response_model=AhorroOut,
        status_code=201,
        name="registrar_" + _categoria.replace("-", "_"),
        summary=f"Registrar ahorro: {_categoria}",
    )
