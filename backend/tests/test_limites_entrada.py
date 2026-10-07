"""Datos fuera de rango deben dar 422 (y no un error de la base de datos)."""
import pytest


def _consumo(**cambios):
    datos = {
        "entidad": "Alkosto",
        "monto_inicial": 100.0,
        "saldo_actual": 80.0,
        "tasa": 1.5,
        "total_cuotas": 12,
        "cuota_proxima": 1,
        "valor_cuota": 10.0,
        "proximo_pago": "2026-09-17",
    }
    datos.update(cambios)
    return datos


def _prestamo_personal(**cambios):
    datos = {
        "prestamista": "Tío Pedro",
        "monto_inicial": 100.0,
        "saldo_actual": 80.0,
        "valor_cuota": 10.0,
        "proximo_pago": "2026-09-17",
    }
    datos.update(cambios)
    return datos


def _hipotecario(**cambios):
    datos = {
        "entidad": "Bancolombia",
        "monto_inicial": 100_000_000.0,
        "saldo_actual": 90_000_000.0,
        "tasa": 11.0,
        "anos": 20,
        "valor_cuota": 994114.88,
        "cuota_proxima": 22,
        "proximo_pago": "2026-09-17",
    }
    datos.update(cambios)
    return datos


def _post(client, usuario_id, ruta, payload):
    return client.post(f"/deudas/{ruta}", params={"usuario_id": usuario_id}, json=payload)


def test_consumo_y_prestamo_personal_validos_se_registran(client, usuario_id):
    assert _post(client, usuario_id, "consumo", _consumo()).status_code == 201
    assert _post(client, usuario_id, "prestamo_personal", _prestamo_personal()).status_code == 201


def test_consumo_con_saldo_mayor_al_monto_da_422(client, usuario_id):
    respuesta = _post(client, usuario_id, "consumo", _consumo(monto_inicial=100.0, saldo_actual=500.0))
    assert respuesta.status_code == 422


def test_prestamo_personal_con_saldo_mayor_al_monto_da_422(client, usuario_id):
    respuesta = _post(
        client, usuario_id, "prestamo_personal", _prestamo_personal(monto_inicial=100.0, saldo_actual=500.0)
    )
    assert respuesta.status_code == 422


@pytest.mark.parametrize("tasa", [1000.0, 100.5])
def test_tasa_sobre_el_tope_da_422(client, usuario_id, tasa):
    assert _post(client, usuario_id, "hipotecario", _hipotecario(tasa=tasa)).status_code == 422


def test_tasa_que_se_redondea_a_cero_no_pasa_como_hipotecario(client, usuario_id):
    assert _post(client, usuario_id, "hipotecario", _hipotecario(tasa=0.00001)).status_code == 422


def test_tasa_que_se_redondea_a_cero_en_consumo_queda_sin_intereses(client, usuario_id):
    respuesta = _post(client, usuario_id, "consumo", _consumo(tasa=0.00001))
    assert respuesta.status_code == 201
    assert respuesta.json()["tiene_intereses"] is False


def test_monto_sobre_el_tope_da_422(client, usuario_id):
    respuesta = _post(
        client, usuario_id, "hipotecario", _hipotecario(monto_inicial=1e15, saldo_actual=1e14)
    )
    assert respuesta.status_code == 422


def test_infinito_y_nan_dan_422(client, usuario_id):
    for valor in ("Infinity", "NaN"):
        cuerpo = '{"entidad": "X", "monto_inicial": 100, "saldo_actual": %s, "tasa": 1, "anos": 1, "valor_cuota": 10, "cuota_proxima": 1, "proximo_pago": "2026-09-17"}' % valor
        respuesta = client.post(
            "/deudas/hipotecario",
            params={"usuario_id": usuario_id},
            content=cuerpo,
            headers={"Content-Type": "application/json"},
        )
        assert respuesta.status_code == 422


@pytest.mark.parametrize(
    "ruta,payload",
    [
        ("hipotecario", _hipotecario(entidad="B" * 101)),
        ("consumo", _consumo(articulo="a" * 31)),
        ("prestamo_personal", _prestamo_personal(prestamista="p" * 61)),
        ("hipotecario", _hipotecario(anos=500)),
    ],
)
def test_textos_y_plazos_demasiado_largos_dan_422(client, usuario_id, ruta, payload):
    assert _post(client, usuario_id, ruta, payload).status_code == 422


def test_nombre_de_usuario_solo_espacios_da_422(client):
    respuesta = client.post(
        "/usuarios",
        json={
            "nombre": "    ",
            "correo": "espacios@example.com",
            "contrasena": "Segura1234",
            "acepta_terminos": True,
            "acepta_tratamiento_datos": True,
        },
    )
    assert respuesta.status_code == 422


def test_cantidad_de_hijos_absurda_da_422(client):
    respuesta = client.post(
        "/usuarios",
        json={
            "nombre": "Ana",
            "correo": "hijos@example.com",
            "contrasena": "Segura1234",
            "cantidad_hijos": 300,
            "acepta_terminos": True,
            "acepta_tratamiento_datos": True,
        },
    )
    assert respuesta.status_code == 422


def test_el_422_no_devuelve_el_valor_recibido(client):
    respuesta = client.post(
        "/usuarios",
        json={"nombre": "Ana", "correo": "no-es-correo", "contrasena": "Secreta12345"},
    )
    assert respuesta.status_code == 422
    assert "Secreta12345" not in respuesta.text
