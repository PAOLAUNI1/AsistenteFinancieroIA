def test_registrar_usuario(client):
    respuesta = client.post(
        "/usuarios",
        json={"nombre": "Juan Camilo Garcia", "correo": "juancamilo@example.com", "cantidad_hijos": 1},
    )
    assert respuesta.status_code == 201
    cuerpo = respuesta.json()
    assert cuerpo["correo"] == "juancamilo@example.com"
    assert cuerpo["estado"] == "ACTIVO"


def test_registrar_usuario_con_correo_duplicado_devuelve_409(client):
    client.post("/usuarios", json={"nombre": "Uno", "correo": "repetido@example.com"})
    respuesta = client.post("/usuarios", json={"nombre": "Otro", "correo": "repetido@example.com"})
    assert respuesta.status_code == 409


def test_registrar_usuario_con_correo_invalido_devuelve_422(client):
    respuesta = client.post("/usuarios", json={"nombre": "Malo", "correo": "no-es-un-correo"})
    assert respuesta.status_code == 422


def test_usuario_recien_creado_pasa_a_ser_el_usuario_actual(client):
    client.post("/usuarios", json={"nombre": "Demo previo", "correo": "demo@example.com"})
    nuevo = client.post("/usuarios", json={"nombre": "Nuevo", "correo": "nuevo@example.com"}).json()

    perfil = client.get("/perfil").json()
    assert perfil["usuario_id"] == nuevo["id"]
