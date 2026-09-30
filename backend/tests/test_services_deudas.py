from datetime import date

import pytest

from backend.services.deudas import (
    validar_consumo,
    validar_hipotecario,
    validar_libre_inversion,
    validar_prestamo_personal,
    validar_tarjeta,
    validar_vehiculo,
)


def test_hipotecario_ejemplo_claude_md():
    # Ejemplo de la sección 9 de CLAUDE.md: 20 años, cuota 22 -> plazo 240.
    resultado = validar_hipotecario(
        entidad="Bancolombia",
        monto_inicial=100_000_000.0,
        saldo_actual=90_000_000.0,
        tasa=11.0,
        periodicidad_tasa="EA",
        tipo_tasa="FIJA",
        anos=20,
        meses=0,
        valor_cuota=994_114.88,
        cuota_proxima=22,
        proximo_pago=date(2026, 9, 17),
    )

    base = resultado["base"]
    assert base["plazo_meses"] == 240
    assert base["proxima_cuota"] == 22
    assert resultado["detalle"] is None


def test_hipotecario_saldo_mayor_a_monto_inicial_es_invalido():
    with pytest.raises(ValueError, match="no puede ser mayor al monto inicial"):
        validar_hipotecario(
            entidad="Banco X",
            monto_inicial=1_000_000.0,
            saldo_actual=2_000_000.0,
            tasa=10.0,
            periodicidad_tasa="EA",
            tipo_tasa="FIJA",
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
            periodicidad_tasa="EA",
            tipo_tasa="FIJA",
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
            ultimos_digitos="1234",
            cupo_total=500_000.0,
            saldo_actual=800_000.0,
            tasa=2.5,
            periodicidad_tasa="MENSUAL",
            pago_minimo=50_000.0,
            cuota_manejo=10_000.0,
            dia_corte=15,
            dia_pago=5,
            proximo_pago=date.today(),
        )


def test_tarjeta_valida_no_tiene_plazo_fijo():
    resultado = validar_tarjeta(
        entidad="Bancolombia",
        franquicia="Visa",
        ultimos_digitos="1234",
        cupo_total=800_000.0,
        saldo_actual=600_000.0,
        tasa=2.5,
        periodicidad_tasa="MENSUAL",
        pago_minimo=50_000.0,
        cuota_manejo=10_000.0,
        dia_corte=15,
        dia_pago=5,
        proximo_pago=date.today(),
    )

    assert resultado["base"]["plazo_meses"] is None
    assert resultado["detalle"]["dia_corte"] == 15
    assert resultado["detalle"]["dia_pago"] == 5


def test_vehiculo_calcula_plazo_en_meses():
    resultado = validar_vehiculo(
        entidad="Sufi Bancolombia",
        monto_inicial=40_000_000.0,
        saldo_actual=30_000_000.0,
        tasa=14.5,
        periodicidad_tasa="EA",
        anos=5,
        meses=0,
        valor_cuota=900_000.0,
        cuota_proxima=10,
        proximo_pago=date.today(),
        tipo_vehiculo="AUTOMOVIL",
        marca="Mazda",
        modelo="CX-30",
        anio=2023,
        placa="ABC123",
    )

    assert resultado["base"]["plazo_meses"] == 60
    assert resultado["detalle"]["marca"] == "Mazda"


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

    base = resultado["base"]
    assert base["tiene_intereses"] is False
    assert base["periodicidad_tasa"] is None
    assert base["monto_inicial"] == 200_000.0  # usa saldo_actual como fallback


def test_consumo_proxima_cuota_no_puede_superar_total():
    with pytest.raises(ValueError, match="no puede ser superior al total de cuotas"):
        validar_consumo(
            entidad="Alkosto",
            articulo="Computador",
            monto_inicial=2_000_000.0,
            saldo_actual=1_500_000.0,
            tasa=1.8,
            periodicidad_tasa="MENSUAL",
            total_cuotas=12,
            cuota_proxima=13,
            valor_cuota=180_000.0,
            proximo_pago=date.today(),
        )


def test_libre_inversion_calcula_plazo():
    resultado = validar_libre_inversion(
        entidad="BBVA",
        monto_inicial=5_000_000.0,
        saldo_actual=3_000_000.0,
        tasa=15.0,
        periodicidad_tasa="EA",
        total_meses=36,
        cuota_proxima=10,
        valor_cuota=200_000.0,
        proximo_pago=date.today(),
    )

    assert resultado["base"]["plazo_meses"] == 36
    assert resultado["base"]["proxima_cuota"] == 10
