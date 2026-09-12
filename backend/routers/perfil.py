from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.schemas.perfil import MetaAhorroIn, MetaAhorroOut, PerfilIn, PerfilOut
from backend.services.perfil import obtener_o_crear_meta, obtener_o_crear_perfil

router = APIRouter(tags=["perfil"])


@router.get("/perfil", response_model=PerfilOut)
def obtener_perfil(db: Session = Depends(get_db)):
    return obtener_o_crear_perfil(db)


@router.put("/perfil", response_model=PerfilOut)
def actualizar_perfil(payload: PerfilIn, db: Session = Depends(get_db)):
    perfil = obtener_o_crear_perfil(db)
    for campo, valor in payload.model_dump().items():
        setattr(perfil, campo, valor)
    db.commit()
    db.refresh(perfil)
    return perfil


@router.get("/meta-ahorro", response_model=MetaAhorroOut)
def obtener_meta_ahorro(db: Session = Depends(get_db)):
    return obtener_o_crear_meta(db)


@router.put("/meta-ahorro", response_model=MetaAhorroOut)
def actualizar_meta_ahorro(payload: MetaAhorroIn, db: Session = Depends(get_db)):
    meta = obtener_o_crear_meta(db)
    meta.monto_objetivo = payload.monto_objetivo
    db.commit()
    db.refresh(meta)
    return meta
