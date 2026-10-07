from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.deps import usuario_actual
from backend.models import Usuario
from backend.schemas.deuda import (
    ConsumoIn,
    DeudaOut,
    EducativoIn,
    HipotecarioIn,
    LibreInversionIn,
    OtrosIn,
    PrestamoPersonalIn,
    TarjetaIn,
    VehiculoIn,
)
from backend.services import deudas as servicio_deudas
from backend.services import repositorio_deudas as repositorio

router = APIRouter(prefix="/deudas", tags=["deudas"])

# Cuerpo que recibe cada POST /deudas/<tipo>. Las llaves son las mismas de
# `servicio_deudas.VALIDADORES_POR_TIPO` (que dice cómo se valida cada tipo).
ESQUEMAS_POR_TIPO = {
    "hipotecario": HipotecarioIn,
    "tarjeta": TarjetaIn,
    "vehiculo": VehiculoIn,
    "educativo": EducativoIn,
    "libre_inversion": LibreInversionIn,
    "prestamo_personal": PrestamoPersonalIn,
    "consumo": ConsumoIn,
    "otros": OtrosIn,
}


@router.get("", response_model=list[DeudaOut])
def listar_deudas(usuario: Usuario = Depends(usuario_actual), db: Session = Depends(get_db)):
    return repositorio.a_deudas_out(db, repositorio.listar_deudas(db, usuario.id))


@router.delete("/{deuda_id}", status_code=204)
def eliminar_deuda(
    deuda_id: int, usuario: Usuario = Depends(usuario_actual), db: Session = Depends(get_db)
):
    if not repositorio.eliminar_deuda(db, usuario.id, deuda_id):
        raise HTTPException(status_code=404, detail="Deuda no encontrada.")


def _endpoint_de_registro(tipo: str, esquema):
    """Crea el endpoint POST /deudas/<tipo>: validar con la regla del tipo, guardar y responder."""
    codigo_tipo, validar = servicio_deudas.VALIDADORES_POR_TIPO[tipo]

    def registrar(
        payload: esquema,
        usuario: Usuario = Depends(usuario_actual),
        db: Session = Depends(get_db),
    ):
        try:
            resultado = validar(**payload.model_dump())
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc))
        try:
            deuda = repositorio.registrar_deuda(db, usuario.id, codigo_tipo, resultado)
        except repositorio.DeudaNoGuardada:
            # Dato fuera de rango o regla de la base incumplida que la validación no cubrió.
            raise HTTPException(status_code=422, detail="Los datos de la deuda no son válidos.")
        return repositorio.a_deudas_out(db, [deuda])[0]

    return registrar


assert ESQUEMAS_POR_TIPO.keys() == servicio_deudas.VALIDADORES_POR_TIPO.keys()

for _tipo, _esquema in ESQUEMAS_POR_TIPO.items():
    router.add_api_route(
        f"/{_tipo}",
        _endpoint_de_registro(_tipo, _esquema),
        methods=["POST"],
        response_model=DeudaOut,
        status_code=201,
        name=f"registrar_{_tipo}",
        summary=f"Registrar deuda: {_tipo.replace('_', ' ')}",
    )
