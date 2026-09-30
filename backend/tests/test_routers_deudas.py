def test_registrar_hipotecario_y_listar(client):
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

    respuesta = client.post("/deudas/hipotecario", json=payload)
    assert respuesta.status_code == 201
    cuerpo = respuesta.json()
    assert cuerpo["plazo_meses"] == 240
    assert cuerpo["cuotas_pendientes"] == 219
    assert cuerpo["tipo_codigo"] == "HIPOTECARIO"

    listado = client.get("/deudas")
    assert listado.status_code == 200
    assert len(listado.json()) == 1
    assert listado.json()[0]["entidad"] == "Bancolombia"


def test_registrar_hipotecario_invalido_devuelve_422(client):
    payload = {
        "entidad": "Banco X",
        "monto_inicial": 1_000_000.0,
        "saldo_actual": 2_000_000.0,
        "tasa": 10.0,
        "valor_cuota": 100_000.0,
        "cuota_proxima": 1,
        "proximo_pago": "2026-01-01",
    }

    respuesta = client.post("/deudas/hipotecario", json=payload)
    assert respuesta.status_code == 422


def test_tarjeta_guarda_detalle_y_no_tiene_plazo_fijo(client):
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
    respuesta = client.post("/deudas/tarjeta", json=payload)
    assert respuesta.status_code == 201
    cuerpo = respuesta.json()
    assert cuerpo["plazo_meses"] is None
    assert cuerpo["detalle"]["dia_corte"] == 15
    assert cuerpo["detalle"]["dia_pago"] == 5


def test_eliminar_deuda(client):
    payload = {
        "prestamista": "Juan Pérez",
        "tipo_relacion": "Amigo / Compañero",
        "saldo_actual": 200_000.0,
        "valor_cuota": 50_000.0,
        "proximo_pago": "2026-01-01",
    }
    creada = client.post("/deudas/prestamo_personal", json=payload).json()

    eliminar = client.delete(f"/deudas/{creada['id']}")
    assert eliminar.status_code == 204

    listado = client.get("/deudas").json()
    assert listado == []


def test_analisis_incluye_deuda_registrada(client):
    client.put(
        "/perfil",
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

    analisis = client.post("/analisis", json={"compras_no_esenciales": 0}).json()

    assert analisis["ingresos_totales"] == 5_000_000
    assert analisis["deuda_total"] == 1_500_000
    assert analisis["saldo_disponible"] == 5_000_000 - 2_500_000
