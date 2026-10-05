from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.schemas.usuario import LoginIn, UsuarioIn, UsuarioOut
from backend.services.perfil import (
    autenticar_usuario,
    crear_usuario,
    listar_usuarios,
    obtener_usuario,
)

router = APIRouter(prefix="/usuarios", tags=["usuarios"])


@router.get("", response_model=list[UsuarioOut])
def listar(db: Session = Depends(get_db)):
    return listar_usuarios(db)


@router.post("", response_model=UsuarioOut, status_code=201)
def registrar(payload: UsuarioIn, db: Session = Depends(get_db)):
    try:
        return crear_usuario(
            db,
            payload.nombre,
            payload.correo,
            payload.contrasena,
            payload.acepta_terminos,
            payload.acepta_tratamiento_datos,
            payload.cantidad_hijos,
        )
    except ValueError as exc:
        mensaje = str(exc)
        # "no aceptó" es error de validación del cliente (422); correo
        # duplicado es conflicto con un recurso existente (409).
        status = 422 if "aceptar" in mensaje else 409
        raise HTTPException(status_code=status, detail=mensaje)


@router.post("/login", response_model=UsuarioOut)
def iniciar_sesion(payload: LoginIn, db: Session = Depends(get_db)):
    usuario = autenticar_usuario(db, payload.correo, payload.contrasena)
    # Mismo mensaje si el correo no existe o la contraseña es incorrecta.
    if usuario is None:
        raise HTTPException(status_code=401, detail="Correo o contraseña incorrectos.")
    if usuario.estado != "ACTIVO":
        raise HTTPException(status_code=403, detail="La cuenta no está activa.")
    return usuario


@router.get("/{usuario_id}", response_model=UsuarioOut)
def obtener(usuario_id: int, db: Session = Depends(get_db)):
    """
    Lo que el orquestador (App_or_ns, hoy la capa de routers) consulta al
    abrir la app para decidir si el usuario va al menú principal
    (estado == "ACTIVO") o al flujo de registro.
    """
    usuario = obtener_usuario(db, usuario_id)
    if usuario is None:
        raise HTTPException(status_code=404, detail=f"No existe un usuario con id {usuario_id}.")
    return usuario
