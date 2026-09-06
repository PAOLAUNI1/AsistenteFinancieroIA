"""
Módulo de gestión y registro de deudas.
Proporciona los formularios especializados y metadatos para cada tipo de crédito.
"""

from .hipotecario import render_formulario as render_hipotecario
from .tarjeta import render_formulario as render_tarjeta
from .vehiculo import render_formulario as render_vehiculo
from .educativo import render_formulario as render_educativo
from .libre_inversion import render_formulario as render_libre_inversion
from .prestamo_personal import render_formulario as render_prestamo_personal
from .consumo import render_formulario as render_consumo

TIPOS_DEUDAS = {
    "Crédito hipotecario": {
        "icono": "🏠",
        "descripcion": "Vivienda nueva, usada o sobre planos.",
        "render": render_hipotecario
    },
    "Tarjeta de crédito": {
        "icono": "💳",
        "descripcion": "Tarjetas bancarias o departamentales.",
        "render": render_tarjeta
    },
    "Crédito de vehículo": {
        "icono": "🚗",
        "descripcion": "Carro, moto o vehículo comercial.",
        "render": render_vehiculo
    },
    "Crédito educativo": {
        "icono": "🎓",
        "descripcion": "ICETEX, pregrado, posgrado o diplomados.",
        "render": render_educativo
    },
    "Préstamo de libre inversión": {
        "icono": "💰",
        "descripcion": "Préstamos bancarios de libre destinación.",
        "render": render_libre_inversion
    },
    "Préstamo personal": {
        "icono": "🤝",
        "descripcion": "Deudas con familiares, amigos o particulares.",
        "render": render_prestamo_personal
    },
    "Crédito de consumo": {
        "icono": "🛒",
        "descripcion": "Financiación de electrodomésticos, tecnología o compras.",
        "render": render_consumo
    }
}


def render_formulario_deuda(tipo_deuda, suffix=""):
    """
    Despacha y renderiza el formulario correspondiente al tipo de crédito.
    """
    if tipo_deuda in TIPOS_DEUDAS:
        TIPOS_DEUDAS[tipo_deuda]["render"](suffix=suffix)