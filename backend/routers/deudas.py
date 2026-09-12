from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import Deuda
from backend.schemas.deuda import (
    ConsumoIn,
    DeudaOut,
    EducativoIn,
    HipotecarioIn,
    LibreInversionIn,
    PrestamoPersonalIn,
    TarjetaIn,
    VehiculoIn,
)
from backend.services import deudas as servicio_deudas

router = APIRouter(prefix="/deudas", tags=["deudas"])


def _guardar(db: Session, datos: dict) -> Deuda:
    deuda = Deuda(**datos)
    db.add(deuda)
    db.commit()
    db.refresh(deuda)
    return deuda


@router.get("", response_model=list[DeudaOut])
def listar_deudas(db: Session = Depends(get_db)):
    return db.query(Deuda).order_by(Deuda.creado_en.desc()).all()


@router.delete("/{deuda_id}", status_code=204)
def eliminar_deuda(deuda_id: int, db: Session = Depends(get_db)):
    deuda = db.get(Deuda, deuda_id)
    if deuda is None:
        raise HTTPException(status_code=404, detail="Deuda no encontrada.")
    db.delete(deuda)
    db.commit()


@router.post("/hipotecario", response_model=DeudaOut, status_code=201)
def registrar_hipotecario(payload: HipotecarioIn, db: Session = Depends(get_db)):
    try:
        datos = servicio_deudas.validar_hipotecario(**payload.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    return _guardar(db, datos)


@router.post("/tarjeta", response_model=DeudaOut, status_code=201)
def registrar_tarjeta(payload: TarjetaIn, db: Session = Depends(get_db)):
    try:
        datos = servicio_deudas.validar_tarjeta(**payload.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    return _guardar(db, datos)


@router.post("/vehiculo", response_model=DeudaOut, status_code=201)
def registrar_vehiculo(payload: VehiculoIn, db: Session = Depends(get_db)):
    try:
        datos = servicio_deudas.validar_vehiculo(**payload.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    return _guardar(db, datos)


@router.post("/educativo", response_model=DeudaOut, status_code=201)
def registrar_educativo(payload: EducativoIn, db: Session = Depends(get_db)):
    try:
        datos = servicio_deudas.validar_educativo(**payload.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    return _guardar(db, datos)


@router.post("/libre_inversion", response_model=DeudaOut, status_code=201)
def registrar_libre_inversion(payload: LibreInversionIn, db: Session = Depends(get_db)):
    try:
        datos = servicio_deudas.validar_libre_inversion(**payload.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    return _guardar(db, datos)


@router.post("/prestamo_personal", response_model=DeudaOut, status_code=201)
def registrar_prestamo_personal(payload: PrestamoPersonalIn, db: Session = Depends(get_db)):
    try:
        datos = servicio_deudas.validar_prestamo_personal(**payload.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    return _guardar(db, datos)


@router.post("/consumo", response_model=DeudaOut, status_code=201)
def registrar_consumo(payload: ConsumoIn, db: Session = Depends(get_db)):
    try:
        datos = servicio_deudas.validar_consumo(**payload.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    return _guardar(db, datos)
