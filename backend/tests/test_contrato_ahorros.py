"""El registro de ahorros por categoría: un esquema y un validador por categoría, unidos por nombre."""

import inspect

import pytest

from backend.main import app
from backend.routers.ahorros import ESQUEMAS_POR_CATEGORIA
from backend.services.ahorros import VALIDADORES_POR_CATEGORIA

CATEGORIAS = list(ESQUEMAS_POR_CATEGORIA)


def test_cada_categoria_tiene_esquema_y_validador():
    assert ESQUEMAS_POR_CATEGORIA.keys() == VALIDADORES_POR_CATEGORIA.keys()
    assert len(CATEGORIAS) >= 2


@pytest.mark.parametrize("categoria", CATEGORIAS)
def test_los_campos_del_esquema_son_los_parametros_del_validador(categoria):
    # El router llama validar(**payload.model_dump()): si divergen, daría un 500 en vez de un 422.
    campos = set(ESQUEMAS_POR_CATEGORIA[categoria].model_fields)
    parametros = set(inspect.signature(VALIDADORES_POR_CATEGORIA[categoria]).parameters)

    assert campos == parametros


@pytest.mark.parametrize("categoria", CATEGORIAS)
def test_cada_categoria_expone_su_endpoint_de_registro(categoria):
    rutas = app.openapi()["paths"]

    assert f"/ahorros/{categoria}" in rutas
    assert "post" in rutas[f"/ahorros/{categoria}"]


def test_los_identificadores_de_operacion_de_openapi_son_unicos():
    operaciones = [
        operacion["operationId"]
        for ruta in app.openapi()["paths"].values()
        for operacion in ruta.values()
    ]

    assert len(operaciones) == len(set(operaciones))
