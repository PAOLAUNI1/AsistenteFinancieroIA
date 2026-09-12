"""
Validación y cálculo para cada uno de los 7 tipos de deuda (sección 4 de
CLAUDE.md), migrados de deudas/*.py quitando toda línea de Streamlit (st.*).

Cada función recibe los datos ya parseados (floats/ints, no strings con
formato "$1.000.000") y devuelve el dict listo para persistir en el modelo
Deuda. Si algo no es válido, levanta ValueError con el mismo mensaje que
mostraba el formulario en Streamlit, para no reinventar las reglas ya
definidas en la sección 10 de CLAUDE.md.
"""

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
) -> dict:
    total_cuotas = (anos * 12) + meses
    cuotas_pendientes = max(total_cuotas - cuota_proxima + 1, 0)

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
    if total_cuotas <= 0:
        raise ValueError("El plazo del crédito debe ser mayor a 0 meses.")
    if cuota_proxima > total_cuotas:
        raise ValueError("La próxima cuota no puede superar el total de cuotas.")
    if valor_cuota <= 0:
        raise ValueError("El valor de la cuota mensual debe ser mayor que cero.")

    return {
        "tipo": "Crédito hipotecario",
        "icono": "🏠",
        "entidad": entidad.strip(),
        "monto_inicial": monto_inicial,
        "saldo_actual": saldo_actual,
        "tasa": tasa,
        "periodicidad_tasa": periodicidad_tasa,
        "tipo_tasa": tipo_tasa,
        "anos": anos,
        "meses": meses,
        "total_cuotas": str(total_cuotas),
        "cuota_proxima": cuota_proxima,
        "cuotas_pendientes": str(cuotas_pendientes),
        "valor_cuota": valor_cuota,
        "proximo_pago": str(proximo_pago),
        "detalle": {},
    }


def validar_tarjeta(
    entidad: str,
    franquicia: str,
    cupo_total: float,
    saldo_actual: float,
    tasa: float,
    periodicidad_tasa: str,
    pago_minimo: float,
    cuota_manejo: float,
    dia_corte: int,
    proximo_pago: date,
) -> dict:
    if not entidad.strip():
        raise ValueError("Ingresa la entidad financiera emisora.")
    if cupo_total <= 0:
        raise ValueError("El cupo total aprobado debe ser mayor a cero.")
    if saldo_actual <= 0:
        raise ValueError("El saldo adeudado debe ser mayor a cero.")
    if saldo_actual > cupo_total:
        raise ValueError("El saldo utilizado no puede superar el cupo aprobado.")
    if pago_minimo <= 0:
        raise ValueError("El pago mínimo mensual debe ser mayor a cero.")

    cuota_total_mes = pago_minimo + cuota_manejo
    nombre_tarjeta = f"{entidad.strip()} ({franquicia})"

    return {
        "tipo": "Tarjeta de crédito",
        "icono": "💳",
        "entidad": nombre_tarjeta,
        "monto_inicial": cupo_total,
        "saldo_actual": saldo_actual,
        "tasa": tasa,
        "periodicidad_tasa": periodicidad_tasa,
        "tipo_tasa": "Variable",
        "anos": 0,
        "meses": 0,
        "total_cuotas": "Rotativo",
        "cuota_proxima": 1,
        "cuotas_pendientes": "Rotativo",
        "valor_cuota": cuota_total_mes,
        "proximo_pago": str(proximo_pago),
        "detalle": {
            "cupo_total": cupo_total,
            "pago_minimo": pago_minimo,
            "cuota_manejo": cuota_manejo,
            "dia_corte": dia_corte,
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
) -> dict:
    total_cuotas = (anos * 12) + meses
    cuotas_pendientes = max(total_cuotas - cuota_proxima + 1, 0)

    if not entidad.strip():
        raise ValueError("Ingresa la entidad financiera.")
    if monto_inicial <= 0:
        raise ValueError("El monto financiado debe ser mayor a cero.")
    if saldo_actual <= 0:
        raise ValueError("El saldo actual debe ser mayor a cero.")
    if saldo_actual > monto_inicial:
        raise ValueError("El saldo actual no puede ser mayor al monto financiado.")
    if total_cuotas <= 0:
        raise ValueError("El plazo del crédito debe ser mayor a 0 meses.")
    if valor_cuota <= 0:
        raise ValueError("El valor de la cuota debe ser mayor a cero.")

    return {
        "tipo": "Crédito de vehículo",
        "icono": "🚗",
        "entidad": entidad.strip(),
        "monto_inicial": monto_inicial,
        "saldo_actual": saldo_actual,
        "tasa": tasa,
        "periodicidad_tasa": periodicidad_tasa,
        "tipo_tasa": "Fija",
        "anos": anos,
        "meses": meses,
        "total_cuotas": str(total_cuotas),
        "cuota_proxima": cuota_proxima,
        "cuotas_pendientes": str(cuotas_pendientes),
        "valor_cuota": valor_cuota,
        "proximo_pago": str(proximo_pago),
        "detalle": {},
    }


def validar_educativo(
    entidad: str,
    carrera: str,
    estado_credito: str,
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

    nombre = entidad.strip()
    if carrera.strip():
        nombre += f" ({carrera.strip()})"

    return {
        "tipo": "Crédito educativo",
        "icono": "🎓",
        "entidad": nombre,
        "monto_inicial": monto_inicial or saldo_actual,
        "saldo_actual": saldo_actual,
        "tasa": tasa,
        "periodicidad_tasa": periodicidad_tasa,
        "tipo_tasa": estado_credito,
        "anos": cuotas_pendientes // 12,
        "meses": cuotas_pendientes % 12,
        "total_cuotas": str(cuotas_pendientes),
        "cuota_proxima": 1,
        "cuotas_pendientes": str(cuotas_pendientes),
        "valor_cuota": valor_cuota,
        "proximo_pago": str(proximo_pago),
        "detalle": {"estado_credito": estado_credito},
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
    cuotas_pendientes = max(total_meses - cuota_proxima + 1, 0)

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
        "tipo": "Préstamo de libre inversión",
        "icono": "💰",
        "entidad": entidad.strip(),
        "monto_inicial": monto_inicial,
        "saldo_actual": saldo_actual,
        "tasa": tasa,
        "periodicidad_tasa": periodicidad_tasa,
        "tipo_tasa": "Fija",
        "anos": total_meses // 12,
        "meses": total_meses % 12,
        "total_cuotas": str(total_meses),
        "cuota_proxima": cuota_proxima,
        "cuotas_pendientes": str(cuotas_pendientes),
        "valor_cuota": valor_cuota,
        "proximo_pago": str(proximo_pago),
        "detalle": {},
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
        "tipo": "Préstamo personal",
        "icono": "🤝",
        "entidad": nombre,
        "monto_inicial": monto_inicial or saldo_actual,
        "saldo_actual": saldo_actual,
        "tasa": tasa,
        "periodicidad_tasa": "Mensual" if tasa > 0 else "Sin interés",
        "tipo_tasa": "Personal / Informal",
        "anos": 0,
        "meses": 0,
        "total_cuotas": "Pactado",
        "cuota_proxima": 1,
        "cuotas_pendientes": "Acuerdo mutuo",
        "valor_cuota": valor_cuota,
        "proximo_pago": str(proximo_pago),
        "detalle": {"tipo_relacion": tipo_relacion},
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
    cuotas_pendientes = max(total_cuotas - cuota_proxima + 1, 0)

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
        "tipo": "Crédito de consumo",
        "icono": "🛒",
        "entidad": nombre,
        "monto_inicial": monto_inicial or saldo_actual,
        "saldo_actual": saldo_actual,
        "tasa": tasa,
        "periodicidad_tasa": periodicidad_tasa,
        "tipo_tasa": "Fija",
        "anos": total_cuotas // 12,
        "meses": total_cuotas % 12,
        "total_cuotas": str(total_cuotas),
        "cuota_proxima": cuota_proxima,
        "cuotas_pendientes": str(cuotas_pendientes),
        "valor_cuota": valor_cuota,
        "proximo_pago": str(proximo_pago),
        "detalle": {},
    }


# Slugs de URL -> función de validación/cálculo (paralelo a TIPOS_DEUDAS en
# deudas/__init__.py, que usa el nombre completo como clave para la UI).
VALIDADORES_POR_TIPO = {
    "hipotecario": validar_hipotecario,
    "tarjeta": validar_tarjeta,
    "vehiculo": validar_vehiculo,
    "educativo": validar_educativo,
    "libre_inversion": validar_libre_inversion,
    "prestamo_personal": validar_prestamo_personal,
    "consumo": validar_consumo,
}
