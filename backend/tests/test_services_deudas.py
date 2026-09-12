from datetime import date

import pytest

from backend.services.deudas import (
    validar_consumo,
    validar_hipotecario,
    validar_libre_inversion,
    validar_prestamo_personal,
    validar_tarjeta,
)


def test_hipotecario_ejemplo_claude_md():
    # Ejemplo de la sección 9 de CLAUDE.md: 20 años, cuota 22 -> 219 pendientes.
    resultado = validar_hipotecario(
        entidad="Bancolombia",
        monto_inicial=100_000_000.0,
        saldo_actual=90_000_000.0,
        tasa=11.0,
        periodicidad_tasa="Efectiva anual (EA)",
        tipo_tasa="Fija",
        anos=20,
        meses=0,
        valor_cuota=994_114.88,
        cuota_proxima=22,
        proximo_pago=date(2026, 9, 17),
    )

    assert resultado["total_cuotas"] == "240"
    assert resultado["cuotas_pendientes"] == "219"
    assert resultado["tipo"] == "Crédito hipotecario"


def test_hipotecario_saldo_mayor_a_monto_inicial_es_invalido():
    with pytest.raises(ValueError, match="no puede ser mayor al monto inicial"):
        validar_hipotecario(
            entidad="Banco X",
            monto_inicial=1_000_000.0,
            saldo_actual=2_000_000.0,
            tasa=10.0,
            periodicidad_tasa="Efectiva anual (EA)",
            tipo_tasa="Fija",
            anos=1,
            meses=0,
            valor_cuota=100_000.0,
            cuota_proxima=1,
            proximo_pago=date.today(),
        )


def test_hipotecario_entidad_vacia_es_invalida():
    with pytest.raises(ValueError, match="entidad financiera"):
        validar_hipotecario(
            entidad="   ",
            monto_inicial=1_000_000.0,
            saldo_actual=500_000.0,
            tasa=10.0,
            periodicidad_tasa="Efectiva anual (EA)",
            tipo_tasa="Fija",
            anos=1,
            meses=0,
            valor_cuota=100_000.0,
            cuota_proxima=1,
            proximo_pago=date.today(),
        )


def test_tarjeta_saldo_no_puede_superar_cupo():
    with pytest.raises(ValueError, match="no puede superar el cupo"):
        validar_tarjeta(
            entidad="Bancolombia",
            franquicia="Visa",
            cupo_total=500_000.0,
            saldo_actual=800_000.0,
            tasa=2.5,
            periodicidad_tasa="Mensual vencido (MV)",
            pago_minimo=50_000.0,
            cuota_manejo=10_000.0,
            dia_corte=15,
            proximo_pago=date.today(),
        )


def test_tarjeta_valida_es_rotativa():
    resultado = validar_tarjeta(
        entidad="Bancolombia",
        franquicia="Visa",
        cupo_total=800_000.0,
        saldo_actual=600_000.0,
        tasa=2.5,
        periodicidad_tasa="Mensual vencido (MV)",
        pago_minimo=50_000.0,
        cuota_manejo=10_000.0,
        dia_corte=15,
        proximo_pago=date.today(),
    )

    assert resultado["total_cuotas"] == "Rotativo"
    assert resultado["cuotas_pendientes"] == "Rotativo"
    assert resultado["detalle"]["dia_corte"] == 15


def test_prestamo_personal_sin_interes():
    resultado = validar_prestamo_personal(
        prestamista="Tío Carlos",
        tipo_relacion="Familiar",
        monto_inicial=0.0,
        saldo_actual=200_000.0,
        tasa=0.0,
        valor_cuota=50_000.0,
        proximo_pago=date.today(),
    )

    assert resultado["periodicidad_tasa"] == "Sin interés"
    assert resultado["monto_inicial"] == 200_000.0  # usa saldo_actual como fallback


def test_consumo_proxima_cuota_no_puede_superar_total():
    with pytest.raises(ValueError, match="no puede ser superior al total de cuotas"):
        validar_consumo(
            entidad="Alkosto",
            articulo="Computador",
            monto_inicial=2_000_000.0,
            saldo_actual=1_500_000.0,
            tasa=1.8,
            periodicidad_tasa="Mensual",
            total_cuotas=12,
            cuota_proxima=13,
            valor_cuota=180_000.0,
            proximo_pago=date.today(),
        )


def test_libre_inversion_calcula_cuotas_pendientes():
    resultado = validar_libre_inversion(
        entidad="BBVA",
        monto_inicial=5_000_000.0,
        saldo_actual=3_000_000.0,
        tasa=15.0,
        periodicidad_tasa="Efectiva anual (EA)",
        total_meses=36,
        cuota_proxima=10,
        valor_cuota=200_000.0,
        proximo_pago=date.today(),
    )

    assert resultado["cuotas_pendientes"] == "27"
