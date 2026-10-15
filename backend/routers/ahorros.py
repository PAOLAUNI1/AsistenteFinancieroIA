from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.deps import usuario_actual
from backend.models import Usuario
from backend.schemas.ahorro import AhorroAlcanciaIn, AhorroOtroIn, AhorroOut
from backend.services import ahorros as servicio

router = APIRouter(prefix="/ahorros", tags=["ahorros"])


@router.get("", response_model=list[AhorroOut])
def listar_ahorros(usuario: Usuario = Depends(usuario_actual), db: Session = Depends(get_db)):
    return [AhorroOut.desde_modelo(a) for a in servicio.listar_ahorros(db, usuario.id)]


def _guardar(db: Session, usuario: Usuario, validar, datos: dict) -> AhorroOut:
    """Valida con la regla de la categoría, guarda y responde; las reglas rotas dan 422."""
    try:
        columnas = validar(**datos)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    try:
        ahorro = servicio.registrar_ahorro(db, usuario.id, columnas)
    except servicio.AhorroNoGuardado:
        raise HTTPException(status_code=422, detail="Los datos del ahorro no son válidos.")
    return AhorroOut.desde_modelo(ahorro)


@router.post("/otro", response_model=AhorroOut, status_code=201)
def registrar_ahorro_otro(
    payload: AhorroOtroIn,
    usuario: Usuario = Depends(usuario_actual),
    db: Session = Depends(get_db),
):
    return _guardar(db, usuario, servicio.validar_ahorro_otro, payload.model_dump())


@router.post("/alcancia", response_model=AhorroOut, status_code=201)
def registrar_alcancia(
    payload: AhorroAlcanciaIn,
    usuario: Usuario = Depends(usuario_actual),
    db: Session = Depends(get_db),
):
    return _guardar(db, usuario, servicio.validar_ahorro_alcancia, payload.model_dump())


@router.delete("/{ahorro_id}", status_code=204)
def eliminar_ahorro(
    ahorro_id: int, usuario: Usuario = Depends(usuario_actual), db: Session = Depends(get_db)
):
    if not servicio.eliminar_ahorro(db, usuario.id, ahorro_id):
        raise HTTPException(status_code=404, detail="Ahorro no encontrado.")
