"""
Fija el texto exacto de cada error de validación de las deudas.

La app muestra estos mensajes tal cual, así que unificar o reordenar los validadores
no puede cambiarlos. Cada fila es (tipo, regla incumplida, mensaje esperado).
"""

from datetime import date

import pytest

from backend.routers.deudas import ESQUEMAS_POR_TIPO
from backend.services.deudas import VALIDADORES_POR_TIPO
from backend.tests.test_registro_por_tipo import VALIDOS


def _entidad_vacia(d):
    return {("prestamista" if "prestamista" in d else "entidad"): "   "}


def _saldo_mayor(d):
    # En la tarjeta el tope es el cupo; en las demás, el monto inicial.
    return {"saldo_actual": (d["cupo_total"] if "cupo_total" in d else d["monto_inicial"]) + 1}


REGLAS = {
    "entidad_vacia": _entidad_vacia,
    "saldo_cero": lambda d: {"saldo_actual": 0},
    "saldo_mayor": _saldo_mayor,
    "cuota_fuera_plazo": lambda d: {"cuota_proxima": 1000},
    "inicio_posterior": lambda d: {"fecha_inicio": date(2030, 1, 1)},
    "cuota_cero": lambda d: {"valor_cuota": 0},
    "sin_plazo": lambda d: {"anos": 0, "meses": 0},
    "plazo_cero": lambda d: {"plazo_meses": 0},
}

MENSAJES = [
    ("hipotecario", "entidad_vacia", "Ingresa la entidad financiera."),
    ("hipotecario", "saldo_cero", "El saldo actual debe ser mayor que cero."),
    ("hipotecario", "saldo_mayor", "El saldo actual no puede ser mayor al monto inicial."),
    ("hipotecario", "cuota_fuera_plazo", "La próxima cuota no puede superar el total de cuotas."),
    ("hipotecario", "inicio_posterior", "La fecha de inicio no puede ser posterior al próximo pago."),
    ("hipotecario", "cuota_cero", "El valor de la cuota mensual debe ser mayor que cero."),
    ("hipotecario", "sin_plazo", "El plazo del crédito debe ser mayor a 0 meses."),
    ("tarjeta", "entidad_vacia", "Ingresa la entidad financiera emisora."),
    ("tarjeta", "saldo_cero", "El saldo adeudado debe ser mayor a cero."),
    ("tarjeta", "saldo_mayor", "El saldo utilizado no puede superar el cupo aprobado."),
    ("vehiculo", "entidad_vacia", "Ingresa la entidad financiera."),
    ("vehiculo", "saldo_cero", "El saldo actual debe ser mayor a cero."),
    ("vehiculo", "saldo_mayor", "El saldo actual no puede ser mayor al monto financiado."),
    ("vehiculo", "cuota_fuera_plazo", "La próxima cuota no puede superar el total de cuotas."),
    ("vehiculo", "inicio_posterior", "La fecha de inicio no puede ser posterior al próximo pago."),
    ("vehiculo", "cuota_cero", "El valor de la cuota debe ser mayor a cero."),
    ("vehiculo", "sin_plazo", "El plazo del crédito debe ser mayor a 0 meses."),
    ("educativo", "entidad_vacia", "Ingresa la entidad o institución del crédito educativo."),
    ("educativo", "saldo_cero", "El saldo actual debe ser mayor a cero."),
    ("educativo", "saldo_mayor", "El saldo actual no puede ser mayor al monto inicial."),
    ("educativo", "cuota_fuera_plazo", "La próxima cuota no puede superar el total de cuotas."),
    ("educativo", "inicio_posterior", "La fecha de inicio no puede ser posterior al próximo pago."),
    ("educativo", "cuota_cero", "El valor de la cuota mensual debe ser mayor a cero."),
    ("educativo", "plazo_cero", "El plazo debe ser mayor a 0 meses."),
    ("libre_inversion", "entidad_vacia", "Ingresa la entidad financiera."),
    ("libre_inversion", "saldo_cero", "El saldo pendiente debe ser mayor a cero."),
    ("libre_inversion", "saldo_mayor", "El saldo pendiente no puede superar el monto inicial."),
    ("libre_inversion", "cuota_fuera_plazo", "La próxima cuota no puede ser superior al total de cuotas."),
    ("libre_inversion", "cuota_cero", "El valor de la cuota mensual debe ser mayor a cero."),
    ("prestamo_personal", "entidad_vacia", "Ingresa el nombre del prestamista o acreedor."),
    ("prestamo_personal", "saldo_cero", "El saldo pendiente debe ser mayor a cero."),
    ("prestamo_personal", "saldo_mayor", "El saldo pendiente no puede superar el monto inicial."),
    ("prestamo_personal", "cuota_cero", "El abono mensual acordado debe ser mayor a cero."),
    ("consumo", "entidad_vacia", "Ingresa la entidad o comercio del crédito."),
    ("consumo", "saldo_cero", "El saldo actual debe ser mayor a cero."),
    ("consumo", "saldo_mayor", "El saldo actual no puede ser mayor al monto inicial."),
    ("consumo", "cuota_fuera_plazo", "La próxima cuota no puede ser superior al total de cuotas."),
    ("consumo", "cuota_cero", "El valor de la cuota mensual debe ser mayor a cero."),
    ("otros", "entidad_vacia", "Ingresa la entidad o la persona a quien le debes."),
    ("otros", "saldo_cero", "El saldo actual debe ser mayor a cero."),
    ("otros", "saldo_mayor", "El saldo actual no puede ser mayor al monto total."),
    ("otros", "cuota_fuera_plazo", "La próxima cuota no puede superar el total de cuotas."),
    ("otros", "inicio_posterior", "La fecha de inicio no puede ser posterior al próximo pago."),
    ("otros", "cuota_cero", "El valor de la cuota mensual debe ser mayor a cero."),
    ("otros", "plazo_cero", "El plazo debe ser mayor a 0 meses."),
]


def _validar(tipo, **cambios):
    _, validar = VALIDADORES_POR_TIPO[tipo]
    datos = ESQUEMAS_POR_TIPO[tipo](**VALIDOS[tipo]).model_dump()
    datos.update(cambios)
    return validar(**datos)


@pytest.mark.parametrize("tipo,regla,mensaje", MENSAJES, ids=[f"{t}-{r}" for t, r, _ in MENSAJES])
def test_cada_regla_incumplida_da_su_mensaje_exacto(tipo, regla, mensaje):
    cambios = REGLAS[regla](ESQUEMAS_POR_TIPO[tipo](**VALIDOS[tipo]).model_dump())

    with pytest.raises(ValueError) as error:
        _validar(tipo, **cambios)

    assert str(error.value) == mensaje


@pytest.mark.parametrize("tipo", list(VALIDOS))
def test_el_cuerpo_valido_de_cada_tipo_no_incumple_ninguna_regla(tipo):
    resultado = _validar(tipo)

    assert set(resultado) == {"base", "detalle"}
