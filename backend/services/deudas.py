"""
Validación y cálculo para cada uno de los 7 tipos de deuda (sección 4 de
CLAUDE.md), adaptados al esquema real de la base `asistente_financiero`
(MySQL): una tabla base `deudas` común a los 7 tipos, y tablas de detalle
1:1 (`deuda_tarjeta`, `deuda_vehiculo`, `deuda_educativo`) para los tipos que
tienen atributos propios que no caben en la tabla base.

Cada función recibe los datos ya parseados (floats/ints, no strings con
formato "$1.000.000") y devuelve un dict con dos claves:
  - "base": columnas para la tabla `deudas`
  - "detalle": columnas para la tabla de detalle (o None si el tipo no tiene)

Si algo no es válido, levanta ValueError con el mismo mensaje que mostraba
el formulario en Streamlit, para no reinventar las reglas ya definidas en
la sección 10 de CLAUDE.md.
"""

import calendar
from datetime import date

from backend.tiempo import hoy_colombia


def _texto(valor: str | None) -> str | None:
    """El texto sin espacios sobrantes, o None si queda vacío."""
    return (valor or "").strip() or None


def _exigir(es_invalido: bool, mensaje: str) -> None:
    if es_invalido:
        raise ValueError(mensaje)


def _base_deuda(
    *,
    entidad: str,
    monto_inicial: float,
    saldo_actual: float,
    tasa: float | None,
    periodicidad_tasa: str | None,
    tipo_tasa: str | None,
    plazo_meses: int | None,
    valor_cuota: float | None,
    proxima_cuota: int | None,
    proximo_pago: date,
    tiene_intereses: bool,
    nombre: str | None = None,
    fecha_inicio: date | None = None,
    descripcion: str | None = None,
    activa: bool = True,
) -> dict:
    """Columnas de la tabla `deudas` que comparten los ocho tipos de deuda."""
    return {
        "entidad": entidad,
        "nombre": _texto(nombre),
        "monto_inicial": monto_inicial,
        "saldo_actual": saldo_actual,
        "tiene_intereses": tiene_intereses,
        "tasa_interes": tasa,
        "periodicidad_tasa": periodicidad_tasa,
        "tipo_tasa": tipo_tasa,
        "plazo_meses": plazo_meses,
        "valor_cuota": valor_cuota,
        "proxima_cuota": proxima_cuota,
        "fecha_proximo_pago": proximo_pago,
        "fecha_inicio": fecha_inicio,
        "descripcion": _texto(descripcion),
        "estado": "ACTIVA" if activa else "CANCELADA",
    }


def _base_credito(*, tasa: float, **resto) -> dict:
    """Base de un crédito con cuotas fijas: hay intereses si la tasa es mayor a cero y la tasa es fija."""
    resto.setdefault("tiene_intereses", tasa > 0)
    resto.setdefault("tipo_tasa", "FIJA")
    return _base_deuda(tasa=tasa, **resto)


def _exigir_inicio_no_posterior(fecha_inicio: date | None, proximo_pago: date) -> None:
    _exigir(
        fecha_inicio is not None and fecha_inicio > proximo_pago,
        "La fecha de inicio no puede ser posterior al próximo pago.",
    )


def validar_hipotecario(
    entidad: str,
    monto_inicial: float,
    saldo_actual: float,
    tasa: float,
    periodicidad_tasa: str,
    tipo_tasa: str,
    anos: int,
    meses: int,
    valor_cuota: float,
    cuota_proxima: int,
    proximo_pago: date,
    nombre: str | None = None,
    fecha_inicio: date | None = None,
    descripcion: str | None = None,
    activa: bool = True,
) -> dict:
    plazo_meses = (anos * 12) + meses

    _exigir(not entidad.strip(), "Ingresa la entidad financiera.")
    _exigir(monto_inicial <= 0, "El monto inicial debe ser mayor que cero.")
    _exigir(saldo_actual <= 0, "El saldo actual debe ser mayor que cero.")
    _exigir(saldo_actual > monto_inicial, "El saldo actual no puede ser mayor al monto inicial.")
    _exigir(tasa <= 0, "Ingresa una tasa de interés válida.")
    _exigir(plazo_meses <= 0, "El plazo del crédito debe ser mayor a 0 meses.")
    _exigir(cuota_proxima > plazo_meses, "La próxima cuota no puede superar el total de cuotas.")
    _exigir(valor_cuota <= 0, "El valor de la cuota mensual debe ser mayor que cero.")
    _exigir_inicio_no_posterior(fecha_inicio, proximo_pago)

    return {
        "base": _base_credito(
            entidad=entidad.strip(),
            nombre=nombre,
            monto_inicial=monto_inicial,
            saldo_actual=saldo_actual,
            tasa=tasa,
            periodicidad_tasa=periodicidad_tasa,
            tipo_tasa=tipo_tasa,
            plazo_meses=plazo_meses,
            valor_cuota=valor_cuota,
            proxima_cuota=cuota_proxima,
            proximo_pago=proximo_pago,
            fecha_inicio=fecha_inicio,
            descripcion=descripcion,
            activa=activa,
            tiene_intereses=True,
        ),
        "detalle": None,
    }


def proxima_fecha_de_pago(dia_pago: int, hoy: date | None = None) -> date:
    """Próxima fecha (hoy incluido) en que cae el día de pago, ajustado al fin de mes."""
    hoy = hoy or hoy_colombia()
    anio, mes = hoy.year, hoy.month
    for _ in range(2):
        ultimo_dia = calendar.monthrange(anio, mes)[1]
        candidata = date(anio, mes, min(dia_pago, ultimo_dia))
        if candidata >= hoy:
            return candidata
        mes += 1
        if mes > 12:
            mes, anio = 1, anio + 1
    return candidata


def validar_tarjeta(
    entidad: str,
    cupo_total: float,
    saldo_actual: float,
    tasa: float,
    periodicidad_tasa: str = "MENSUAL",
    dia_corte: int = 15,
    dia_pago: int = 5,
    franquicia: str | None = None,
    ultimos_digitos: str | None = None,
    pago_minimo: float = 0.0,
    cuota_manejo: float = 0.0,
    proximo_pago: date | None = None,
    nombre: str | None = None,
    descripcion: str | None = None,
    activa: bool = True,
) -> dict:
    _exigir(not entidad.strip(), "Ingresa la entidad financiera emisora.")
    _exigir(cupo_total <= 0, "El cupo total aprobado debe ser mayor a cero.")
    _exigir(saldo_actual <= 0, "El saldo adeudado debe ser mayor a cero.")
    _exigir(saldo_actual > cupo_total, "El saldo utilizado no puede superar el cupo aprobado.")
    _exigir(
        pago_minimo < 0 or cuota_manejo < 0,
        "El pago mínimo y la cuota de manejo no pueden ser negativos.",
    )

    cuota_total_mes = pago_minimo + cuota_manejo

    return {
        "base": _base_deuda(
            entidad=entidad.strip(),
            nombre=nombre,
            monto_inicial=cupo_total,
            saldo_actual=saldo_actual,
            tasa=tasa,
            periodicidad_tasa=periodicidad_tasa,
            tipo_tasa="VARIABLE",
            plazo_meses=None,
            valor_cuota=cuota_total_mes if cuota_total_mes > 0 else None,
            proxima_cuota=None,
            proximo_pago=proximo_pago or proxima_fecha_de_pago(dia_pago),
            tiene_intereses=tasa > 0,
            descripcion=descripcion,
            activa=activa,
        ),
        "detalle": {
            "cupo_total": cupo_total,
            "dia_corte": dia_corte,
            "dia_pago": dia_pago,
            "franquicia": franquicia,
            "ultimos_digitos": ultimos_digitos,
        },
    }


def validar_vehiculo(
    entidad: str,
    monto_inicial: float,
    saldo_actual: float,
    tasa: float,
    periodicidad_tasa: str,
    anos: int,
    meses: int,
    valor_cuota: float,
    cuota_proxima: int,
    proximo_pago: date,
    tipo_vehiculo: str = "OTRO",
    marca: str | None = None,
    modelo: str | None = None,
    anio: int | None = None,
    placa: str | None = None,
    nombre: str | None = None,
    fecha_inicio: date | None = None,
    descripcion: str | None = None,
    activa: bool = True,
) -> dict:
    plazo_meses = (anos * 12) + meses

    _exigir(not entidad.strip(), "Ingresa la entidad financiera.")
    _exigir(monto_inicial <= 0, "El monto financiado debe ser mayor a cero.")
    _exigir(saldo_actual <= 0, "El saldo actual debe ser mayor a cero.")
    _exigir(saldo_actual > monto_inicial, "El saldo actual no puede ser mayor al monto financiado.")
    _exigir(plazo_meses <= 0, "El plazo del crédito debe ser mayor a 0 meses.")
    _exigir(cuota_proxima > plazo_meses, "La próxima cuota no puede superar el total de cuotas.")
    _exigir(valor_cuota <= 0, "El valor de la cuota debe ser mayor a cero.")
    _exigir_inicio_no_posterior(fecha_inicio, proximo_pago)

    return {
        "base": _base_credito(
            entidad=entidad.strip(),
            nombre=nombre,
            monto_inicial=monto_inicial,
            saldo_actual=saldo_actual,
            tasa=tasa,
            periodicidad_tasa=periodicidad_tasa,
            plazo_meses=plazo_meses,
            valor_cuota=valor_cuota,
            proxima_cuota=cuota_proxima,
            proximo_pago=proximo_pago,
            fecha_inicio=fecha_inicio,
            descripcion=descripcion,
            activa=activa,
        ),
        "detalle": {
            "tipo_vehiculo": tipo_vehiculo,
            "marca": marca,
            "modelo": modelo,
            "anio": anio,
            "placa": placa,
            "valor_vehiculo": monto_inicial,
            "cuota_inicial": None,
        },
    }


def validar_educativo(
    entidad: str,
    saldo_actual: float,
    tasa: float,
    valor_cuota: float,
    proximo_pago: date,
    plazo_meses: int,
    carrera: str | None = None,
    modalidad: str = "En amortización",
    cuota_proxima: int = 1,
    monto_inicial: float = 0,
    periodicidad_tasa: str = "EA",
    nombre: str | None = None,
    fecha_inicio: date | None = None,
    descripcion: str | None = None,
    activa: bool = True,
) -> dict:
    _exigir(not entidad.strip(), "Ingresa la entidad o institución del crédito educativo.")
    _exigir(saldo_actual <= 0, "El saldo actual debe ser mayor a cero.")
    _exigir(
        monto_inicial > 0 and saldo_actual > monto_inicial,
        "El saldo actual no puede ser mayor al monto inicial.",
    )
    _exigir(valor_cuota <= 0, "El valor de la cuota mensual debe ser mayor a cero.")
    _exigir_inicio_no_posterior(fecha_inicio, proximo_pago)

    _exigir(plazo_meses <= 0, "El plazo debe ser mayor a 0 meses.")
    _exigir(cuota_proxima > plazo_meses, "La próxima cuota no puede superar el total de cuotas.")

    return {
        "base": _base_credito(
            entidad=entidad.strip(),
            nombre=nombre,
            monto_inicial=monto_inicial or saldo_actual,
            saldo_actual=saldo_actual,
            tasa=tasa,
            periodicidad_tasa=periodicidad_tasa,
            plazo_meses=plazo_meses,
            valor_cuota=valor_cuota,
            proxima_cuota=cuota_proxima,
            proximo_pago=proximo_pago,
            fecha_inicio=fecha_inicio,
            descripcion=descripcion,
            activa=activa,
        ),
        "detalle": {
            "institucion": entidad.strip(),
            "programa": _texto(carrera),
            "modalidad": modalidad or None,
            "beneficiario": None,
        },
    }


def validar_otros(
    entidad: str,
    monto_inicial: float,
    saldo_actual: float,
    plazo_meses: int,
    valor_cuota: float,
    proximo_pago: date,
    tipo_credito: str = "OTRO",
    nombre: str | None = None,
    tasa: float = 0.0,
    periodicidad_tasa: str = "EA",
    cuota_proxima: int = 1,
    fecha_inicio: date | None = None,
    descripcion: str | None = None,
    activa: bool = True,
) -> dict:
    _exigir(not entidad.strip(), "Ingresa la entidad o la persona a quien le debes.")
    _exigir(monto_inicial <= 0, "El monto total de la deuda debe ser mayor a cero.")
    _exigir(saldo_actual <= 0, "El saldo actual debe ser mayor a cero.")
    _exigir(saldo_actual > monto_inicial, "El saldo actual no puede ser mayor al monto total.")
    _exigir(plazo_meses <= 0, "El plazo debe ser mayor a 0 meses.")
    _exigir(cuota_proxima > plazo_meses, "La próxima cuota no puede superar el total de cuotas.")
    _exigir(valor_cuota <= 0, "El valor de la cuota mensual debe ser mayor a cero.")
    _exigir_inicio_no_posterior(fecha_inicio, proximo_pago)

    return {
        "base": _base_credito(
            entidad=entidad.strip(),
            nombre=nombre,
            monto_inicial=monto_inicial,
            saldo_actual=saldo_actual,
            tasa=tasa,
            periodicidad_tasa=periodicidad_tasa,
            plazo_meses=plazo_meses,
            valor_cuota=valor_cuota,
            proxima_cuota=cuota_proxima,
            proximo_pago=proximo_pago,
            fecha_inicio=fecha_inicio,
            descripcion=descripcion,
            activa=activa,
        ),
        "detalle": {"tipo_credito": tipo_credito},
    }


def validar_libre_inversion(
    entidad: str,
    monto_inicial: float,
    saldo_actual: float,
    tasa: float,
    periodicidad_tasa: str,
    total_meses: int,
    cuota_proxima: int,
    valor_cuota: float,
    proximo_pago: date,
) -> dict:
    _exigir(not entidad.strip(), "Ingresa la entidad financiera.")
    _exigir(monto_inicial <= 0, "El monto inicial debe ser mayor a cero.")
    _exigir(saldo_actual <= 0, "El saldo pendiente debe ser mayor a cero.")
    _exigir(saldo_actual > monto_inicial, "El saldo pendiente no puede superar el monto inicial.")
    _exigir(cuota_proxima > total_meses, "La próxima cuota no puede ser superior al total de cuotas.")
    _exigir(valor_cuota <= 0, "El valor de la cuota mensual debe ser mayor a cero.")

    return {
        "base": _base_credito(
            entidad=entidad.strip(),
            monto_inicial=monto_inicial,
            saldo_actual=saldo_actual,
            tasa=tasa,
            periodicidad_tasa=periodicidad_tasa,
            plazo_meses=total_meses,
            valor_cuota=valor_cuota,
            proxima_cuota=cuota_proxima,
            proximo_pago=proximo_pago,
        ),
        "detalle": None,
    }


def validar_prestamo_personal(
    prestamista: str,
    tipo_relacion: str,
    monto_inicial: float,
    saldo_actual: float,
    tasa: float,
    valor_cuota: float,
    proximo_pago: date,
) -> dict:
    _exigir(not prestamista.strip(), "Ingresa el nombre del prestamista o acreedor.")
    _exigir(saldo_actual <= 0, "El saldo pendiente debe ser mayor a cero.")
    _exigir(
        monto_inicial > 0 and saldo_actual > monto_inicial,
        "El saldo pendiente no puede superar el monto inicial.",
    )
    _exigir(valor_cuota <= 0, "El abono mensual acordado debe ser mayor a cero.")

    tiene_intereses = tasa > 0
    return {
        "base": _base_deuda(
            entidad=f"{prestamista.strip()} ({tipo_relacion})",
            monto_inicial=monto_inicial or saldo_actual,
            saldo_actual=saldo_actual,
            tasa=tasa if tiene_intereses else None,
            periodicidad_tasa="MENSUAL" if tiene_intereses else None,
            tipo_tasa=None,
            plazo_meses=None,
            valor_cuota=valor_cuota,
            proxima_cuota=None,
            proximo_pago=proximo_pago,
            tiene_intereses=tiene_intereses,
        ),
        "detalle": None,
    }


def validar_consumo(
    entidad: str,
    articulo: str,
    monto_inicial: float,
    saldo_actual: float,
    tasa: float,
    periodicidad_tasa: str,
    total_cuotas: int,
    cuota_proxima: int,
    valor_cuota: float,
    proximo_pago: date,
) -> dict:
    _exigir(not entidad.strip(), "Ingresa la entidad o comercio del crédito.")
    _exigir(saldo_actual <= 0, "El saldo actual debe ser mayor a cero.")
    _exigir(
        monto_inicial > 0 and saldo_actual > monto_inicial,
        "El saldo actual no puede ser mayor al monto inicial.",
    )
    _exigir(cuota_proxima > total_cuotas, "La próxima cuota no puede ser superior al total de cuotas.")
    _exigir(valor_cuota <= 0, "El valor de la cuota mensual debe ser mayor a cero.")

    nombre = entidad.strip()
    if articulo.strip():
        nombre += f" ({articulo.strip()})"
    # La columna deudas.entidad admite 100 caracteres y el nombre lleva el artículo entre paréntesis.
    _exigir(len(nombre) > 100, "El comercio y el artículo juntos no pueden superar los 100 caracteres.")

    return {
        "base": _base_credito(
            entidad=nombre,
            monto_inicial=monto_inicial or saldo_actual,
            saldo_actual=saldo_actual,
            tasa=tasa,
            periodicidad_tasa=periodicidad_tasa,
            plazo_meses=total_cuotas,
            valor_cuota=valor_cuota,
            proxima_cuota=cuota_proxima,
            proximo_pago=proximo_pago,
        ),
        "detalle": None,
    }


# Slugs de URL -> (código en tipos_deuda, función de validación/cálculo).
VALIDADORES_POR_TIPO = {
    "hipotecario": ("HIPOTECARIO", validar_hipotecario),
    "tarjeta": ("TARJETA", validar_tarjeta),
    "vehiculo": ("VEHICULO", validar_vehiculo),
    "educativo": ("EDUCATIVO", validar_educativo),
    "libre_inversion": ("LIBRE_INVERSION", validar_libre_inversion),
    "prestamo_personal": ("PRESTAMO_PERSONAL", validar_prestamo_personal),
    "consumo": ("CONSUMO", validar_consumo),
    "otros": ("OTRO", validar_otros),
}
