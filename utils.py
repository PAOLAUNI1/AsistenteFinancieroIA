import streamlit as st
import re


# ======================================
# FORMATO MONEDA ENTERA
# ======================================

def campo_moneda(label, key):
    """
    Input de texto para Streamlit con formato de moneda en pesos (sin decimales).
    Ejemplo visual: $1.500.000
    """
    def actualizar():
        valor = str(st.session_state[key]).strip()
        valor = valor.replace("$", "").replace(" ", "")
        numeros = re.sub(r"[^0-9]", "", valor)

        if numeros != "":
            numero = int(numeros)
            st.session_state[key] = f"${numero:,}".replace(",", ".")
        else:
            st.session_state[key] = ""

    if key not in st.session_state:
        st.session_state[key] = ""

    return st.text_input(
        label,
        key=key,
        on_change=actualizar
    )


# ======================================
# FORMATO MONEDA CON DECIMALES
# ======================================

def campo_moneda_decimal(label, key):
    """
    Input de texto para Streamlit con formato de moneda en pesos colombianos con decimales.
    Ejemplo visual: $96.145.520,00
    """
    def actualizar():
        valor = str(st.session_state[key]).strip()
        valor = valor.replace("$", "").replace(" ", "")

        if valor == "":
            st.session_state[key] = ""
            return

        try:
            if "," in valor:
                partes = valor.rsplit(",", 1)
                parte_entera = re.sub(r"[^0-9]", "", partes[0])
                parte_decimal = re.sub(r"[^0-9]", "", partes[1])[:2]

                if parte_entera == "":
                    parte_entera = "0"

                numero = float(f"{parte_entera}.{parte_decimal or '00'}")
            else:
                valor_limpio = re.sub(r"[^0-9.]", "", valor)
                numero = float(valor_limpio)

            entero = int(numero)
            decimales = int(round((numero - entero) * 100))

            if decimales == 100:
                entero += 1
                decimales = 0

            st.session_state[key] = (
                f"${entero:,}".replace(",", ".")
                + f",{decimales:02d}"
            )

        except ValueError:
            st.session_state[key] = valor

    if key not in st.session_state:
        st.session_state[key] = ""

    return st.text_input(
        label,
        key=key,
        on_change=actualizar
    )


# ======================================
# LIMPIAR MONEDA
# ======================================

def limpiar_moneda(valor):
    """Convierte un string formateado de moneda a entero."""
    valor = str(valor)
    valor = valor.replace("$", "").replace(".", "").strip()

    if valor == "":
        return 0

    try:
        return int(valor)
    except ValueError:
        return 0


# ======================================
# LIMPIAR MONEDA CON DECIMALES
# ======================================

def limpiar_moneda_decimal(valor):
    """Convierte un string formateado de moneda a float."""
    valor = str(valor)
    valor = valor.replace("$", "").replace(".", "").replace(",", ".").strip()

    if valor == "":
        return 0.0

    try:
        return float(valor)
    except ValueError:
        return 0.0


# ======================================
# MOSTRAR MONEDA
# ======================================

def mostrar_moneda(valor):
    """Formatea un valor numérico como string de moneda colombiana ($ 1.000.000,00)."""
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
