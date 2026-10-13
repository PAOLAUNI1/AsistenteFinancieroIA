from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.deps import usuario_actual
from backend.models import Usuario
from backend.schemas.ahorro import AhorroOtroIn, AhorroOut
from backend.services import ahorros as servicio

router = APIRouter(prefix="/ahorros", tags=["ahorros"])


@router.get("", response_model=list[AhorroOut])
def listar_ahorros(usuario: Usuario = Depends(usuario_actual), db: Session = Depends(get_db)):
    return [AhorroOut.desde_modelo(a) for a in servicio.listar_ahorros(db, usuario.id)]


@router.post("/otro", response_model=AhorroOut, status_code=201)
def registrar_ahorro_otro(
    payload: AhorroOtroIn,
    usuario: Usuario = Depends(usuario_actual),
    db: Session = Depends(get_db),
):
    try:
        columnas = servicio.validar_ahorro_otro(**payload.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    try:
        ahorro = servicio.registrar_ahorro(db, usuario.id, columnas)
    except servicio.AhorroNoGuardado:
        raise HTTPException(status_code=422, detail="Los datos del ahorro no son válidos.")
    return AhorroOut.desde_modelo(ahorro)


@router.delete("/{ahorro_id}", status_code=204)
def eliminar_ahorro(
    ahorro_id: int, usuario: Usuario = Depends(usuario_actual), db: Session = Depends(get_db)
):
    if not servicio.eliminar_ahorro(db, usuario.id, ahorro_id):
        raise HTTPException(status_code=404, detail="Ahorro no encontrado.")
