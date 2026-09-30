from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.schemas.perfil import MetaAhorroIn, MetaAhorroOut, PerfilIn, PerfilOut
from backend.services.perfil import (
    actualizar_perfil,
    establecer_meta_principal,
    obtener_meta_principal,
    obtener_o_crear_usuario_actual,
    obtener_perfil,
)

router = APIRouter(tags=["perfil"])


@router.get("/perfil", response_model=PerfilOut)
def obtener_perfil_endpoint(db: Session = Depends(get_db)):
    usuario = obtener_o_crear_usuario_actual(db)
    return {"usuario_id": usuario.id, **obtener_perfil(db, usuario)}


@router.put("/perfil", response_model=PerfilOut)
def actualizar_perfil_endpoint(payload: PerfilIn, db: Session = Depends(get_db)):
    usuario = obtener_o_crear_usuario_actual(db)
    actualizar_perfil(db, usuario, payload.model_dump())
    return {"usuario_id": usuario.id, **obtener_perfil(db, usuario)}


@router.get("/meta-ahorro", response_model=MetaAhorroOut)
def obtener_meta_ahorro(db: Session = Depends(get_db)):
    usuario = obtener_o_crear_usuario_actual(db)
    meta = obtener_meta_principal(db, usuario)
    if meta is None:
        return MetaAhorroOut(id=None, usuario_id=usuario.id, monto_objetivo=0.0, monto_actual=0.0)
    return meta


@router.put("/meta-ahorro", response_model=MetaAhorroOut)
def actualizar_meta_ahorro(payload: MetaAhorroIn, db: Session = Depends(get_db)):
    usuario = obtener_o_crear_usuario_actual(db)
    return establecer_meta_principal(db, usuario, payload.monto_objetivo)
