from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.deps import usuario_actual
from backend.models import Usuario
from backend.schemas.perfil import MetaAhorroIn, MetaAhorroOut, PerfilIn, PerfilOut
from backend.services.perfil import (
    actualizar_perfil,
    establecer_meta_principal,
    obtener_meta_principal,
    obtener_perfil,
)

router = APIRouter(tags=["perfil"])


@router.get("/perfil", response_model=PerfilOut)
def obtener_perfil_endpoint(
    usuario: Usuario = Depends(usuario_actual), db: Session = Depends(get_db)
):
    return {"usuario_id": usuario.id, **obtener_perfil(db, usuario)}


@router.put("/perfil", response_model=PerfilOut)
def actualizar_perfil_endpoint(
    payload: PerfilIn,
    usuario: Usuario = Depends(usuario_actual),
    db: Session = Depends(get_db),
):
    actualizar_perfil(db, usuario, payload.model_dump())
    return {"usuario_id": usuario.id, **obtener_perfil(db, usuario)}


@router.get("/meta-ahorro", response_model=MetaAhorroOut)
def obtener_meta_ahorro(
    usuario: Usuario = Depends(usuario_actual), db: Session = Depends(get_db)
):
    meta = obtener_meta_principal(db, usuario)
    if meta is None:
        return MetaAhorroOut(id=None, usuario_id=usuario.id, monto_objetivo=0.0, monto_actual=0.0)
    return meta


@router.put("/meta-ahorro", response_model=MetaAhorroOut)
def actualizar_meta_ahorro(
    payload: MetaAhorroIn,
    usuario: Usuario = Depends(usuario_actual),
    db: Session = Depends(get_db),
):
    return establecer_meta_principal(db, usuario, payload.monto_objetivo)
