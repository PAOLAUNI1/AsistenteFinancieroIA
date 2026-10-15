from backend.services.limite_intentos import LimiteIntentos


def test_consultar_correos_distintos_no_deja_claves_guardadas():
    limite = LimiteIntentos()

    for i in range(1000):
        assert limite.segundos_de_espera(f"nadie{i}@example.com", f"10.0.{i % 250}.1") == 0

    assert limite.claves_guardadas() == 0


def test_los_fallos_vencidos_se_olvidan_y_liberan_la_clave(monkeypatch):
    reloj = [1000.0]
    monkeypatch.setattr("backend.services.limite_intentos.time.monotonic", lambda: reloj[0])
    limite = LimiteIntentos(max_por_correo=2, max_por_ip=10, ventana=60)
    limite.registrar_fallo("a@example.com", "1.1.1.1")
    limite.registrar_fallo("a@example.com", "1.1.1.1")
    assert limite.segundos_de_espera("a@example.com", "1.1.1.1") > 0

    reloj[0] += 61

    assert limite.segundos_de_espera("a@example.com", "1.1.1.1") == 0
    assert limite.claves_guardadas() == 0


def test_bloquea_al_llegar_al_maximo_por_correo_y_el_exito_lo_libera():
    limite = LimiteIntentos(max_por_correo=3, max_por_ip=100)
    for _ in range(3):
        limite.registrar_fallo("A@Example.com", "1.1.1.1")

    assert limite.segundos_de_espera("a@example.com", "2.2.2.2") > 0

    limite.registrar_exito("a@example.com")

    assert limite.segundos_de_espera("a@example.com", "2.2.2.2") == 0


def test_bloquea_por_ip_aunque_cambie_el_correo():
    limite = LimiteIntentos(max_por_correo=100, max_por_ip=3)
    for i in range(3):
        limite.registrar_fallo(f"u{i}@example.com", "9.9.9.9")

    assert limite.segundos_de_espera("otro@example.com", "9.9.9.9") > 0
    assert limite.segundos_de_espera("otro@example.com", "8.8.8.8") == 0


def test_con_demasiadas_claves_se_barren_las_vencidas(monkeypatch):
    reloj = [1000.0]
    monkeypatch.setattr("backend.services.limite_intentos.time.monotonic", lambda: reloj[0])
    limite = LimiteIntentos(max_por_correo=5, max_por_ip=50, ventana=60, max_claves=10)
    # Un atacante rota correos e IP: cada uno falla una sola vez y no vuelve a aparecer.
    for i in range(20):
        limite.registrar_fallo(f"x{i}@example.com", f"10.0.0.{i}")
    assert limite.claves_guardadas() > 10

    reloj[0] += 61
    limite.registrar_fallo("nuevo@example.com", "10.9.9.9")

    assert limite.claves_guardadas() == 2  # solo lo recién registrado: correo y IP


def test_el_barrido_no_borra_los_fallos_vigentes(monkeypatch):
    reloj = [1000.0]
    monkeypatch.setattr("backend.services.limite_intentos.time.monotonic", lambda: reloj[0])
    limite = LimiteIntentos(max_por_correo=2, max_por_ip=50, ventana=60, max_claves=4)
    limite.registrar_fallo("a@example.com", "1.1.1.1")
    limite.registrar_fallo("a@example.com", "1.1.1.1")
    for i in range(6):
        limite.registrar_fallo(f"b{i}@example.com", f"2.2.2.{i}")  # fuerzan barridos, aún vigentes

    assert limite.segundos_de_espera("a@example.com", "9.9.9.9") > 0
