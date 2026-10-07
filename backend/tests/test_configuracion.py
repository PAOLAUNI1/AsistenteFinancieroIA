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
