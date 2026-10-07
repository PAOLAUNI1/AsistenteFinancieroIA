from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.deps import usuario_actual
from backend.models import Usuario
from backend.schemas.usuario import LoginIn, SesionOut, UsuarioIn, UsuarioOut
from backend.services.perfil import (
    CorreoDuplicado,
    TerminosNoAceptados,
    autenticar_usuario,
    crear_usuario,
)
from backend.services.limite_intentos import limite_login
from backend.services.tokens import crear_token

router = APIRouter(prefix="/usuarios", tags=["usuarios"])


def _sesion(usuario: Usuario) -> SesionOut:
    base = UsuarioOut.model_validate(usuario)
    return SesionOut(**base.model_dump(), token=crear_token(usuario.id))


@router.post("", response_model=SesionOut, status_code=201)
def registrar(payload: UsuarioIn, db: Session = Depends(get_db)):
    try:
        usuario = crear_usuario(
            db,
            payload.nombre,
            payload.correo,
            payload.contrasena,
            payload.acepta_terminos,
            payload.acepta_tratamiento_datos,
            payload.cantidad_hijos,
        )
    except TerminosNoAceptados as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    except CorreoDuplicado as exc:
        raise HTTPException(status_code=409, detail=str(exc))
    return _sesion(usuario)


@router.post("/login", response_model=SesionOut)
def iniciar_sesion(payload: LoginIn, request: Request, db: Session = Depends(get_db)):
    ip = request.client.host if request.client else "desconocida"
    espera = limite_login.segundos_de_espera(payload.correo, ip)
    if espera:
        raise HTTPException(
            status_code=429,
            detail="Demasiados intentos fallidos. Intenta de nuevo más tarde.",
            headers={"Retry-After": str(espera)},
        )
    usuario = autenticar_usuario(db, payload.correo, payload.contrasena)
    # Mismo mensaje si el correo no existe o la contraseña es incorrecta.
    if usuario is None:
        limite_login.registrar_fallo(payload.correo, ip)
        raise HTTPException(status_code=401, detail="Correo o contraseña incorrectos.")
    limite_login.registrar_exito(payload.correo)
    if usuario.estado != "ACTIVO":
        raise HTTPException(status_code=403, detail="La cuenta no está activa.")
    return _sesion(usuario)


@router.get("/me", response_model=UsuarioOut)
def mi_usuario(usuario: Usuario = Depends(usuario_actual)):
    """El usuario dueño del token (la app lo usa para saber si la sesión sigue vigente)."""
    return usuario
