"""
Funciones de formato monetario (sección 11 de CLAUDE.md), migradas de
utils.py sin las partes de UI de Streamlit (campo_moneda/campo_moneda_decimal
no aplican a una API: son inputs de texto interactivos).
"""


def limpiar_moneda(valor) -> int:
    """Convierte un string formateado de moneda a entero."""
    valor = str(valor)
    valor = valor.replace("$", "").replace(".", "").strip()

    if valor == "":
        return 0

    try:
        return int(valor)
    except ValueError:
        return 0


def limpiar_moneda_decimal(valor) -> float:
    """Convierte un string formateado de moneda a float."""
    valor = str(valor)
    valor = valor.replace("$", "").replace(".", "").replace(",", ".").strip()

    if valor == "":
        return 0.0

    try:
        return float(valor)
    except ValueError:
        return 0.0


def mostrar_moneda(valor) -> str:
    """Formatea un valor numérico como string de moneda colombiana ($1.000.000,00)."""
    try:
        valor = float(valor)
    except (ValueError, TypeError):
        return "$0,00"

    return (
        f"${valor:,.2f}"
        .replace(",", "X")
        .replace(".", ",")
        .replace("X", ".")
    )
