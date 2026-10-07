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

    if not entidad.strip():
        raise ValueError("Ingresa la entidad financiera.")
    if monto_inicial <= 0:
        raise ValueError("El monto inicial debe ser mayor que cero.")
    if saldo_actual <= 0:
        raise ValueError("El saldo actual debe ser mayor que cero.")
    if saldo_actual > monto_inicial:
        raise ValueError("El saldo actual no puede ser mayor al monto inicial.")
    if tasa <= 0:
        raise ValueError("Ingresa una tasa de interés válida.")
    if plazo_meses <= 0:
        raise ValueError("El plazo del crédito debe ser mayor a 0 meses.")
    if cuota_proxima > plazo_meses:
        raise ValueError("La próxima cuota no puede superar el total de cuotas.")
    if valor_cuota <= 0:
        raise ValueError("El valor de la cuota mensual debe ser mayor que cero.")
    if fecha_inicio is not None and fecha_inicio > proximo_pago:
        raise ValueError("La fecha de inicio no puede ser posterior al próximo pago.")

    return {
        "base": {
            "entidad": entidad.strip(),
            "nombre": (nombre or "").strip() or None,
            "monto_inicial": monto_inicial,
            "saldo_actual": saldo_actual,
            "tiene_intereses": True,
            "tasa_interes": tasa,
            "periodicidad_tasa": periodicidad_tasa,
            "tipo_tasa": tipo_tasa,
            "plazo_meses": plazo_meses,
            "valor_cuota": valor_cuota,
            "proxima_cuota": cuota_proxima,
            "fecha_proximo_pago": proximo_pago,
            "fecha_inicio": fecha_inicio,
            "descripcion": (descripcion or "").strip() or None,
            "estado": "ACTIVA" if activa else "CANCELADA",
        },
        "detalle": None,
    }


def proxima_fecha_de_pago(dia_pago: int, hoy: date | None = None) -> date:
    """Próxima fecha (hoy incluido) en que cae el día de pago, ajustado al fin de mes."""
    hoy = hoy or date.today()
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
    if not entidad.strip():
        raise ValueError("Ingresa la entidad financiera emisora.")
    if cupo_total <= 0:
        raise ValueError("El cupo total aprobado debe ser mayor a cero.")
    if saldo_actual <= 0:
        raise ValueError("El saldo adeudado debe ser mayor a cero.")
    if saldo_actual > cupo_total:
        raise ValueError("El saldo utilizado no puede superar el cupo aprobado.")
    if pago_minimo < 0 or cuota_manejo < 0:
        raise ValueError("El pago mínimo y la cuota de manejo no pueden ser negativos.")

    cuota_total_mes = pago_minimo + cuota_manejo

    return {
        "base": {
            "entidad": entidad.strip(),
            "nombre": nombre.strip() if nombre and nombre.strip() else None,
            "descripcion": descripcion.strip() if descripcion and descripcion.strip() else None,
            "estado": "ACTIVA" if activa else "CANCELADA",
            "monto_inicial": cupo_total,
            "saldo_actual": saldo_actual,
            "tiene_intereses": tasa > 0,
            "tasa_interes": tasa,
            "periodicidad_tasa": periodicidad_tasa,
            "tipo_tasa": "VARIABLE",
            "plazo_meses": None,
            "valor_cuota": cuota_total_mes if cuota_total_mes > 0 else None,
            "proxima_cuota": None,
            "fecha_proximo_pago": proximo_pago or proxima_fecha_de_pago(dia_pago),
        },
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

    if not entidad.strip():
        raise ValueError("Ingresa la entidad financiera.")
    if monto_inicial <= 0:
        raise ValueError("El monto financiado debe ser mayor a cero.")
    if saldo_actual <= 0:
        raise ValueError("El saldo actual debe ser mayor a cero.")
    if saldo_actual > monto_inicial:
        raise ValueError("El saldo actual no puede ser mayor al monto financiado.")
    if plazo_meses <= 0:
        raise ValueError("El plazo del crédito debe ser mayor a 0 meses.")
    if cuota_proxima > plazo_meses:
        raise ValueError("La próxima cuota no puede superar el total de cuotas.")
    if valor_cuota <= 0:
        raise ValueError("El valor de la cuota debe ser mayor a cero.")
    if fecha_inicio is not None and fecha_inicio > proximo_pago:
        raise ValueError("La fecha de inicio no puede ser posterior al próximo pago.")

    return {
        "base": {
            "entidad": entidad.strip(),
            "nombre": (nombre or "").strip() or None,
            "monto_inicial": monto_inicial,
            "saldo_actual": saldo_actual,
            "tiene_intereses": tasa > 0,
            "tasa_interes": tasa,
            "periodicidad_tasa": periodicidad_tasa,
            "tipo_tasa": "FIJA",
            "plazo_meses": plazo_meses,
            "valor_cuota": valor_cuota,
            "proxima_cuota": cuota_proxima,
            "fecha_proximo_pago": proximo_pago,
            "fecha_inicio": fecha_inicio,
            "descripcion": (descripcion or "").strip() or None,
            "estado": "ACTIVA" if activa else "CANCELADA",
        },
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
    carrera: str,
    modalidad: str,
    cuotas_pendientes: int,
    monto_inicial: float,
    saldo_actual: float,
    tasa: float,
    periodicidad_tasa: str,
    valor_cuota: float,
    proximo_pago: date,
) -> dict:
    if not entidad.strip():
        raise ValueError("Ingresa la entidad o institución del crédito educativo.")
    if saldo_actual <= 0:
        raise ValueError("El saldo actual debe ser mayor a cero.")
    if valor_cuota <= 0:
        raise ValueError("El valor de la cuota mensual debe ser mayor a cero.")

    return {
        "base": {
            "entidad": entidad.strip(),
            "monto_inicial": monto_inicial or saldo_actual,
            "saldo_actual": saldo_actual,
            "tiene_intereses": tasa > 0,
            "tasa_interes": tasa,
            "periodicidad_tasa": periodicidad_tasa,
            "tipo_tasa": "FIJA",
            "plazo_meses": cuotas_pendientes,
            "valor_cuota": valor_cuota,
            "proxima_cuota": 1,
            "fecha_proximo_pago": proximo_pago,
        },
        "detalle": {
            "institucion": entidad.strip(),
            "programa": carrera.strip() or None,
            "modalidad": modalidad or None,
            "beneficiario": None,
        },
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
    if not entidad.strip():
        raise ValueError("Ingresa la entidad financiera.")
    if monto_inicial <= 0:
        raise ValueError("El monto inicial debe ser mayor a cero.")
    if saldo_actual <= 0:
        raise ValueError("El saldo pendiente debe ser mayor a cero.")
    if saldo_actual > monto_inicial:
        raise ValueError("El saldo pendiente no puede superar el monto inicial.")
    if cuota_proxima > total_meses:
        raise ValueError("La próxima cuota no puede ser superior al total de cuotas.")
    if valor_cuota <= 0:
        raise ValueError("El valor de la cuota mensual debe ser mayor a cero.")

    return {
        "base": {
            "entidad": entidad.strip(),
            "monto_inicial": monto_inicial,
            "saldo_actual": saldo_actual,
            "tiene_intereses": tasa > 0,
            "tasa_interes": tasa,
            "periodicidad_tasa": periodicidad_tasa,
            "tipo_tasa": "FIJA",
            "plazo_meses": total_meses,
            "valor_cuota": valor_cuota,
            "proxima_cuota": cuota_proxima,
            "fecha_proximo_pago": proximo_pago,
        },
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
    if not prestamista.strip():
        raise ValueError("Ingresa el nombre del prestamista o acreedor.")
    if saldo_actual <= 0:
        raise ValueError("El saldo pendiente debe ser mayor a cero.")
    if valor_cuota <= 0:
        raise ValueError("El abono mensual acordado debe ser mayor a cero.")

    nombre = f"{prestamista.strip()} ({tipo_relacion})"

    return {
        "base": {
            "entidad": nombre,
            "monto_inicial": monto_inicial or saldo_actual,
            "saldo_actual": saldo_actual,
            "tiene_intereses": tasa > 0,
            "tasa_interes": tasa if tasa > 0 else None,
            "periodicidad_tasa": "MENSUAL" if tasa > 0 else None,
            "tipo_tasa": None,
            "plazo_meses": None,
            "valor_cuota": valor_cuota,
            "proxima_cuota": None,
            "fecha_proximo_pago": proximo_pago,
        },
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
    if not entidad.strip():
        raise ValueError("Ingresa la entidad o comercio del crédito.")
    if saldo_actual <= 0:
        raise ValueError("El saldo actual debe ser mayor a cero.")
    if cuota_proxima > total_cuotas:
        raise ValueError("La próxima cuota no puede ser superior al total de cuotas.")
    if valor_cuota <= 0:
        raise ValueError("El valor de la cuota mensual debe ser mayor a cero.")

    nombre = entidad.strip()
    if articulo.strip():
        nombre += f" ({articulo.strip()})"

    return {
        "base": {
            "entidad": nombre,
            "monto_inicial": monto_inicial or saldo_actual,
            "saldo_actual": saldo_actual,
            "tiene_intereses": tasa > 0,
            "tasa_interes": tasa,
            "periodicidad_tasa": periodicidad_tasa,
            "tipo_tasa": "FIJA",
            "plazo_meses": total_cuotas,
            "valor_cuota": valor_cuota,
            "proxima_cuota": cuota_proxima,
            "fecha_proximo_pago": proximo_pago,
        },
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
}
