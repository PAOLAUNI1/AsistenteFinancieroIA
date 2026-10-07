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


def test_deudas_requiere_token(client):
    respuesta = client.get("/deudas")
    assert respuesta.status_code == 401  # sin sesión no hay datos


def test_deudas_con_token_de_usuario_inexistente_devuelve_401(client):
    respuesta = client.get("/deudas", params={"usuario_id": 999})
    assert respuesta.status_code == 401


ACEPTACIONES = {
    "contrasena": "Segura1234",
    "acepta_terminos": True,
    "acepta_tratamiento_datos": True,
}


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


def _tarjeta(**extra):
    return {
        "entidad": "Bancolombia",
        "franquicia": "Visa",
        "ultimos_digitos": "1234",
        "cupo_total": 800000,
        "saldo_actual": 600000,
        "tasa": 2.5,
        "pago_minimo": 50000,
        "cuota_manejo": 10000,
        "dia_corte": 15,
        "dia_pago": 5,
        "proximo_pago": "2026-10-05",
        **extra,
    }


def test_tarjeta_guarda_nombre_y_detalle_completo(client, usuario_id):
    respuesta = client.post(
        "/deudas/tarjeta",
        params={"usuario_id": usuario_id},
        json=_tarjeta(nombre="  Visa personal  "),
    )
    assert respuesta.status_code == 201
    cuerpo = respuesta.json()
    assert cuerpo["nombre"] == "Visa personal"
    assert cuerpo["estado"] == "ACTIVA"
    assert cuerpo["saldo_actual"] == 600000
    assert cuerpo["valor_cuota"] == 60000  # pago mínimo + cuota de manejo
    assert cuerpo["detalle"]["cupo_total"] == 800000
    assert cuerpo["detalle"]["franquicia"] == "Visa"
    assert cuerpo["detalle"]["ultimos_digitos"] == "1234"


def test_tarjeta_sin_nombre_sigue_funcionando(client, usuario_id):
    respuesta = client.post(
        "/deudas/tarjeta", params={"usuario_id": usuario_id}, json=_tarjeta()
    )
    assert respuesta.status_code == 201
    assert respuesta.json()["nombre"] is None


def test_tarjeta_inactiva_queda_cancelada_y_no_cuenta_en_el_analisis(client, usuario_id):
    respuesta = client.post(
        "/deudas/tarjeta", params={"usuario_id": usuario_id}, json=_tarjeta(activa=False)
    )
    assert respuesta.status_code == 201
    assert respuesta.json()["estado"] == "CANCELADA"


def test_tarjeta_con_saldo_mayor_al_cupo_se_rechaza(client, usuario_id):
    respuesta = client.post(
        "/deudas/tarjeta",
        params={"usuario_id": usuario_id},
        json=_tarjeta(saldo_actual=900000),
    )
    assert respuesta.status_code == 422


def test_tarjeta_sin_intereses_es_valida(client, usuario_id):
    respuesta = client.post(
        "/deudas/tarjeta", params={"usuario_id": usuario_id}, json=_tarjeta(tasa=0)
    )
    assert respuesta.status_code == 201
    assert respuesta.json()["tiene_intereses"] is False


def test_tarjeta_con_los_datos_minimos_de_la_app(client, usuario_id):
    # Lo único que pide la app móvil: sin franquicia, pago mínimo ni fecha de próximo pago.
    payload = {
        "entidad": "Davivienda",
        "nombre": "Tarjeta de crédito Davivienda",
        "cupo_total": 5_000_000,
        "saldo_actual": 2_500_000,
        "tasa": 2.2,
        "periodicidad_tasa": "MENSUAL",
        "dia_corte": 25,
        "dia_pago": 10,
        "descripcion": "Tarjeta principal para gastos del hogar y compras varias.",
        "activa": True,
    }
    respuesta = client.post(
        "/deudas/tarjeta", params={"usuario_id": usuario_id}, json=payload
    )

    assert respuesta.status_code == 201
    cuerpo = respuesta.json()
    assert cuerpo["nombre"] == "Tarjeta de crédito Davivienda"
    assert cuerpo["descripcion"].startswith("Tarjeta principal")
    assert cuerpo["valor_cuota"] is None  # sin pago mínimo no hay cuota que mostrar
    assert cuerpo["detalle"]["franquicia"] is None
    assert cuerpo["detalle"]["dia_corte"] == 25
    assert cuerpo["fecha_proximo_pago"] is not None
    assert cuerpo["fecha_proximo_pago"].endswith("-10")  # cae el día de pago


def test_tarjeta_descripcion_demasiado_larga_se_rechaza(client, usuario_id):
    respuesta = client.post(
        "/deudas/tarjeta",
        params={"usuario_id": usuario_id},
        json=_tarjeta(descripcion="x" * 201),
    )
    assert respuesta.status_code == 422


def _vehiculo(**extra):
    return {
        "entidad": "Bancolombia",
        "nombre": "Crédito vehículo",
        "monto_inicial": 45_000_000,
        "saldo_actual": 32_500_000,
        "tasa": 14.5,
        "anos": 5,
        "meses": 0,
        "valor_cuota": 950_000,
        "cuota_proxima": 16,
        "proximo_pago": "2026-10-10",
        "fecha_inicio": "2024-01-10",
        "descripcion": "Crédito para vehículo Mazda CX-5, modelo 2024.",
        **extra,
    }


def test_vehiculo_guarda_los_datos_del_diseno_de_la_app(client, usuario_id):
    respuesta = client.post(
        "/deudas/vehiculo", params={"usuario_id": usuario_id}, json=_vehiculo()
    )

    assert respuesta.status_code == 201
    cuerpo = respuesta.json()
    assert cuerpo["nombre"] == "Crédito vehículo"
    assert cuerpo["saldo_actual"] == 32_500_000
    assert cuerpo["plazo_meses"] == 60
    assert cuerpo["cuotas_pendientes"] == 45
    assert cuerpo["fecha_inicio"] == "2024-01-10"
    assert cuerpo["descripcion"].startswith("Crédito para vehículo")
    assert cuerpo["estado"] == "ACTIVA"
    assert cuerpo["detalle"]["tipo_vehiculo"] == "OTRO"  # la app no pregunta el tipo


def test_vehiculo_inactivo_queda_cancelado(client, usuario_id):
    respuesta = client.post(
        "/deudas/vehiculo", params={"usuario_id": usuario_id}, json=_vehiculo(activa=False)
    )
    assert respuesta.status_code == 201
    assert respuesta.json()["estado"] == "CANCELADA"


def test_vehiculo_con_saldo_mayor_al_monto_se_rechaza(client, usuario_id):
    respuesta = client.post(
        "/deudas/vehiculo",
        params={"usuario_id": usuario_id},
        json=_vehiculo(saldo_actual=46_000_000),
    )
    assert respuesta.status_code == 422


def test_vehiculo_con_cuota_proxima_fuera_del_plazo_se_rechaza(client, usuario_id):
    respuesta = client.post(
        "/deudas/vehiculo", params={"usuario_id": usuario_id}, json=_vehiculo(cuota_proxima=61)
    )
    assert respuesta.status_code == 422


def test_vehiculo_con_inicio_posterior_al_proximo_pago_se_rechaza(client, usuario_id):
    respuesta = client.post(
        "/deudas/vehiculo",
        params={"usuario_id": usuario_id},
        json=_vehiculo(fecha_inicio="2026-12-01"),
    )
    assert respuesta.status_code == 422


def _educativo(**extra):
    return {
        "entidad": "CUN",
        "nombre": "Matrícula Universidad CUN",
        "carrera": "Ingeniería de Sistemas",
        "monto_inicial": 2_752_145,
        "saldo_actual": 2_752_145,
        "tasa": 0,
        "plazo_meses": 5,
        "cuota_proxima": 1,
        "valor_cuota": 550_429,
        "fecha_inicio": "2025-09-30",
        "proximo_pago": "2025-10-30",
        "descripcion": "Matrícula semestre 2025 - CUN.",
        **extra,
    }


def test_educativo_guarda_los_datos_del_diseno_de_la_app(client, usuario_id):
    respuesta = client.post(
        "/deudas/educativo", params={"usuario_id": usuario_id}, json=_educativo()
    )

    assert respuesta.status_code == 201
    cuerpo = respuesta.json()
    assert cuerpo["nombre"] == "Matrícula Universidad CUN"
    assert cuerpo["plazo_meses"] == 5
    assert cuerpo["cuotas_pendientes"] == 5
    assert cuerpo["tiene_intereses"] is False
    assert cuerpo["fecha_inicio"] == "2025-09-30"
    assert cuerpo["detalle"]["programa"] == "Ingeniería de Sistemas"
    assert cuerpo["detalle"]["institucion"] == "CUN"


def test_educativo_con_cuotas_ya_pagadas(client, usuario_id):
    respuesta = client.post(
        "/deudas/educativo",
        params={"usuario_id": usuario_id},
        json=_educativo(cuota_proxima=3),
    )
    assert respuesta.status_code == 201
    assert respuesta.json()["cuotas_pendientes"] == 3  # 5 - 3 + 1


def test_educativo_con_el_contrato_anterior_sigue_funcionando(client, usuario_id):
    respuesta = client.post(
        "/deudas/educativo",
        params={"usuario_id": usuario_id},
        json={
            "entidad": "ICETEX",
            "cuotas_pendientes": 24,
            "saldo_actual": 4_800_000,
            "tasa": 5,
            "valor_cuota": 250_000,
            "proximo_pago": "2026-10-30",
        },
    )
    assert respuesta.status_code == 201
    cuerpo = respuesta.json()
    assert cuerpo["plazo_meses"] == 24
    assert cuerpo["cuotas_pendientes"] == 24


def test_educativo_inactivo_queda_cancelado(client, usuario_id):
    respuesta = client.post(
        "/deudas/educativo", params={"usuario_id": usuario_id}, json=_educativo(activa=False)
    )
    assert respuesta.status_code == 201
    assert respuesta.json()["estado"] == "CANCELADA"


def test_educativo_con_cuota_proxima_fuera_del_plazo_se_rechaza(client, usuario_id):
    respuesta = client.post(
        "/deudas/educativo", params={"usuario_id": usuario_id}, json=_educativo(cuota_proxima=6)
    )
    assert respuesta.status_code == 422


def test_educativo_con_saldo_mayor_al_monto_se_rechaza(client, usuario_id):
    respuesta = client.post(
        "/deudas/educativo",
        params={"usuario_id": usuario_id},
        json=_educativo(saldo_actual=3_000_000),
    )
    assert respuesta.status_code == 422


def test_educativo_con_inicio_posterior_al_proximo_pago_se_rechaza(client, usuario_id):
    respuesta = client.post(
        "/deudas/educativo",
        params={"usuario_id": usuario_id},
        json=_educativo(fecha_inicio="2026-01-01"),
    )
    assert respuesta.status_code == 422


def _otros(**extra):
    return {
        "entidad": "Juan Pérez",
        "tipo_credito": "PRESTAMO_FAMILIAR",
        "nombre": "Anillo de matrimonio",
        "monto_inicial": 700_000,
        "saldo_actual": 700_000,
        "tasa": 0,
        "plazo_meses": 8,
        "cuota_proxima": 1,
        "valor_cuota": 87_500,
        "fecha_inicio": "2025-10-01",
        "proximo_pago": "2025-11-01",
        "descripcion": "Préstamo familiar para compra de anillo de matrimonio.",
        **extra,
    }


def test_otros_guarda_los_datos_del_diseno_de_la_app(client, usuario_id):
    respuesta = client.post(
        "/deudas/otros", params={"usuario_id": usuario_id}, json=_otros()
    )

    assert respuesta.status_code == 201
    cuerpo = respuesta.json()
    assert cuerpo["tipo_codigo"] == "OTRO"
    assert cuerpo["nombre"] == "Anillo de matrimonio"
    assert cuerpo["entidad"] == "Juan Pérez"
    assert cuerpo["plazo_meses"] == 8
    assert cuerpo["cuotas_pendientes"] == 8
    assert cuerpo["tiene_intereses"] is False
    assert cuerpo["detalle"]["tipo_credito"] == "PRESTAMO_FAMILIAR"


def test_otros_con_tipo_de_credito_desconocido_se_rechaza(client, usuario_id):
    respuesta = client.post(
        "/deudas/otros",
        params={"usuario_id": usuario_id},
        json=_otros(tipo_credito="INVENTADO"),
    )
    assert respuesta.status_code == 422


def test_otros_inactivo_queda_cancelado(client, usuario_id):
    respuesta = client.post(
        "/deudas/otros", params={"usuario_id": usuario_id}, json=_otros(activa=False)
    )
    assert respuesta.status_code == 201
    assert respuesta.json()["estado"] == "CANCELADA"


def test_otros_con_cuota_proxima_fuera_del_plazo_se_rechaza(client, usuario_id):
    respuesta = client.post(
        "/deudas/otros", params={"usuario_id": usuario_id}, json=_otros(cuota_proxima=9)
    )
    assert respuesta.status_code == 422


def test_otros_con_saldo_mayor_al_monto_se_rechaza(client, usuario_id):
    respuesta = client.post(
        "/deudas/otros", params={"usuario_id": usuario_id}, json=_otros(saldo_actual=800_000)
    )
    assert respuesta.status_code == 422


def test_otros_se_puede_eliminar_con_su_detalle(client, usuario_id):
    creada = client.post(
        "/deudas/otros", params={"usuario_id": usuario_id}, json=_otros()
    ).json()

    eliminar = client.delete(f"/deudas/{creada['id']}", params={"usuario_id": usuario_id})

    assert eliminar.status_code == 204
    assert client.get("/deudas", params={"usuario_id": usuario_id}).json() == []


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
        "OTRO",
    }


def _payload_hipotecario(**extra):
    return {
        "entidad": "Banco XYZ",
        "monto_inicial": 94_000_000,
        "saldo_actual": 89_800_000,
        "tasa": 11,
        "periodicidad_tasa": "EA",
        "tipo_tasa": "FIJA",
        "anos": 20,
        "meses": 0,
        "valor_cuota": 994_115,
        "cuota_proxima": 23,
        "proximo_pago": "2026-10-15",
        **extra,
    }


def test_hipotecario_guarda_nombre_fecha_inicio_y_descripcion(client, usuario_id):
    respuesta = client.post(
        "/deudas/hipotecario",
        params={"usuario_id": usuario_id},
        json=_payload_hipotecario(
            nombre="Crédito hipotecario vivienda",
            fecha_inicio="2025-01-15",
            descripcion="Apartamento en Bogotá",
        ),
    )

    assert respuesta.status_code == 201
    cuerpo = respuesta.json()
    assert cuerpo["nombre"] == "Crédito hipotecario vivienda"
    assert cuerpo["fecha_inicio"] == "2025-01-15"
    assert cuerpo["descripcion"] == "Apartamento en Bogotá"
    assert cuerpo["estado"] == "ACTIVA"
    assert cuerpo["cuotas_pendientes"] == 218  # 240 - 22 pagadas

    listado = client.get("/deudas", params={"usuario_id": usuario_id}).json()
    assert listado[0]["nombre"] == "Crédito hipotecario vivienda"


def test_hipotecario_sin_los_campos_nuevos_sigue_funcionando(client, usuario_id):
    respuesta = client.post(
        "/deudas/hipotecario", params={"usuario_id": usuario_id}, json=_payload_hipotecario()
    )

    assert respuesta.status_code == 201
    assert respuesta.json()["nombre"] is None
    assert respuesta.json()["fecha_inicio"] is None


def test_hipotecario_inactiva_queda_cancelada_y_no_cuenta_en_el_analisis(client, usuario_id):
    client.post(
        "/deudas/hipotecario",
        params={"usuario_id": usuario_id},
        json=_payload_hipotecario(activa=False),
    )
    activa = client.post(
        "/deudas/hipotecario",
        params={"usuario_id": usuario_id},
        json=_payload_hipotecario(saldo_actual=1_000_000),
    ).json()

    assert activa["estado"] == "ACTIVA"
    estados = {d["estado"] for d in client.get("/deudas", params={"usuario_id": usuario_id}).json()}
    assert estados == {"ACTIVA", "CANCELADA"}

    analisis = client.post(
        "/analisis", params={"usuario_id": usuario_id}, json={"compras_no_esenciales": 0}
    ).json()
    assert analisis["deuda_total"] == 1_000_000  # solo la activa


def test_hipotecario_con_fecha_de_inicio_posterior_al_proximo_pago_devuelve_422(client, usuario_id):
    respuesta = client.post(
        "/deudas/hipotecario",
        params={"usuario_id": usuario_id},
        json=_payload_hipotecario(fecha_inicio="2027-01-01"),
    )
    assert respuesta.status_code == 422


def test_hipotecario_con_descripcion_de_mas_de_200_caracteres_devuelve_422(client, usuario_id):
    respuesta = client.post(
        "/deudas/hipotecario",
        params={"usuario_id": usuario_id},
        json=_payload_hipotecario(descripcion="x" * 201),
    )
    assert respuesta.status_code == 422
