import streamlit as st
from datetime import date
from utils import campo_moneda_decimal, limpiar_moneda_decimal


def render_formulario(suffix="_personal"):
    """
    Renderiza el formulario para registrar un Préstamo Personal / Informal.
    """
    st.markdown("##### 🤝 Datos del Préstamo Personal")

    col_p1, col_p2 = st.columns(2)
    with col_p1:
        prestamista = st.text_input(
            "Nombre del prestamista / Acreedor",
            placeholder="Ej. Juan Pérez, Tío Carlos, Empresa",
            key=f"prestamista{suffix}"
        )
    with col_p2:
        tipo_relacion = st.selectbox(
            "Tipo de relación / Fuente",
            ["Familiar", "Amigo / Compañero", "Particular / Tercero", "Préstamo laboral"],
            key=f"tipo_relacion{suffix}"
        )

    col1, col2 = st.columns(2)
    with col1:
        monto_inicial = campo_moneda_decimal(
            "Monto original prestado",
            f"monto_inicial{suffix}"
        )
    with col2:
        saldo_actual = campo_moneda_decimal(
            "Saldo pendiente a pagar",
            f"saldo_actual{suffix}"
        )

    col3, col4 = st.columns(2)
    with col3:
        tasa = st.number_input(
            "Tasa de interés mensual (%) - (0% si no cobra)",
            min_value=0.0,
            max_value=100.0,
            value=0.0,
            step=0.1,
            key=f"tasa{suffix}"
        )
    with col4:
        valor_cuota = campo_moneda_decimal(
            "Abono / Cuota mensual acordada",
            f"valor_cuota{suffix}"
        )

    fecha_proximo_pago = st.date_input(
        "Fecha del próximo abono",
        value=date.today(),
        key=f"fecha_proximo_pago{suffix}"
    )

    monto_inicial_num = limpiar_moneda_decimal(monto_inicial)
    saldo_actual_num = limpiar_moneda_decimal(saldo_actual)
    valor_cuota_num = limpiar_moneda_decimal(valor_cuota)

    # Estimación de cuotas restantes
    if valor_cuota_num > 0 and saldo_actual_num > 0:
        cuotas_est = int(round(saldo_actual_num / valor_cuota_num))
        st.caption(f"Tiempo estimado para terminar de pagar: **~{cuotas_est} pagos mensuales**")

    if st.button("➕ Registrar préstamo personal", key=f"btn_reg{suffix}"):
        if not prestamista.strip():
            st.error("Ingresa el nombre del prestamista o acreedor.")
        elif saldo_actual_num <= 0:
            st.error("El saldo pendiente debe ser mayor a cero.")
        elif valor_cuota_num <= 0:
            st.error("El abono mensual acordado debe ser mayor a cero.")
        else:
            nombre = f"{prestamista.strip()} ({tipo_relacion})"
            nueva_deuda = {
                "tipo": "Préstamo personal",
                "icono": "🤝",
                "entidad": nombre,
                "monto_inicial": monto_inicial_num or saldo_actual_num,
                "saldo_actual": saldo_actual_num,
                "tasa": tasa,
                "periodicidad_tasa": "Mensual" if tasa > 0 else "Sin interés",
                "tipo_tasa": "Personal / Informal",
                "anos": 0,
                "meses": 0,
                "total_cuotas": "Pactado",
                "cuota_proxima": 1,
                "cuotas_pendientes": "Acuerdo mutuo",
                "valor_cuota": valor_cuota_num,
                "proximo_pago": str(fecha_proximo_pago)
            }
            st.session_state.deudas.append(nueva_deuda)
            st.success(f"¡Préstamo personal con {prestamista} registrado!")
            st.rerun()
