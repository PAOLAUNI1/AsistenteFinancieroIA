def test_registrar_hipotecario_y_listar(client, usuario_id):
    payload = {
        "entidad": "Bancolombia",
        "monto_inicial": 100_000_000.0,
        "saldo_actual": 90_000_000.0,
        "tasa": 11.0,
        "periodicidad_tasa": "EA",
        "tipo_tasa": "FIJA",
        "anos": 20,
        "meses": 0,
        "valor_cuota": 994114.88,
        "cuota_proxima": 22,
        "proximo_pago": "2026-09-17",
    }

    respuesta = client.post(
        "/deudas/hipotecario", params={"usuario_id": usuario_id}, json=payload
    )
    assert respuesta.status_code == 201
    cuerpo = respuesta.json()
    assert cuerpo["plazo_meses"] == 240
    assert cuerpo["cuotas_pendientes"] == 219
    assert cuerpo["tipo_codigo"] == "HIPOTECARIO"

    listado = client.get("/deudas", params={"usuario_id": usuario_id})
    assert listado.status_code == 200
    assert len(listado.json()) == 1
    assert listado.json()[0]["entidad"] == "Bancolombia"


def test_registrar_hipotecario_invalido_devuelve_422(client, usuario_id):
    payload = {
        "entidad": "Banco X",
        "monto_inicial": 1_000_000.0,
        "saldo_actual": 2_000_000.0,
        "tasa": 10.0,
        "valor_cuota": 100_000.0,
        "cuota_proxima": 1,
        "proximo_pago": "2026-01-01",
    }

    respuesta = client.post(
        "/deudas/hipotecario", params={"usuario_id": usuario_id}, json=payload
    )
    assert respuesta.status_code == 422


def test_deudas_requiere_usuario_id(client):
    respuesta = client.get("/deudas")
    assert respuesta.status_code == 422  # falta el query param obligatorio


def test_deudas_con_usuario_inexistente_devuelve_404(client):
    respuesta = client.get("/deudas", params={"usuario_id": 999})
    assert respuesta.status_code == 404


ACEPTACIONES = {"acepta_terminos": True, "acepta_tratamiento_datos": True}


def test_un_usuario_no_ve_las_deudas_de_otro(client):
    usuario_a = client.post(
        "/usuarios", json={"nombre": "A", "correo": "a@example.com", **ACEPTACIONES}
    ).json()["id"]
    usuario_b = client.post(
        "/usuarios", json={"nombre": "B", "correo": "b@example.com", **ACEPTACIONES}
    ).json()["id"]

    client.post(
        "/deudas/prestamo_personal",
        params={"usuario_id": usuario_a},
        json={
            "prestamista": "Juan Pérez",
            "saldo_actual": 200_000.0,
            "valor_cuota": 50_000.0,
            "proximo_pago": "2026-01-01",
        },
    )

    assert client.get("/deudas", params={"usuario_id": usuario_a}).json() != []
    assert client.get("/deudas", params={"usuario_id": usuario_b}).json() == []


def test_tarjeta_guarda_detalle_y_no_tiene_plazo_fijo(client, usuario_id):
    payload = {
        "entidad": "Bancolombia",
        "franquicia": "Visa",
        "cupo_total": 800000,
        "saldo_actual": 600000,
        "tasa": 2.5,
        "pago_minimo": 50000,
        "cuota_manejo": 10000,
        "dia_corte": 15,
        "dia_pago": 5,
        "proximo_pago": "2026-10-05",
    }
    respuesta = client.post(
        "/deudas/tarjeta", params={"usuario_id": usuario_id}, json=payload
    )
    assert respuesta.status_code == 201
    cuerpo = respuesta.json()
    assert cuerpo["plazo_meses"] is None
    assert cuerpo["detalle"]["dia_corte"] == 15
    assert cuerpo["detalle"]["dia_pago"] == 5


def test_eliminar_deuda(client, usuario_id):
    payload = {
        "prestamista": "Juan Pérez",
        "tipo_relacion": "Amigo / Compañero",
        "saldo_actual": 200_000.0,
        "valor_cuota": 50_000.0,
        "proximo_pago": "2026-01-01",
    }
    creada = client.post(
        "/deudas/prestamo_personal", params={"usuario_id": usuario_id}, json=payload
    ).json()

    eliminar = client.delete(f"/deudas/{creada['id']}", params={"usuario_id": usuario_id})
    assert eliminar.status_code == 204

    listado = client.get("/deudas", params={"usuario_id": usuario_id}).json()
    assert listado == []


def test_no_se_puede_eliminar_la_deuda_de_otro_usuario(client):
    usuario_a = client.post(
        "/usuarios", json={"nombre": "A", "correo": "a2@example.com", **ACEPTACIONES}
    ).json()["id"]
    usuario_b = client.post(
        "/usuarios", json={"nombre": "B", "correo": "b2@example.com", **ACEPTACIONES}
    ).json()["id"]

    deuda = client.post(
        "/deudas/prestamo_personal",
        params={"usuario_id": usuario_a},
        json={
            "prestamista": "Juan Pérez",
            "saldo_actual": 200_000.0,
            "valor_cuota": 50_000.0,
            "proximo_pago": "2026-01-01",
        },
    ).json()

    eliminar = client.delete(f"/deudas/{deuda['id']}", params={"usuario_id": usuario_b})
    assert eliminar.status_code == 404


def test_analisis_incluye_deuda_registrada(client, usuario_id):
    client.put(
        "/perfil",
        params={"usuario_id": usuario_id},
        json={
            "salario_mensual": 5_000_000,
            "otros_ingresos": 0,
            "alimentacion": 800_000,
            "transporte": 200_000,
            "vestimenta": 100_000,
            "entretenimiento": 150_000,
            "arriendo_hipoteca": 1_000_000,
            "servicios_publicos": 250_000,
        },
    )
    client.post(
        "/deudas/consumo",
        params={"usuario_id": usuario_id},
        json={
            "entidad": "Alkosto",
            "saldo_actual": 1_500_000,
            "tasa": 1.8,
            "total_cuotas": 12,
            "cuota_proxima": 1,
            "valor_cuota": 180_000,
            "proximo_pago": "2026-01-01",
        },
    )

    analisis = client.post(
        "/analisis", params={"usuario_id": usuario_id}, json={"compras_no_esenciales": 0}
    ).json()

    assert analisis["ingresos_totales"] == 5_000_000
    assert analisis["deuda_total"] == 1_500_000
    assert analisis["saldo_disponible"] == 5_000_000 - 2_500_000


def test_listar_tipos_deuda(client):
    respuesta = client.get("/tipos-deuda")
    assert respuesta.status_code == 200
    codigos = {t["codigo"] for t in respuesta.json()}
    assert codigos == {
        "HIPOTECARIO",
        "TARJETA",
        "VEHICULO",
        "EDUCATIVO",
        "LIBRE_INVERSION",
        "PRESTAMO_PERSONAL",
        "CONSUMO",
    }
