import streamlit as st
from datetime import date
from utils import campo_moneda_decimal, limpiar_moneda_decimal


def render_formulario(suffix="_tarjeta"):
    """
    Renderiza el formulario para registrar una Tarjeta de Crédito.
    """
    st.markdown("##### Datos de la Tarjeta de Crédito")

    col_e1, col_e2 = st.columns([1.5, 1])
    with col_e1:
        entidad = st.text_input(
            "Entidad emisora / Banco",
            placeholder="Ej. Bancolombia, Davivienda, Nu",
            key=f"entidad{suffix}"
        )
    with col_e2:
        franquicia = st.selectbox(
            "Franquicia",
            ["Visa", "Mastercard", "American Express", "Diners Club", "Otra"],
            key=f"franquicia{suffix}"
        )

    col1, col2 = st.columns(2)
    with col1:
        cupo_total = campo_moneda_decimal(
            "Cupo total aprobado",
            f"cupo_total{suffix}"
        )
    with col2:
        saldo_actual = campo_moneda_decimal(
            "Deuda actual / Saldo utilizado",
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
            ["Mensual vencido (MV)", "Efectiva anual (EA)"],
            key=f"periodicidad{suffix}"
        )

    col5, col6 = st.columns(2)
    with col5:
        pago_minimo = campo_moneda_decimal(
            "Pago mínimo del mes",
            f"pago_minimo{suffix}"
        )
    with col6:
        cuota_manejo = campo_moneda_decimal(
            "Cuota de manejo mensual (opcional)",
            f"cuota_manejo{suffix}"
        )

    col7, col8 = st.columns(2)
    with col7:
        dia_corte = st.number_input(
            "Día de corte del mes",
            min_value=1,
            max_value=31,
            value=15,
            step=1,
            key=f"dia_corte{suffix}"
        )
    with col8:
        fecha_proximo_pago = st.date_input(
            "Fecha límite de pago",
            value=date.today(),
            key=f"fecha_proximo_pago{suffix}"
        )

    # Conversión
    cupo_total_num = limpiar_moneda_decimal(cupo_total)
    saldo_actual_num = limpiar_moneda_decimal(saldo_actual)
    pago_minimo_num = limpiar_moneda_decimal(pago_minimo)
    cuota_manejo_num = limpiar_moneda_decimal(cuota_manejo)

    # Métricas informativas de tarjeta
    if cupo_total_num > 0:
        cupo_disponible = max(cupo_total_num - saldo_actual_num, 0.0)
        uso_porcentaje = (saldo_actual_num / cupo_total_num) * 100
        c1, c2 = st.columns(2)
        with c1:
            st.caption(f"Cupo disponible: **${cupo_disponible:,.2f}**".replace(",", "X").replace(".", ",").replace("X", "."))
        with c2:
            st.caption(f"Porcentaje de ocupación: **{uso_porcentaje:.1f}%**")

    # Registro
    if st.button("Registrar tarjeta de crédito", key=f"btn_reg{suffix}"):
        if not entidad.strip():
            st.error("Ingresa la entidad financiera emisora.")
        elif cupo_total_num <= 0:
            st.error("El cupo total aprobado debe ser mayor a cero.")
        elif saldo_actual_num <= 0:
            st.error("El saldo adeudado debe ser mayor a cero.")
        elif saldo_actual_num > cupo_total_num:
            st.error("El saldo utilizado no puede superar el cupo aprobado.")
        elif pago_minimo_num <= 0:
            st.error("El pago mínimo mensual debe ser mayor a cero.")
        else:
            cuota_total_mes = pago_minimo_num + cuota_manejo_num
            nombre_tarjeta = f"{entidad.strip()} ({franquicia})"
            nueva_deuda = {
                "tipo": "Tarjeta de crédito",
                "entidad": nombre_tarjeta,
                "monto_inicial": cupo_total_num,
                "saldo_actual": saldo_actual_num,
                "cupo_total": cupo_total_num,
                "tasa": tasa,
                "periodicidad_tasa": periodicidad,
                "tipo_tasa": "Variable",
                "anos": 0,
                "meses": 0,
                "total_cuotas": "Rotativo",
                "cuota_proxima": 1,
                "cuotas_pendientes": "Rotativo",
                "valor_cuota": cuota_total_mes,
                "pago_minimo": pago_minimo_num,
                "cuota_manejo": cuota_manejo_num,
                "dia_corte": dia_corte,
                "proximo_pago": str(fecha_proximo_pago)
            }
            st.session_state.deudas.append(nueva_deuda)
            st.success(f"¡Tarjeta de crédito {nombre_tarjeta} registrada exitosamente!")
            st.rerun()
