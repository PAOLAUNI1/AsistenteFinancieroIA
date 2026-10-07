"""
Reglas que cumplen los ocho tipos de deuda, probadas con los mismos casos para todos:
registro, aislamiento por usuario, borrado y validaciones comunes.
"""

import copy
import json

import pytest

PAGO = "2026-12-01"

# Un cuerpo válido para cada POST /deudas/<tipo>.
VALIDOS = {
    "hipotecario": {
        "entidad": "Banco", "monto_inicial": 94_000_000, "saldo_actual": 89_800_000, "tasa": 11,
        "anos": 20, "valor_cuota": 994_115, "cuota_proxima": 23, "proximo_pago": PAGO,
        "fecha_inicio": "2025-01-15",
    },
    "tarjeta": {
        "entidad": "Banco", "cupo_total": 800_000, "saldo_actual": 600_000, "tasa": 2.5,
        "dia_corte": 15, "dia_pago": 5,
    },
    "vehiculo": {
        "entidad": "Banco", "monto_inicial": 45_000_000, "saldo_actual": 32_500_000, "tasa": 14.5,
        "anos": 5, "valor_cuota": 950_000, "cuota_proxima": 16, "proximo_pago": PAGO,
        "fecha_inicio": "2024-01-10",
    },
    "educativo": {
        "entidad": "CUN", "monto_inicial": 2_752_145, "saldo_actual": 2_752_145, "tasa": 0,
        "plazo_meses": 5, "valor_cuota": 550_429, "cuota_proxima": 1, "proximo_pago": PAGO,
        "fecha_inicio": "2025-09-30",
    },
    "libre_inversion": {
        "entidad": "Banco", "monto_inicial": 10_000_000, "saldo_actual": 8_000_000, "tasa": 1.5,
        "periodicidad_tasa": "MENSUAL", "total_meses": 36, "cuota_proxima": 5,
        "valor_cuota": 350_000, "proximo_pago": PAGO,
    },
    "prestamo_personal": {
        "prestamista": "Ana", "tipo_relacion": "Amigo", "monto_inicial": 1_000_000,
        "saldo_actual": 800_000, "tasa": 0, "valor_cuota": 100_000, "proximo_pago": PAGO,
    },
    "consumo": {
        "entidad": "Alkosto", "articulo": "Computador", "monto_inicial": 2_000_000,
        "saldo_actual": 1_500_000, "tasa": 1.8, "total_cuotas": 12, "cuota_proxima": 1,
        "valor_cuota": 180_000, "proximo_pago": PAGO,
    },
    "otros": {
        "entidad": "Juan", "tipo_credito": "PRESTAMO_FAMILIAR", "monto_inicial": 700_000,
        "saldo_actual": 700_000, "tasa": 0, "plazo_meses": 8, "cuota_proxima": 1,
        "valor_cuota": 87_500, "proximo_pago": PAGO, "fecha_inicio": "2025-10-01",
    },
}

CODIGOS = {
    "hipotecario": "HIPOTECARIO", "tarjeta": "TARJETA", "vehiculo": "VEHICULO",
    "educativo": "EDUCATIVO", "libre_inversion": "LIBRE_INVERSION",
    "prestamo_personal": "PRESTAMO_PERSONAL", "consumo": "CONSUMO", "otros": "OTRO",
}

TIPOS = list(VALIDOS)


def _con(tipo, **cambios):
    cuerpo = copy.deepcopy(VALIDOS[tipo])
    cuerpo.update(cambios)
    return cuerpo


def _registrar(client, tipo, usuario_id, cuerpo=None):
    return client.post(
        f"/deudas/{tipo}", params={"usuario_id": usuario_id}, json=cuerpo or VALIDOS[tipo]
    )


@pytest.mark.parametrize("tipo", TIPOS)
def test_un_cuerpo_valido_se_registra_con_su_tipo(client, usuario_id, tipo):
    respuesta = _registrar(client, tipo, usuario_id)

    assert respuesta.status_code == 201, respuesta.text
    cuerpo = respuesta.json()
    assert cuerpo["tipo_codigo"] == CODIGOS[tipo]
    assert cuerpo["estado"] == "ACTIVA"
    assert cuerpo["saldo_actual"] == VALIDOS[tipo]["saldo_actual"]


@pytest.mark.parametrize("tipo", TIPOS)
def test_registrar_sin_token_responde_401(client, tipo):
    assert client.post(f"/deudas/{tipo}", json=VALIDOS[tipo]).status_code == 401


@pytest.mark.parametrize("tipo", TIPOS)
def test_una_deuda_registrada_aparece_solo_en_la_lista_de_su_dueno(client, usuario_id, tipo):
    id_deuda = _registrar(client, tipo, usuario_id).json()["id"]
    otro = client.post(
        "/usuarios",
        json={
            "nombre": "Otro", "correo": f"otro-{tipo}@example.com", "contrasena": "Segura1234",
            "acepta_terminos": True, "acepta_tratamiento_datos": True,
        },
    ).json()["id"]

    propias = client.get("/deudas", params={"usuario_id": usuario_id}).json()
    ajenas = client.get("/deudas", params={"usuario_id": otro}).json()

    assert [d["id"] for d in propias] == [id_deuda]
    assert ajenas == []


@pytest.mark.parametrize("tipo", TIPOS)
def test_una_deuda_se_elimina_y_otro_usuario_no_puede_eliminarla(client, usuario_id, tipo):
    id_deuda = _registrar(client, tipo, usuario_id).json()["id"]
    otro = client.post(
        "/usuarios",
        json={
            "nombre": "Otro", "correo": f"intruso-{tipo}@example.com", "contrasena": "Segura1234",
            "acepta_terminos": True, "acepta_tratamiento_datos": True,
        },
    ).json()["id"]

    assert client.delete(f"/deudas/{id_deuda}", params={"usuario_id": otro}).status_code == 404
    assert client.delete(f"/deudas/{id_deuda}", params={"usuario_id": usuario_id}).status_code == 204
    assert client.get("/deudas", params={"usuario_id": usuario_id}).json() == []


@pytest.mark.parametrize("tipo", ["hipotecario", "tarjeta", "vehiculo", "educativo", "otros"])
def test_una_deuda_inactiva_queda_cancelada(client, usuario_id, tipo):
    respuesta = _registrar(client, tipo, usuario_id, _con(tipo, activa=False))

    assert respuesta.status_code == 201
    assert respuesta.json()["estado"] == "CANCELADA"


# El saldo nunca puede superar el monto (o el cupo, en la tarjeta).
SALDO_MAYOR = {
    "hipotecario": {"saldo_actual": 94_000_001},
    "tarjeta": {"saldo_actual": 800_001},
    "vehiculo": {"saldo_actual": 45_000_001},
    "educativo": {"saldo_actual": 2_752_146},
    "libre_inversion": {"saldo_actual": 10_000_001},
    "prestamo_personal": {"saldo_actual": 1_000_001},
    "consumo": {"saldo_actual": 2_000_001},
    "otros": {"saldo_actual": 700_001},
}


@pytest.mark.parametrize("tipo", TIPOS)
def test_el_saldo_no_puede_superar_el_monto_o_el_cupo(client, usuario_id, tipo):
    respuesta = _registrar(client, tipo, usuario_id, _con(tipo, **SALDO_MAYOR[tipo]))

    assert respuesta.status_code == 422


# La próxima cuota no puede pasar del total de cuotas.
CUOTA_FUERA_DEL_PLAZO = {
    "hipotecario": {"cuota_proxima": 241},
    "vehiculo": {"cuota_proxima": 61},
    "educativo": {"cuota_proxima": 6},
    "libre_inversion": {"cuota_proxima": 37},
    "consumo": {"cuota_proxima": 13},
    "otros": {"cuota_proxima": 9},
}


@pytest.mark.parametrize("tipo", list(CUOTA_FUERA_DEL_PLAZO))
def test_la_proxima_cuota_no_puede_superar_el_total(client, usuario_id, tipo):
    respuesta = _registrar(client, tipo, usuario_id, _con(tipo, **CUOTA_FUERA_DEL_PLAZO[tipo]))

    assert respuesta.status_code == 422


@pytest.mark.parametrize("tipo", ["hipotecario", "vehiculo", "educativo", "otros"])
def test_la_fecha_de_inicio_no_puede_ser_posterior_al_proximo_pago(client, usuario_id, tipo):
    respuesta = _registrar(client, tipo, usuario_id, _con(tipo, fecha_inicio="2027-06-01"))

    assert respuesta.status_code == 422


@pytest.mark.parametrize("tipo", TIPOS)
def test_una_entidad_vacia_se_rechaza(client, usuario_id, tipo):
    campo = "prestamista" if tipo == "prestamo_personal" else "entidad"

    assert _registrar(client, tipo, usuario_id, _con(tipo, **{campo: "   "})).status_code == 422


@pytest.mark.parametrize("tipo", TIPOS)
def test_un_monto_infinito_se_rechaza(client, usuario_id, tipo):
    # JSON estándar no admite Infinity, pero Python lo escribe: el servidor debe rechazarlo.
    cuerpo = json.dumps(_con(tipo, saldo_actual=float("inf")), allow_nan=True)

    respuesta = client.post(
        f"/deudas/{tipo}",
        params={"usuario_id": usuario_id},
        content=cuerpo,
        headers={"Content-Type": "application/json"},
    )

    assert respuesta.status_code == 422


def test_el_listado_trae_los_ocho_tipos_con_su_nombre(client, usuario_id):
    for tipo in TIPOS:
        assert _registrar(client, tipo, usuario_id).status_code == 201

    codigos = {d["tipo_codigo"] for d in client.get("/deudas", params={"usuario_id": usuario_id}).json()}

    assert codigos == set(CODIGOS.values())


def test_el_analisis_solo_suma_las_deudas_activas(client, usuario_id):
    _registrar(client, "hipotecario", usuario_id)  # activa: 89.800.000
    _registrar(client, "tarjeta", usuario_id, _con("tarjeta", activa=False))  # cancelada: no suma

    analisis = client.post(
        "/analisis", params={"usuario_id": usuario_id}, json={"compras_no_esenciales": 0}
    ).json()

    assert analisis["deuda_total"] == 89_800_000


CLAVES_ANALISIS = {
    "ingresos_totales", "gastos_totales", "saldo_disponible", "porcentaje_gasto",
    "score_financiero", "nivel_gasto", "deuda_total", "pago_sugerido_deuda",
    "ahorro_semanal_sugerido", "ahorro_mensual_sugerido", "ahorro_anual_proyectado",
    "meta_ahorro_anual", "meta_alcanzable",
}


def test_el_analisis_responde_con_todos_sus_campos(client, usuario_id):
    respuesta = client.post("/analisis", params={"usuario_id": usuario_id}, json={})

    assert respuesta.status_code == 200
    assert set(respuesta.json()) == CLAVES_ANALISIS
    assert respuesta.json()["meta_alcanzable"] is None  # sin meta definida


@pytest.mark.parametrize("valor", [-1, 10**14])
def test_las_compras_no_esenciales_deben_estar_en_rango(client, usuario_id, valor):
    respuesta = client.post(
        "/analisis", params={"usuario_id": usuario_id}, json={"compras_no_esenciales": valor}
    )

    assert respuesta.status_code == 422
