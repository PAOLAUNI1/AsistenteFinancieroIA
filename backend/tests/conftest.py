import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.database import Base, get_db
from backend.main import app
from backend.models import CategoriaGasto, TipoDeuda

# Mismo catálogo ya sembrado en la base real `asistente_financiero` (tablas
# tipos_deuda y categorias_gasto): se replica aquí porque Base.metadata.create_all
# solo crea el esquema, no los datos de catálogo.
TIPOS_DEUDA_SEED = [
    ("HIPOTECARIO", "Crédito hipotecario", "🏠"),
    ("TARJETA", "Tarjeta de crédito", "💳"),
    ("VEHICULO", "Crédito de vehículo", "🚗"),
    ("EDUCATIVO", "Crédito educativo", "🎓"),
    ("LIBRE_INVERSION", "Préstamo de libre inversión", "💰"),
    ("PRESTAMO_PERSONAL", "Préstamo personal", "🤝"),
    ("CONSUMO", "Crédito de consumo", "🛒"),
]

CATEGORIAS_GASTO_SEED = [
    ("ALIMENTACION", "Alimentación", "HOGAR"),
    ("TRANSPORTE", "Transporte", "PERSONAL"),
    ("VESTIMENTA", "Vestimenta", "PERSONAL"),
    ("ENTRETENIMIENTO", "Entretenimiento", "PERSONAL"),
    ("ARRIENDO", "Arriendo o hipoteca", "HOGAR"),
    ("SERVICIOS", "Servicios públicos", "HOGAR"),
    ("COLEGIO", "Pago de colegio", "FAMILIA_EDUCACION"),
    ("UNIVERSIDAD", "Pago de universidad", "FAMILIA_EDUCACION"),
]


@pytest.fixture()
def client():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    with TestingSessionLocal() as db:
        db.add_all(TipoDeuda(codigo=c, nombre=n, icono=i) for c, n, i in TIPOS_DEUDA_SEED)
        db.add_all(CategoriaGasto(codigo=c, nombre=n, grupo=g) for c, n, g in CATEGORIAS_GASTO_SEED)
        db.commit()

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture()
def usuario_id(client):
    respuesta = client.post(
        "/usuarios",
        json={
            "nombre": "Usuario de prueba",
            "correo": "prueba@example.com",
            "acepta_terminos": True,
            "acepta_tratamiento_datos": True,
        },
    )
    return respuesta.json()["id"]
