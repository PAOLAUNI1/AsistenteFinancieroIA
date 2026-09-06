import streamlit as st
from datetime import date
from utils import campo_moneda_decimal, limpiar_moneda_decimal


def render_formulario(suffix="_hipo"):
    """
    Renderiza el formulario para registrar un Crédito Hipotecario.
    """
    st.markdown("##### 🏠 Datos del Crédito Hipotecario")

    entidad = st.text_input(
        "Entidad financiera / Banco",
        key=f"entidad{suffix}"
    )

    col1, col2 = st.columns(2)
    with col1:
        monto_inicial = campo_moneda_decimal(
            "Monto inicial del crédito",
            f"monto_inicial{suffix}"
        )
    with col2:
        saldo_actual = campo_moneda_decimal(
            "Saldo actual de la deuda",
            f"saldo_actual{suffix}"
        )

    col3, col4, col5 = st.columns([1.2, 1.2, 1])
    with col3:
        tasa = st.number_input(
            "Tasa de interés (%)",
            min_value=0.0,
            max_value=100.0,
            step=0.01,
            key=f"tasa{suffix}"
        )
    with col4:
        periodicidad = st.selectbox(
            "Periodicidad",
            ["Efectiva anual (EA)", "Mensual"],
            key=f"periodicidad{suffix}"
        )
    with col5:
        tipo_tasa = st.selectbox(
            "Tipo de tasa",
            ["Fija", "Variable"],
            key=f"tipo_tasa{suffix}"
        )

    st.markdown("###### Plazo y Cuotas")
    col_p1, col_p2, col_p3 = st.columns([1, 1, 1.5])
    with col_p1:
        anos = st.number_input(
            "Años",
            min_value=0,
            step=1,
            key=f"anos{suffix}"
        )
    with col_p2:
        meses = st.number_input(
            "Meses",
            min_value=0,
            max_value=11,
            step=1,
            key=f"meses{suffix}"
        )
    with col_p3:
        valor_cuota = campo_moneda_decimal(
            "Valor de la cuota mensual",
            f"valor_cuota{suffix}"
        )

    col_q1, col_q2 = st.columns(2)
    with col_q1:
        cuota_proxima = st.number_input(
            "Número de próxima cuota a pagar",
            min_value=1,
            step=1,
            key=f"cuota_proxima{suffix}"
        )
    with col_q2:
        fecha_proximo_pago = st.date_input(
            "Fecha del próximo pago",
            value=date.today(),
            key=f"fecha_proximo_pago{suffix}"
        )

    # Cálculos derivados
    monto_inicial_num = limpiar_moneda_decimal(monto_inicial)
    saldo_actual_num = limpiar_moneda_decimal(saldo_actual)
    valor_cuota_num = limpiar_moneda_decimal(valor_cuota)
    total_cuotas = (anos * 12) + meses
    cuotas_pendientes = max(total_cuotas - cuota_proxima + 1, 0)

    # Resumen métrico
    if total_cuotas > 0:
        c_res1, c_res2 = st.columns(2)
        with c_res1:
            st.caption(f"Total de cuotas del crédito: **{total_cuotas}**")
        with c_res2:
            st.caption(f"Cuotas pendientes por pagar: **{cuotas_pendientes}**")

    # Botón de registro
    if st.button("➕ Registrar crédito hipotecario", key=f"btn_reg{suffix}"):
        if not entidad.strip():
            st.error("Ingresa la entidad financiera.")
        elif monto_inicial_num <= 0:
            st.error("El monto inicial debe ser mayor que cero.")
        elif saldo_actual_num <= 0:
            st.error("El saldo actual debe ser mayor que cero.")
        elif saldo_actual_num > monto_inicial_num:
            st.error("El saldo actual no puede ser mayor al monto inicial.")
        elif tasa <= 0:
            st.error("Ingresa una tasa de interés válida.")
        elif total_cuotas <= 0:
            st.error("El plazo del crédito debe ser mayor a 0 meses.")
        elif cuota_proxima > total_cuotas:
            st.error("La próxima cuota no puede superar el total de cuotas.")
        elif valor_cuota_num <= 0:
            st.error("El valor de la cuota mensual debe ser mayor que cero.")
        else:
            nueva_deuda = {
                "tipo": "Crédito hipotecario",
                "icono": "🏠",
                "entidad": entidad.strip(),
                "monto_inicial": monto_inicial_num,
                "saldo_actual": saldo_actual_num,
                "tasa": tasa,
                "periodicidad_tasa": periodicidad,
                "tipo_tasa": tipo_tasa,
                "anos": anos,
                "meses": meses,
                "total_cuotas": total_cuotas,
                "cuota_proxima": cuota_proxima,
                "cuotas_pendientes": cuotas_pendientes,
                "valor_cuota": valor_cuota_num,
                "proximo_pago": str(fecha_proximo_pago)
            }
            st.session_state.deudas.append(nueva_deuda)
            st.success(f"¡Crédito hipotecario con {entidad} registrado exitosamente!")
            st.rerun()
