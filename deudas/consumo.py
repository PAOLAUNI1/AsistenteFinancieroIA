import streamlit as st
from datetime import date
from utils import campo_moneda_decimal, limpiar_moneda_decimal


def render_formulario(suffix="_consumo"):
    """
    Renderiza el formulario para registrar un Crédito de Consumo / Comercio.
    """
    st.markdown("##### Datos del Crédito de Consumo")

    col_c1, col_c2 = st.columns(2)
    with col_c1:
        entidad = st.text_input(
            "Almacén / Entidad financiera",
            placeholder="Ej. Alkosto, Falabella, Éxito, Banco",
            key=f"entidad{suffix}"
        )
    with col_c2:
        articulo = st.text_input(
            "Artículo o concepto (Opcional)",
            placeholder="Ej. Computador, Celular, Muebles",
            key=f"articulo{suffix}"
        )

    col1, col2 = st.columns(2)
    with col1:
        monto_inicial = campo_moneda_decimal(
            "Monto financiado original",
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
            ["Mensual", "Efectiva anual (EA)"],
            key=f"periodicidad{suffix}"
        )

    col5, col6, col7 = st.columns([1, 1, 1.5])
    with col5:
        total_cuotas = st.number_input(
            "Total de cuotas",
            min_value=1,
            max_value=72,
            value=12,
            step=1,
            key=f"total_cuotas{suffix}"
        )
    with col6:
        cuota_proxima = st.number_input(
            "Próxima cuota a pagar",
            min_value=1,
            step=1,
            key=f"cuota_proxima{suffix}"
        )
    with col7:
        valor_cuota = campo_moneda_decimal(
            "Valor de la cuota mensual",
            f"valor_cuota{suffix}"
        )

    fecha_proximo_pago = st.date_input(
        "Fecha del próximo pago",
        value=date.today(),
        key=f"fecha_proximo_pago{suffix}"
    )

    monto_inicial_num = limpiar_moneda_decimal(monto_inicial)
    saldo_actual_num = limpiar_moneda_decimal(saldo_actual)
    valor_cuota_num = limpiar_moneda_decimal(valor_cuota)
    cuotas_pendientes = max(total_cuotas - cuota_proxima + 1, 0)

    if total_cuotas > 0:
        c1, c2 = st.columns(2)
        with c1:
            st.caption(f"Cuotas pactadas: **{total_cuotas}**")
        with c2:
            st.caption(f"Cuotas pendientes: **{cuotas_pendientes}**")

    if st.button("Registrar crédito de consumo", key=f"btn_reg{suffix}"):
        if not entidad.strip():
            st.error("Ingresa la entidad o comercio del crédito.")
        elif saldo_actual_num <= 0:
            st.error("El saldo actual debe ser mayor a cero.")
        elif cuota_proxima > total_cuotas:
            st.error("La próxima cuota no puede ser superior al total de cuotas.")
        elif valor_cuota_num <= 0:
            st.error("El valor de la cuota mensual debe ser mayor a cero.")
        else:
            nombre = entidad.strip()
            if articulo.strip():
                nombre += f" ({articulo.strip()})"

            nueva_deuda = {
                "tipo": "Crédito de consumo",
                "entidad": nombre,
                "monto_inicial": monto_inicial_num or saldo_actual_num,
                "saldo_actual": saldo_actual_num,
                "tasa": tasa,
                "periodicidad_tasa": periodicidad,
                "tipo_tasa": "Fija",
                "anos": total_cuotas // 12,
                "meses": total_cuotas % 12,
                "total_cuotas": total_cuotas,
                "cuota_proxima": cuota_proxima,
                "cuotas_pendientes": cuotas_pendientes,
                "valor_cuota": valor_cuota_num,
                "proximo_pago": str(fecha_proximo_pago)
            }
            st.session_state.deudas.append(nueva_deuda)
            st.success(f"¡Crédito de consumo ({nombre}) registrado!")
            st.rerun()
