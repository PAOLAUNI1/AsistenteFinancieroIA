"""La conexión a la base se arma con DATABASE_URL (nube) o con las variables DB_* (local)."""

from sqlalchemy.engine import make_url

from backend import database


def test_database_url_de_un_proveedor_usa_el_driver_pymysql(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "mysql://usuario:clave@host.ejemplo.com:3307/mibase")

    url = make_url(database._url_desde_entorno())

    assert url.drivername == "mysql+pymysql"
    assert (url.username, url.password) == ("usuario", "clave")
    assert (url.host, url.port, url.database) == ("host.ejemplo.com", 3307, "mibase")
    assert url.query["charset"] == "utf8mb4"


def test_database_url_con_parametros_conserva_los_suyos(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "mysql://u:p@h:3306/b?ssl=true")

    url = database._url_desde_entorno()

    assert "ssl=true" in url
    assert url.count("charset=utf8mb4") == 1


def test_sin_database_url_se_usan_las_variables_db(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.setattr(database, "DB_HOST", "127.0.0.1")
    monkeypatch.setattr(database, "DB_PORT", "3306")
    monkeypatch.setattr(database, "DB_NAME", "asistente")
    monkeypatch.setattr(database, "DB_USER", "root")
    monkeypatch.setattr(database, "DB_PASSWORD", "p@ss word:1")

    url = make_url(database._url_desde_entorno())

    assert url.password == "p@ss word:1"  # los caracteres especiales sobreviven al armado
    assert (url.host, url.database) == ("127.0.0.1", "asistente")


def test_en_produccion_sin_jwt_secret_no_arranca(monkeypatch):
    import pytest

    from backend.services import tokens

    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.delenv("JWT_SECRET", raising=False)
    with pytest.raises(RuntimeError):
        tokens._cargar_clave()

    monkeypatch.setenv("JWT_SECRET", "corta")
    with pytest.raises(RuntimeError):
        tokens._cargar_clave()

    monkeypatch.setenv("JWT_SECRET", "x" * 32)
    assert tokens._cargar_clave() == "x" * 32


def test_fuera_de_produccion_sin_jwt_secret_usa_clave_temporal(monkeypatch):
    from backend.services import tokens

    monkeypatch.delenv("APP_ENV", raising=False)
    monkeypatch.delenv("JWT_SECRET", raising=False)
    assert len(tokens._cargar_clave()) >= tokens.LARGO_MINIMO_CLAVE


def test_jwt_dias_con_basura_usa_30(monkeypatch):
    from backend.services import tokens

    monkeypatch.setenv("JWT_DIAS", "abc")
    assert tokens._dias_de_vida() == 30
