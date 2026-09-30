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


def test_perfil_usa_el_usuario_id_indicado_explicitamente(client):
    uno = client.post("/usuarios", json={"nombre": "Uno", "correo": "uno@example.com"}).json()
    dos = client.post("/usuarios", json={"nombre": "Dos", "correo": "dos@example.com"}).json()

    perfil_uno = client.get("/perfil", params={"usuario_id": uno["id"]}).json()
    perfil_dos = client.get("/perfil", params={"usuario_id": dos["id"]}).json()

    assert perfil_uno["usuario_id"] == uno["id"]
    assert perfil_dos["usuario_id"] == dos["id"]
