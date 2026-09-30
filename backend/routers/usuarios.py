from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.schemas.usuario import UsuarioIn, UsuarioOut
from backend.services.perfil import crear_usuario, listar_usuarios

router = APIRouter(prefix="/usuarios", tags=["usuarios"])


@router.get("", response_model=list[UsuarioOut])
def listar(db: Session = Depends(get_db)):
    return listar_usuarios(db)


@router.post("", response_model=UsuarioOut, status_code=201)
def registrar(payload: UsuarioIn, db: Session = Depends(get_db)):
    try:
        return crear_usuario(db, payload.nombre, payload.correo, payload.cantidad_hijos)
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc))
