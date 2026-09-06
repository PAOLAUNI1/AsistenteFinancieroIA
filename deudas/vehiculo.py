import streamlit as st
from datetime import date
from utils import campo_moneda_decimal, limpiar_moneda_decimal


def render_formulario(suffix="_vehiculo"):
    """
    Renderiza el formulario para registrar un Crédito de Vehículo.
    """
    st.markdown("##### 🚗 Datos del Crédito de Vehículo")

    col_v1, col_v2 = st.columns(2)
    with col_v1:
        entidad = st.text_input(
            "Entidad financiera / Concesionario",
            placeholder="Ej. Sufi Bancolombia, Banco de Bogotá",
            key=f"entidad{suffix}"
        )
    with col_v2:
        pass

    col1, col2 = st.columns(2)
    with col1:
        monto_inicial = campo_moneda_decimal(
            "Monto financiado / Valor inicial",
            f"monto_inicial{suffix}"
        )
    with col2:
        saldo_actual = campo_moneda_decimal(
            "Saldo actual de la deuda",
            f"saldo_actual{suffix}"
        )

    col3, col4 = st.columns(2)
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
            "Periodicidad de la tasa",
            ["Efectiva anual (EA)", "Mensual"],
            key=f"periodicidad{suffix}"
        )

    st.markdown("###### Plazo y Cuotas")
    col_p1, col_p2, col_p3 = st.columns([1, 1, 1.5])
    with col_p1:
        anos = st.number_input(
            "Años de plazo",
            min_value=0,
            step=1,
            key=f"anos{suffix}"
        )
    with col_p2:
        meses = st.number_input(
            "Meses adicionales",
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
            "Próxima cuota a pagar",
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

    # Cálculos
    monto_inicial_num = limpiar_moneda_decimal(monto_inicial)
    saldo_actual_num = limpiar_moneda_decimal(saldo_actual)
    valor_cuota_num = limpiar_moneda_decimal(valor_cuota)
    total_cuotas = (anos * 12) + meses
    cuotas_pendientes = max(total_cuotas - cuota_proxima + 1, 0)

    if total_cuotas > 0:
        c1, c2 = st.columns(2)
        with c1:
            st.caption(f"Total de cuotas: **{total_cuotas}**")
        with c2:
            st.caption(f"Cuotas pendientes: **{cuotas_pendientes}**")

    # Registro
    if st.button("➕ Registrar crédito de vehículo", key=f"btn_reg{suffix}"):
        if not entidad.strip():
            st.error("Ingresa la entidad financiera.")
        elif monto_inicial_num <= 0:
            st.error("El monto financiado debe ser mayor a cero.")
        elif saldo_actual_num <= 0:
            st.error("El saldo actual debe ser mayor a cero.")
        elif saldo_actual_num > monto_inicial_num:
            st.error("El saldo actual no puede ser mayor al monto financiado.")
        elif total_cuotas <= 0:
            st.error("El plazo del crédito debe ser mayor a 0 meses.")
        elif valor_cuota_num <= 0:
            st.error("El valor de la cuota debe ser mayor a cero.")
        else:
            descripcion = f"{entidad.strip()}"

            nueva_deuda = {
                "tipo": "Crédito de vehículo",
                "icono": "🚗",
                "entidad": descripcion,
                "monto_inicial": monto_inicial_num,
                "saldo_actual": saldo_actual_num,
                "tasa": tasa,
                "periodicidad_tasa": periodicidad,
                "tipo_tasa": "Fija",
                "anos": anos,
                "meses": meses,
                "total_cuotas": total_cuotas,
                "cuota_proxima": cuota_proxima,
                "cuotas_pendientes": cuotas_pendientes,
                "valor_cuota": valor_cuota_num,
                "proximo_pago": str(fecha_proximo_pago)
            }
            st.session_state.deudas.append(nueva_deuda)
            st.success(f"¡Crédito de vehículo ({descripcion}) registrado con éxito!")
            st.rerun()
