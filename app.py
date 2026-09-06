import streamlit as st
import re


# ======================================
# CONFIGURACIÓN
# ======================================

st.set_page_config(
    page_title="Asistente Financiero Inteligente",
    page_icon="💰",
    layout="centered"
)


# ======================================
# INICIALIZAR DEUDAS
# ======================================

if "deudas" not in st.session_state:
    st.session_state.deudas = []

# ======================================
# UTILIDADES Y MÓDULO DE DEUDAS
# ======================================

from utils import (
    campo_moneda,
    campo_moneda_decimal,
    limpiar_moneda,
    limpiar_moneda_decimal,
    mostrar_moneda
)
from deudas import TIPOS_DEUDAS, render_formulario_deuda



# ======================================
# TÍTULO
# ======================================

st.title("Asistente Financiero Inteligente")

st.write(
    "Aplicación de Inteligencia Artificial para analizar "
    "ingresos, gastos, ahorro y nivel financiero."
)

st.markdown("---")


# ======================================
# COLUMNAS
# ======================================

col1, espacio, col2 = st.columns([1, 0.08, 1])


# ======================================
# INGRESOS
# ======================================

with col1:

    with st.container(border=True):

        st.subheader("Ingresos")

        salario = campo_moneda(
            "Salario mensual",
            "salario"
        )

        otros_ingresos = campo_moneda(
            "Otros ingresos",
            "otros_ingresos"
        )

        st.markdown("---")

        st.subheader("Familia y educación")

        hijos = st.number_input(
            "Cantidad de hijos",
            min_value=0,
            step=1
        )

        colegio = campo_moneda(
            "Pago de colegio",
            "colegio"
        )

        universidad = campo_moneda(
            "Pago de universidad",
            "universidad"
        )


# ======================================
# GASTOS
# ======================================

with col2:

    with st.container(border=True):

        st.subheader("Gastos mensuales")

        alimentacion = campo_moneda(
            "Alimentación",
            "alimentacion"
        )

        transporte = campo_moneda(
            "Transporte",
            "transporte"
        )

        vestimenta = campo_moneda(
            "Vestimenta",
            "vestimenta"
        )

        entretenimiento = campo_moneda(
            "Entretenimiento",
            "entretenimiento"
        )

        arriendo = campo_moneda(
            "Arriendo o hipoteca",
            "arriendo"
        )

        servicios = campo_moneda(
            "Servicios públicos",
            "servicios"
        )


# ======================================
# DEUDAS
# ======================================

st.markdown("---")

st.subheader("Deudas y Obligaciones Financieras")

st.write(
    "Selecciona los tipos de deuda que posees actualmente. "
    "Puedes seleccionar múltiples opciones simultáneamente para registrar varios créditos:"
)

tipos_seleccionados = st.multiselect(
    "Tipos de deuda a registrar",
    options=list(TIPOS_DEUDAS.keys()),
    default=[],
    placeholder="Selecciona uno o más tipos de crédito...",
    key="tipos_deuda_seleccionados"
)

if tipos_seleccionados:
    for tipo_sel in tipos_seleccionados:
        info_deuda = TIPOS_DEUDAS[tipo_sel]
        with st.expander(
            f"{info_deuda['icono']} {tipo_sel} — {info_deuda['descripcion']}",
            expanded=True
        ):
            info_deuda["render"](suffix=f"_{tipo_sel}")
else:
    st.info("💡 Selecciona arriba uno o varios tipos de deuda (ej. Tarjeta de crédito, Crédito hipotecario, etc.) para abrir sus respectivos formularios.")


# ======================================
# MIS DEUDAS
# ======================================

if st.session_state.deudas:

    st.markdown("---")

    st.subheader("Mis deudas registradas")

    # Métricas consolidadas
    total_deuda_acumulada = sum(float(d.get("saldo_actual", 0.0)) for d in st.session_state.deudas)
    total_cuotas_acumuladas = sum(float(d.get("valor_cuota", 0.0)) for d in st.session_state.deudas)
    cant_deudas = len(st.session_state.deudas)

    c_met1, c_met2, c_met3 = st.columns(3)
    with c_met1:
        st.metric("Total deudas registradas", f"{cant_deudas}")
    with c_met2:
        st.metric("Saldo total adeudado", mostrar_moneda(total_deuda_acumulada))
    with c_met3:
        st.metric("Cuotas mensuales totales", mostrar_moneda(total_cuotas_acumuladas))

    for i, deuda in enumerate(st.session_state.deudas):

        with st.container(border=True):

            icono = deuda.get("icono", "💵")

            c_head1, c_head2 = st.columns([3, 1])

            with c_head1:
                st.markdown(
                    f"### {icono} {deuda['tipo']}"
                )

            with c_head2:
                if st.button("🗑️ Eliminar", key=f"eliminar_deuda_{i}"):
                    st.session_state.deudas.pop(i)
                    st.rerun()

            # ==================================
            # VALORES PRINCIPALES
            # ==================================

            col1, col2, col3 = st.columns(
                [1.3, 1.1, 0.8]
            )

            with col1:
                st.caption("Saldo actual")
                st.markdown(
                    f"""
                    <div style="
                        font-size: 25px;
                        font-weight: 500;
                        white-space: nowrap;
                    ">
                        {mostrar_moneda(deuda["saldo_actual"])}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            with col2:
                st.caption("Valor de la cuota")
                st.markdown(
                    f"""
                    <div style="
                        font-size: 25px;
                        font-weight: 500;
                        white-space: nowrap;
                    ">
                        {mostrar_moneda(deuda["valor_cuota"])}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            with col3:
                st.caption("Cuotas pendientes")
                st.markdown(
                    f"""
                    <div style="
                        font-size: 25px;
                        font-weight: 500;
                        white-space: nowrap;
                    ">
                        {deuda.get("cuotas_pendientes", "N/A")}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            # ==================================
            # INFORMACIÓN DETALLADA
            # ==================================

            st.write(
                f"**Entidad / Detalle:** {deuda.get('entidad', 'N/A')}"
            )

            if deuda.get("total_cuotas") not in ["Rotativo", "Pactado"]:
                st.write(
                    f"**Próxima cuota:** "
                    f"{deuda.get('cuota_proxima', 1)} de "
                    f"{deuda.get('total_cuotas', 'N/A')}"
                )

            st.write(
                f"**Tasa:** "
                f"{deuda.get('tasa', 0)}% "
                f"{deuda.get('periodicidad_tasa', '')}"
            )

            st.write(
                f"**Próximo pago:** "
                f"{deuda.get('proximo_pago', 'N/A')}"
            )


# ======================================
# PARTE INFERIOR
# ======================================

st.markdown("")


col3, espacio2, col4 = st.columns([1, 0.08, 1])


with col3:

    with st.container(border=True):

        st.subheader("Compras no esenciales")

        compras = campo_moneda(
            "Compras innecesarias",
            "compras"
        )


with col4:

    with st.container(border=True):

        st.subheader("Meta de ahorro anual")

        meta = campo_moneda(
            "¿Cuánto deseas ahorrar en un año?",
            "meta"
        )


st.markdown("")


# ======================================
# BOTÓN ANALIZAR
# ======================================

if st.button("Analizar situación financiera"):


    # ==================================
    # LIMPIAR DATOS
    # ==================================

    salario_num = limpiar_moneda(salario)

    otros_ingresos_num = limpiar_moneda(
        otros_ingresos
    )


    alimentacion_num = limpiar_moneda(
        alimentacion
    )

    transporte_num = limpiar_moneda(
        transporte
    )

    vestimenta_num = limpiar_moneda(
        vestimenta
    )

    entretenimiento_num = limpiar_moneda(
        entretenimiento
    )

    arriendo_num = limpiar_moneda(
        arriendo
    )

    servicios_num = limpiar_moneda(
        servicios
    )


    colegio_num = limpiar_moneda(
        colegio
    )

    universidad_num = limpiar_moneda(
        universidad
    )


    compras_num = limpiar_moneda(
        compras
    )


    meta_num = limpiar_moneda(
        meta
    )


    # ==================================
    # INGRESOS
    # ==================================

    ingresos_totales = (
        salario_num
        + otros_ingresos_num
    )


    # ==================================
    # GASTOS
    # ==================================

    gastos_totales = (

        alimentacion_num
        + transporte_num
        + vestimenta_num
        + entretenimiento_num
        + arriendo_num
        + servicios_num
        + colegio_num
        + universidad_num
        + compras_num
    )


    saldo = (
        ingresos_totales
        - gastos_totales
    )


    # ==================================
    # PORCENTAJE DE GASTOS
    # ==================================

    if ingresos_totales > 0:

        porcentaje_gasto = (
            gastos_totales
            / ingresos_totales
        ) * 100

    else:

        porcentaje_gasto = 0


    # ==================================
    # SCORE
    # ==================================

    if porcentaje_gasto <= 50:

        score = 90

    elif porcentaje_gasto <= 70:

        score = 70

    elif porcentaje_gasto <= 90:

        score = 50

    else:

        score = 30


    # ==================================
    # DASHBOARD
    # ==================================

    st.markdown("---")

    st.header("Dashboard financiero")


    d1, d2, d3 = st.columns(3)


    with d1:

        with st.container(border=True):

            st.metric(
                "Ingresos",
                f"${ingresos_totales:,.0f}".replace(
                    ",",
                    "."
                )
            )


    with d2:

        with st.container(border=True):

            st.metric(
                "Gastos",
                f"${gastos_totales:,.0f}".replace(
                    ",",
                    "."
                )
            )


    with d3:

        with st.container(border=True):

            st.metric(
                "Disponible",
                f"${saldo:,.0f}".replace(
                    ",",
                    "."
                )
            )


    st.markdown("")


    d4, d5 = st.columns(2)


    with d4:

        with st.container(border=True):

            st.metric(
                "% Gastos",
                f"{porcentaje_gasto:.1f}%"
            )


    with d5:

        with st.container(border=True):

            st.metric(
                "Score financiero",
                f"{score}/100"
            )


    # ==================================
    # ANÁLISIS IA
    # ==================================

    st.markdown("---")

    st.header("Análisis inteligente")


    if porcentaje_gasto >= 90:

        st.error(
            "Tu nivel de gasto es muy alto y representa "
            "un riesgo financiero."
        )


    elif porcentaje_gasto >= 70:

        st.warning(
            "Tus gastos son elevados. Se recomienda "
            "reducir gastos no esenciales."
        )


    else:

        st.success(
            "Tu nivel de gasto es saludable."
        )


    # ==================================
    # RECOMENDACIONES
    # ==================================

    st.header(
        "Recomendaciones financieras"
    )


    if compras_num > 0:

        st.write(
            "- Reduce las compras innecesarias para "
            "mejorar tu capacidad de ahorro."
        )


    if entretenimiento_num > 300000:

        st.write(
            "- Tus gastos en entretenimiento son elevados."
        )


    # ==================================
    # PLAN DE DEUDA
    # ==================================

    st.header(
        "Plan de reducción de deuda"
    )


    deuda_total = 0


    for deuda in st.session_state.deudas:

        deuda_total += deuda.get(
            "saldo_actual",
            0
        )


    if deuda_total > 0:

        pago_sugerido = max(
            saldo * 0.30,
            0
        )


        deuda1, deuda2 = st.columns(2)


        with deuda1:

            with st.container(border=True):

                st.metric(
                    "Deuda total",
                    mostrar_moneda(deuda_total)
                )


        with deuda2:

            with st.container(border=True):

                st.metric(
                    "Pago sugerido mensual",
                    mostrar_moneda(pago_sugerido)
                )


                st.caption(
                    "La IA recomienda destinar el 30% "
                    "del dinero disponible al pago de deuda."
                )


        st.info(
            "Este plan busca reducir intereses sin "
            "afectar tu estabilidad financiera."
        )


    else:

        st.success(
            "Actualmente no registras deudas."
        )


    # ==================================
    # ESTRATEGIAS IA
    # ==================================

    st.markdown("---")

    st.header(
        "Estrategias inteligentes IA"
    )


    # ==================================
    # AHORRO IA
    # ==================================

    st.subheader(
        "Plan inteligente de ahorro"
    )


    if saldo > 0:

        ahorro_ideal = (
            ingresos_totales * 0.20
        )


        ahorro_semanal = (
            ahorro_ideal / 4
        )


        ahorro_anual = (
            ahorro_ideal * 12
        )


        st.write(
            "La IA recomienda ahorrar el 20% "
            "de tus ingresos."
        )


        st.markdown("")


        a1, a2, a3 = st.columns(3)


        with a1:

            st.metric(
                "Ahorro semanal",
                f"${ahorro_semanal:,.0f}".replace(
                    ",",
                    "."
                )
            )


            st.caption(
                "Proyección semanal recomendada"
            )


        with a2:

            st.metric(
                "Ahorro mensual",
                f"${ahorro_ideal:,.0f}".replace(
                    ",",
                    "."
                )
            )


            st.caption(
                "Meta mensual sugerida"
            )


        with a3:

            st.metric(
                "Proyección anual",
                f"${ahorro_anual:,.0f}".replace(
                    ",",
                    "."
                )
            )


            st.caption(
                "Ahorro estimado en un año"
            )


        st.markdown("")


        # ==================================
        # VALIDACIÓN META
        # ==================================

        if ahorro_anual >= meta_num:

            st.success(
                "Tu capacidad financiera actual sí permite "
                "alcanzar esta meta anual."
            )


            ok1, ok2, ok3 = st.columns(3)


            with ok1:

                st.metric(
                    "Meta anual",
                    f"${meta_num:,.0f}".replace(
                        ",",
                        "."
                    )
                )


            with ok2:

                st.metric(
                    "Capacidad anual",
                    f"${ahorro_anual:,.0f}".replace(
                        ",",
                        "."
                    )
                )


            with ok3:

                diferencia = (
                    ahorro_anual
                    - meta_num
                )


                st.metric(
                    "Margen adicional",
                    f"${diferencia:,.0f}".replace(
                        ",",
                        "."
                    )
                )


            st.info(
                "Manteniendo disciplina financiera "
                "podrías cumplir tu objetivo anual de ahorro."
            )


        else:

            faltante = (
                meta_num
                - ahorro_anual
            )


            ahorro_semanal_meta = (
                meta_num / 52
            )


            ahorro_mensual_meta = (
                meta_num / 12
            )


            st.warning(
                "Tu capacidad actual no alcanza "
                "la meta anual deseada."
            )


            meta1, meta2, meta3 = st.columns(3)


            with meta1:

                st.metric(
                    "Ahorro semanal requerido",
                    f"${ahorro_semanal_meta:,.0f}".replace(
                        ",",
                        "."
                    )
                )


            with meta2:

                st.metric(
                    "Ahorro mensual requerido",
                    f"${ahorro_mensual_meta:,.0f}".replace(
                        ",",
                        "."
                    )
                )


            with meta3:

                st.metric(
                    "Meta anual",
                    f"${meta_num:,.0f}".replace(
                        ",",
                        "."
                    )
                )


            st.info(
                f"Actualmente podrías ahorrar aproximadamente "
                f"${ahorro_anual:,.0f} al año.".replace(
                    ",",
                    "."
                )
            )


            st.write(
                f"- Necesitas aumentar aproximadamente "
                f"${faltante:,.0f} anuales.".replace(
                    ",",
                    "."
                )
            )


            st.write(
                "- Reduce gastos variables y compras innecesarias."
            )


            st.write(
                "- Considera ingresos adicionales o ahorro automático."
            )


    else:

        st.error(
            "Actualmente tus gastos superan tus ingresos."
        )


        st.write(
            "- Activa modo ahorro extremo."
        )


        st.write(
            "- Reduce entretenimiento y compras innecesarias."
        )


        st.write(
            "- Prioriza pagos esenciales."
        )


    # ==================================
    # MÉTODOS IA
    # ==================================

    st.markdown("---")


    t1, t2 = st.columns(2)


    with t1:

        with st.container(border=True):

            st.subheader(
                "Método bola de nieve"
            )


            st.write(
                "• Paga primero las deudas más pequeñas."
            )


            st.write(
                "• Cada deuda eliminada libera más "
                "dinero mensual."
            )


            st.write(
                "• Mejora motivación y control financiero."
            )


    with t2:

        with st.container(border=True):

            st.subheader(
                "Método avalancha"
            )


            st.write(
                "• Prioriza las deudas con intereses más altos."
            )


            st.write(
                "• Reduce el pago total de intereses."
            )


            st.write(
                "• Método matemáticamente más eficiente."
            )


    st.markdown("")


    t3, t4 = st.columns(2)


    with t3:

        with st.container(border=True):

            st.subheader(
                "Nivel financiero"
            )


            if porcentaje_gasto <= 50:

                st.success(
                    "Nivel financiero saludable."
                )


            elif porcentaje_gasto <= 70:

                st.warning(
                    "Nivel financiero intermedio."
                )


            else:

                st.error(
                    "Nivel financiero de riesgo."
                )


    with t4:

        with st.container(border=True):

            st.subheader(
                "Capacidad financiera anual IA"
            )


            if saldo > 0:

                proyeccion = saldo * 12


                st.metric(
                    "Capacidad de ahorro anual",
                    f"${proyeccion:,.0f}".replace(
                        ",",
                        "."
                    )
                )


            else:

                st.error(
                    "Posible aumento de deuda."
                )