from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.deps import usuario_actual
from backend.models import (
    CompraTarjeta,
    Deuda,
    DeudaEducativo,
    DeudaOtro,
    DeudaTarjeta,
    DeudaVehiculo,
    PagoDeuda,
    TipoDeuda,
    Usuario,
)
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

router = APIRouter(prefix="/deudas", tags=["deudas"])

# Modelo de detalle 1:1 por código de tipo de deuda (los que no están aquí
# guardan todo en la tabla base `deudas`).
MODELOS_DETALLE = {
    "TARJETA": DeudaTarjeta,
    "VEHICULO": DeudaVehiculo,
    "EDUCATIVO": DeudaEducativo,
    "OTRO": DeudaOtro,
}


def _sin_decimal(valor):
    return float(valor) if isinstance(valor, Decimal) else valor


def _a_deuda_out(deuda: Deuda, db: Session) -> DeudaOut:
    detalle = {}
    modelo_detalle = MODELOS_DETALLE.get(deuda.tipo_deuda.codigo)
    if modelo_detalle is not None:
        fila_detalle = db.get(modelo_detalle, deuda.id)
        if fila_detalle is not None:
            detalle = {
                columna.name: _sin_decimal(getattr(fila_detalle, columna.name))
                for columna in modelo_detalle.__table__.columns
                if columna.name != "deuda_id"
            }

    cuotas_pendientes = None
    if deuda.plazo_meses is not None and deuda.proxima_cuota is not None:
        cuotas_pendientes = max(deuda.plazo_meses - deuda.proxima_cuota + 1, 0)

    return DeudaOut(
        id=deuda.id,
        tipo_codigo=deuda.tipo_deuda.codigo,
        tipo_nombre=deuda.tipo_deuda.nombre,
        icono=deuda.tipo_deuda.icono,
        entidad=deuda.entidad,
        monto_inicial=deuda.monto_inicial,
        saldo_actual=deuda.saldo_actual,
        tiene_intereses=deuda.tiene_intereses,
        tasa_interes=deuda.tasa_interes,
        periodicidad_tasa=deuda.periodicidad_tasa,
        tipo_tasa=deuda.tipo_tasa,
        plazo_meses=deuda.plazo_meses,
        valor_cuota=deuda.valor_cuota,
        proxima_cuota=deuda.proxima_cuota,
        cuotas_pendientes=cuotas_pendientes,
        fecha_proximo_pago=deuda.fecha_proximo_pago,
        estado=deuda.estado,
        nombre=deuda.nombre,
        fecha_inicio=deuda.fecha_inicio,
        descripcion=deuda.descripcion,
        detalle=detalle,
    )


def _registrar(db: Session, usuario: Usuario, tipo_slug: str, resultado: dict) -> DeudaOut:
    codigo_tipo, _ = servicio_deudas.VALIDADORES_POR_TIPO[tipo_slug]
    tipo_deuda = db.query(TipoDeuda).filter(TipoDeuda.codigo == codigo_tipo).one()

    deuda = Deuda(usuario_id=usuario.id, tipo_deuda_id=tipo_deuda.id, **resultado["base"])
    db.add(deuda)
    db.flush()  # asigna deuda.id sin cerrar la transacción

    if resultado["detalle"] is not None:
        modelo_detalle = MODELOS_DETALLE[codigo_tipo]
        db.add(modelo_detalle(deuda_id=deuda.id, **resultado["detalle"]))

    db.commit()
    db.refresh(deuda)
    return _a_deuda_out(deuda, db)


@router.get("", response_model=list[DeudaOut])
def listar_deudas(usuario: Usuario = Depends(usuario_actual), db: Session = Depends(get_db)):
    deudas = (
        db.query(Deuda)
        .filter(Deuda.usuario_id == usuario.id)
        .order_by(Deuda.fecha_registro.desc())
        .all()
    )
    return [_a_deuda_out(d, db) for d in deudas]


@router.delete("/{deuda_id}", status_code=204)
def eliminar_deuda(
    deuda_id: int, usuario: Usuario = Depends(usuario_actual), db: Session = Depends(get_db)
):
    deuda = (
        db.query(Deuda)
        .filter(Deuda.id == deuda_id, Deuda.usuario_id == usuario.id)
        .first()
    )
    if deuda is None:
        raise HTTPException(status_code=404, detail="Deuda no encontrada.")

    # La base tiene ON DELETE CASCADE para estas tablas hijas, pero se borra
    # explícito aquí para que el mismo código funcione igual en los tests
    # (SQLite en memoria, sin FKs habilitadas).
    db.query(CompraTarjeta).filter(CompraTarjeta.deuda_id == deuda_id).delete()
    db.query(PagoDeuda).filter(PagoDeuda.deuda_id == deuda_id).delete()
    for modelo_detalle in MODELOS_DETALLE.values():
        db.query(modelo_detalle).filter(modelo_detalle.deuda_id == deuda_id).delete()

    db.delete(deuda)
    db.commit()


@router.post("/hipotecario", response_model=DeudaOut, status_code=201)
def registrar_hipotecario(
    payload: HipotecarioIn,
    usuario: Usuario = Depends(usuario_actual),
    db: Session = Depends(get_db),
):
    try:
        resultado = servicio_deudas.validar_hipotecario(**payload.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    return _registrar(db, usuario, "hipotecario", resultado)


@router.post("/tarjeta", response_model=DeudaOut, status_code=201)
def registrar_tarjeta(
    payload: TarjetaIn,
    usuario: Usuario = Depends(usuario_actual),
    db: Session = Depends(get_db),
):
    try:
        resultado = servicio_deudas.validar_tarjeta(**payload.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    return _registrar(db, usuario, "tarjeta", resultado)


@router.post("/vehiculo", response_model=DeudaOut, status_code=201)
def registrar_vehiculo(
    payload: VehiculoIn,
    usuario: Usuario = Depends(usuario_actual),
    db: Session = Depends(get_db),
):
    try:
        resultado = servicio_deudas.validar_vehiculo(**payload.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    return _registrar(db, usuario, "vehiculo", resultado)


@router.post("/educativo", response_model=DeudaOut, status_code=201)
def registrar_educativo(
    payload: EducativoIn,
    usuario: Usuario = Depends(usuario_actual),
    db: Session = Depends(get_db),
):
    try:
        resultado = servicio_deudas.validar_educativo(**payload.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    return _registrar(db, usuario, "educativo", resultado)


@router.post("/libre_inversion", response_model=DeudaOut, status_code=201)
def registrar_libre_inversion(
    payload: LibreInversionIn,
    usuario: Usuario = Depends(usuario_actual),
    db: Session = Depends(get_db),
):
    try:
        resultado = servicio_deudas.validar_libre_inversion(**payload.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    return _registrar(db, usuario, "libre_inversion", resultado)


@router.post("/prestamo_personal", response_model=DeudaOut, status_code=201)
def registrar_prestamo_personal(
    payload: PrestamoPersonalIn,
    usuario: Usuario = Depends(usuario_actual),
    db: Session = Depends(get_db),
):
    try:
        resultado = servicio_deudas.validar_prestamo_personal(**payload.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    return _registrar(db, usuario, "prestamo_personal", resultado)


@router.post("/consumo", response_model=DeudaOut, status_code=201)
def registrar_consumo(
    payload: ConsumoIn,
    usuario: Usuario = Depends(usuario_actual),
    db: Session = Depends(get_db),
):
    try:
        resultado = servicio_deudas.validar_consumo(**payload.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    return _registrar(db, usuario, "consumo", resultado)


@router.post("/otros", response_model=DeudaOut, status_code=201)
def registrar_otros(
    payload: OtrosIn,
    usuario: Usuario = Depends(usuario_actual),
    db: Session = Depends(get_db),
):
    try:
        resultado = servicio_deudas.validar_otros(**payload.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    return _registrar(db, usuario, "otros", resultado)
