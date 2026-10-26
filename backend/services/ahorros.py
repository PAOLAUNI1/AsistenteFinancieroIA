"""
Ahorros del usuario: reglas del registro y persistencia.

Una regla incumplida lanza ValueError con el texto que se muestra en la app.
"""

import logging
from datetime import date

from sqlalchemy.exc import DataError, IntegrityError
from sqlalchemy.orm import Session

from backend.models import Ahorro, AhorroCdt, AhorroCuenta, AhorroFondo, AhorroProgramado
from backend.tiempo import hoy_colombia

logger = logging.getLogger(__name__)


class AhorroNoGuardado(Exception):
    """La base rechazó el ahorro (dato fuera de rango o regla incumplida) y se deshizo el guardado."""


def _nombre_requerido(nombre: str, mensaje: str) -> str:
    nombre = nombre.strip()
    if not nombre:
        raise ValueError(mensaje)
    return nombre


def _exigir_fecha_no_pasada(fecha: date | None) -> None:
    if fecha is not None and fecha < hoy_colombia():
        raise ValueError("La fecha objetivo no puede ser anterior a hoy.")


def _columnas(
    *,
    categoria: str,
    subtipo: str,
    nombre: str,
    descripcion: str | None,
    monto_actual: float,
    moneda: str,
    metodo: str,
    es_meta: bool = False,
    meta_nombre: str | None = None,
    monto_objetivo: float | None = None,
    fecha_objetivo: date | None = None,
) -> dict:
    """Las columnas de `ahorros` de cualquier categoría: lo que cambia es solo qué reglas se aplican."""
    return {
        "categoria": categoria,
        "subtipo": subtipo,
        "nombre": nombre,
        "descripcion": (descripcion or "").strip() or None,
        "monto_actual": monto_actual,
        "moneda": moneda,
        "metodo": metodo,
        "estado": "ACTIVA",
        "es_meta": es_meta,
        "meta_nombre": (meta_nombre or "").strip() or None,
        "monto_objetivo": monto_objetivo,
        "fecha_objetivo": fecha_objetivo,
    }


def validar_ahorro_otro(
    *,
    subtipo: str,
    nombre: str,
    descripcion: str | None,
    monto_actual: float,
    moneda: str,
    es_meta: bool,
    meta_nombre: str | None,
    monto_objetivo: float | None,
    fecha_objetivo: date | None,
    metodo: str,
) -> dict:
    """Columnas de `ahorros` para la categoría OTRO (la meta es opcional)."""
    nombre = _nombre_requerido(nombre, "Ingresa el nombre del ahorro.")
    if monto_actual < 0:
        raise ValueError("El monto actual no puede ser negativo.")

    meta: dict = {}
    if es_meta:
        if monto_objetivo is None or monto_objetivo <= 0:
            raise ValueError("Ingresa el monto objetivo de la meta.")
        _exigir_fecha_no_pasada(fecha_objetivo)
        meta = {
            "es_meta": True,
            "meta_nombre": meta_nombre,
            "monto_objetivo": monto_objetivo,
            "fecha_objetivo": fecha_objetivo,
        }

    return _columnas(
        categoria="OTRO", subtipo=subtipo, nombre=nombre, descripcion=descripcion,
        monto_actual=monto_actual, moneda=moneda, metodo=metodo, **meta,
    )


def validar_ahorro_alcancia(
    *,
    subtipo: str,
    nombre: str,
    descripcion: str | None,
    monto_objetivo: float,
    moneda: str,
    fecha_objetivo: date | None,
    metodo: str,
    aporte_inicial: float,
) -> dict:
    """Columnas de `ahorros` para una alcancía (siempre es una meta; el aporte inicial es el monto actual)."""
    nombre = _nombre_requerido(nombre, "Ingresa el nombre de la alcancía.")
    if monto_objetivo <= 0:
        raise ValueError("Ingresa el monto objetivo de la alcancía.")
    if aporte_inicial < 0:
        raise ValueError("El aporte inicial no puede ser negativo.")
    _exigir_fecha_no_pasada(fecha_objetivo)

    return _columnas(
        categoria="ALCANCIA", subtipo=subtipo, nombre=nombre, descripcion=descripcion,
        monto_actual=aporte_inicial, moneda=moneda, metodo=metodo,
        es_meta=True, monto_objetivo=monto_objetivo, fecha_objetivo=fecha_objetivo,
    )


def validar_ahorro_programado(
    *,
    subtipo: str,
    nombre: str,
    descripcion: str | None,
    monto_objetivo: float,
    monto_inicial: float,
    moneda: str,
    monto_periodo: float,
    periodicidad: str,
    fecha_inicio: date,
    fecha_objetivo: date,
    metodo: str,
) -> dict:
    """Columnas de `ahorros` más el detalle `programado` (siempre es una meta con fechas)."""
    nombre = _nombre_requerido(nombre, "Ingresa el nombre de la meta.")
    if monto_objetivo <= 0:
        raise ValueError("Ingresa el monto objetivo de la meta.")
    if monto_inicial < 0:
        raise ValueError("El monto inicial no puede ser negativo.")
    if monto_inicial >= monto_objetivo:
        raise ValueError("El monto inicial debe ser menor que el monto objetivo.")
    if monto_periodo <= 0:
        raise ValueError("Ingresa el monto a ahorrar por periodo.")
    if fecha_inicio < hoy_colombia():
        raise ValueError("La fecha de inicio no puede ser anterior a hoy.")
    _exigir_fecha_no_pasada(fecha_objetivo)
    if fecha_objetivo <= fecha_inicio:
        raise ValueError("La fecha objetivo debe ser posterior a la fecha de inicio.")

    columnas = _columnas(
        categoria="PROGRAMADO", subtipo=subtipo, nombre=nombre, descripcion=descripcion,
        monto_actual=monto_inicial, moneda=moneda, metodo=metodo,
        es_meta=True, monto_objetivo=monto_objetivo, fecha_objetivo=fecha_objetivo,
    )
    columnas["programado"] = {
        "monto_periodo": monto_periodo,
        "periodicidad": periodicidad,
        "fecha_inicio": fecha_inicio,
    }
    return columnas


def validar_ahorro_fondo(
    *,
    subtipo: str,
    entidad: str,
    nombre: str,
    descripcion: str | None,
    monto_inicial: float,
    moneda: str,
    fecha_inversion: date,
    plazo_sugerido: str | None,
    tasa_rendimiento: float,
    tipo_rentabilidad: str,
    reinversion: bool,
) -> dict:
    """Columnas de `ahorros` más el detalle `fondo` (no es una meta: el monto inicial es el monto actual)."""
    entidad = _nombre_requerido(entidad, "Selecciona la entidad financiera.")
    nombre = _nombre_requerido(nombre, "Ingresa el nombre del fondo.")
    if monto_inicial <= 0:
        raise ValueError("Ingresa el monto inicial del fondo.")
    if fecha_inversion > hoy_colombia():
        raise ValueError("La fecha de inversión no puede ser posterior a hoy.")

    columnas = _columnas(
        categoria="FONDO_INVERSION", subtipo=subtipo, nombre=nombre, descripcion=descripcion,
        monto_actual=monto_inicial, moneda=moneda, metodo="MANUAL",
    )
    columnas["fondo"] = {
        "entidad": entidad,
        "tasa_rendimiento": tasa_rendimiento,
        "tipo_rentabilidad": tipo_rentabilidad,
        "reinversion": reinversion,
        "plazo_sugerido": plazo_sugerido,
        "fecha_inversion": fecha_inversion,
    }
    return columnas


def validar_ahorro_cuenta(
    *,
    tipo_cuenta: str,
    entidad: str,
    nombre: str,
    descripcion: str | None,
    monto_actual: float,
    moneda: str,
    es_meta: bool,
    meta_nombre: str | None,
    monto_objetivo: float | None,
    fecha_objetivo: date | None,
) -> dict:
    """Columnas de `ahorros` más el detalle `cuenta` (la meta es opcional, como en "Otro")."""
    entidad = _nombre_requerido(entidad, "Selecciona la entidad financiera.")
    nombre = _nombre_requerido(nombre, "Ingresa el nombre de la cuenta.")
    if monto_actual < 0:
        raise ValueError("El monto actual no puede ser negativo.")

    meta: dict = {}
    if es_meta:
        if monto_objetivo is None or monto_objetivo <= 0:
            raise ValueError("Ingresa el monto objetivo de la meta.")
        if fecha_objetivo is None:
            raise ValueError("Selecciona la fecha objetivo.")
        _exigir_fecha_no_pasada(fecha_objetivo)
        meta = {
            "es_meta": True,
            "meta_nombre": meta_nombre,
            "monto_objetivo": monto_objetivo,
            "fecha_objetivo": fecha_objetivo,
        }

    columnas = _columnas(
        categoria="CUENTA", subtipo=tipo_cuenta, nombre=nombre, descripcion=descripcion,
        monto_actual=monto_actual, moneda=moneda, metodo="MANUAL", **meta,
    )
    columnas["cuenta"] = {"entidad": entidad}
    return columnas


def validar_ahorro_cdt(
    *,
    tipo_tasa: str,
    entidad: str,
    nombre: str,
    descripcion: str | None,
    monto: float,
    moneda: str,
    tasa_interes: float,
    plazo_meses: int,
    fecha_apertura: date,
    fecha_vencimiento: date,
    renovacion_automatica: bool,
    instruccion_renovacion: str | None,
) -> dict:
    """Columnas de `ahorros` más el detalle `cdt` (no es una meta: el monto del CDT es el monto actual)."""
    entidad = _nombre_requerido(entidad, "Selecciona la entidad financiera.")
    nombre = _nombre_requerido(nombre, "Ingresa el nombre del CDT.")
    if monto <= 0:
        raise ValueError("Ingresa el monto del CDT.")
    if fecha_vencimiento <= fecha_apertura:
        raise ValueError("La fecha de vencimiento debe ser posterior a la fecha de apertura.")

    columnas = _columnas(
        categoria="CDT", subtipo=tipo_tasa, nombre=nombre, descripcion=descripcion,
        monto_actual=monto, moneda=moneda, metodo="MANUAL",
    )
    columnas["cdt"] = {
        "entidad": entidad,
        "tasa_interes": tasa_interes,
        "plazo_meses": plazo_meses,
        "fecha_apertura": fecha_apertura,
        "fecha_vencimiento": fecha_vencimiento,
        "renovacion_automatica": renovacion_automatica,
        # Las instrucciones solo tienen sentido si el CDT se renueva solo.
        "instruccion_renovacion": (instruccion_renovacion or "MISMO_MONTO") if renovacion_automatica else None,
    }
    return columnas


# Cómo se valida cada categoría; las llaves son las del segmento de la ruta POST /ahorros/<categoria>
# y las mismas que `routers/ahorros.ESQUEMAS_POR_CATEGORIA` (que dice qué cuerpo recibe cada una).
VALIDADORES_POR_CATEGORIA = {
    "otro": validar_ahorro_otro,
    "alcancia": validar_ahorro_alcancia,
    "ahorro-programado": validar_ahorro_programado,
    "fondo-inversion": validar_ahorro_fondo,
    "cdt": validar_ahorro_cdt,
    "cuenta": validar_ahorro_cuenta,
}

# Detalle 1:1 que guarda cada categoría que lo tiene: la llave es la de `columnas` y la del
# atributo de `Ahorro` que lo relaciona.
DETALLE_POR_CLAVE = {
    "programado": AhorroProgramado,
    "fondo": AhorroFondo,
    "cdt": AhorroCdt,
    "cuenta": AhorroCuenta,
}


def registrar_ahorro(db: Session, usuario_id: int, columnas: dict) -> Ahorro:
    # Lo que va a la tabla de detalle de la categoría viaja aparte de las columnas de `ahorros`.
    columnas = dict(columnas)
    detalles = {clave: columnas.pop(clave) for clave in DETALLE_POR_CLAVE if clave in columnas}
    ahorro = Ahorro(usuario_id=usuario_id, **columnas)
    for clave, datos in detalles.items():
        setattr(ahorro, clave, DETALLE_POR_CLAVE[clave](**datos))
    try:
        db.add(ahorro)
        db.commit()
    except (DataError, IntegrityError) as exc:
        db.rollback()
        logger.warning("MySQL rechazó el ahorro del usuario %s: %s", usuario_id, exc.orig)
        raise AhorroNoGuardado() from exc
    db.refresh(ahorro)
    return ahorro


def listar_ahorros(db: Session, usuario_id: int) -> list[Ahorro]:
    return (
        db.query(Ahorro)
        .filter(Ahorro.usuario_id == usuario_id)
        .order_by(Ahorro.fecha_registro.desc(), Ahorro.id.desc())
        .all()
    )


def eliminar_ahorro(db: Session, usuario_id: int, ahorro_id: int) -> bool:
    """False si no existe o es de otro usuario."""
    ahorro = (
        db.query(Ahorro).filter(Ahorro.id == ahorro_id, Ahorro.usuario_id == usuario_id).first()
    )
    if ahorro is None:
        return False
    db.delete(ahorro)
    db.commit()
    return True
