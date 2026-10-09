import streamlit as st
from datetime import date
from utils import campo_moneda_decimal, limpiar_moneda_decimal


def render_formulario(suffix="_educativo"):
    """
    Renderiza el formulario para registrar un Crédito Educativo.
    """
    st.markdown("##### Datos del Crédito Educativo")

    col_ed1, col_ed2 = st.columns(2)
    with col_ed1:
        entidad = st.text_input(
            "Entidad financiera / Institución",
            placeholder="Ej. ICETEX, Banco Pichincha, Cooperativa",
            key=f"entidad{suffix}"
        )
    with col_ed2:
        carrera = st.text_input(
            "Programa o Universidad (Opcional)",
            placeholder="Ej. Pregrado Ingeniería, Posgrado",
            key=f"carrera{suffix}"
        )

    col_est1, col_est2 = st.columns(2)
    with col_est1:
        estado_credito = st.selectbox(
            "Estado del crédito",
            ["En amortización (Pagando cuota completa)", "En periodo de gracia (Solo intereses)", "Época de estudios"],
            key=f"estado{suffix}"
        )
    with col_est2:
        cuotas_pendientes = st.number_input(
            "Cuotas pendientes estimadas",
            min_value=1,
            max_value=360,
            value=24,
            step=1,
            key=f"cuotas_pendientes{suffix}"
        )

    col1, col2 = st.columns(2)
    with col1:
        monto_inicial = campo_moneda_decimal(
            "Monto total desembolsado",
            f"monto_inicial{suffix}"
        )
    with col2:
        saldo_actual = campo_moneda_decimal(
            "Saldo actual adeudado",
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
            "Periodicidad",
            ["Efectiva anual (EA)", "IPC + puntos", "Mensual"],
            key=f"periodicidad{suffix}"
        )

    col5, col6 = st.columns(2)
    with col5:
        valor_cuota = campo_moneda_decimal(
            "Valor de la cuota mensual",
            f"valor_cuota{suffix}"
        )
    with col6:
        fecha_proximo_pago = st.date_input(
            "Fecha del próximo pago",
            value=date.today(),
            key=f"fecha_proximo_pago{suffix}"
        )

    monto_inicial_num = limpiar_moneda_decimal(monto_inicial)
    saldo_actual_num = limpiar_moneda_decimal(saldo_actual)
    valor_cuota_num = limpiar_moneda_decimal(valor_cuota)

    if st.button("Registrar crédito educativo", key=f"btn_reg{suffix}"):
        if not entidad.strip():
            st.error("Ingresa la entidad o institución del crédito educativo.")
        elif saldo_actual_num <= 0:
            st.error("El saldo actual debe ser mayor a cero.")
        elif valor_cuota_num <= 0:
            st.error("El valor de la cuota mensual debe ser mayor a cero.")
        else:
            nombre = entidad.strip()
            if carrera.strip():
                nombre += f" ({carrera.strip()})"

            nueva_deuda = {
                "tipo": "Crédito educativo",
                "entidad": nombre,
                "monto_inicial": monto_inicial_num or saldo_actual_num,
                "saldo_actual": saldo_actual_num,
                "tasa": tasa,
                "periodicidad_tasa": periodicidad,
                "tipo_tasa": estado_credito,
                "anos": cuotas_pendientes // 12,
                "meses": cuotas_pendientes % 12,
                "total_cuotas": cuotas_pendientes,
                "cuota_proxima": 1,
                "cuotas_pendientes": cuotas_pendientes,
                "valor_cuota": valor_cuota_num,
                "proximo_pago": str(fecha_proximo_pago)
            }
            st.session_state.deudas.append(nueva_deuda)
            st.success(f"¡Crédito educativo ({nombre}) registrado exitosamente!")
            st.rerun()
