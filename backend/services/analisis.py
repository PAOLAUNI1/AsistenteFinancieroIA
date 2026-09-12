"""
Cálculo del panel financiero (sección 26/36 de CLAUDE.md), migrado tal cual
del bloque "Analizar situación financiera" de app.py (líneas ~394-841),
quitando el renderizado de Streamlit.
"""


def calcular_analisis(
    salario: float,
    otros_ingresos: float,
    alimentacion: float,
    transporte: float,
    vestimenta: float,
    entretenimiento: float,
    arriendo: float,
    servicios: float,
    colegio: float,
    universidad: float,
    compras: float,
    meta_ahorro_anual: float,
    deuda_total: float,
) -> dict:
    ingresos_totales = salario + otros_ingresos

    gastos_totales = (
        alimentacion
        + transporte
        + vestimenta
        + entretenimiento
        + arriendo
        + servicios
        + colegio
        + universidad
        + compras
    )

    saldo = ingresos_totales - gastos_totales

    porcentaje_gasto = (gastos_totales / ingresos_totales) * 100 if ingresos_totales > 0 else 0

    if porcentaje_gasto <= 50:
        score = 90
        nivel_gasto = "saludable"
    elif porcentaje_gasto <= 70:
        score = 70
        nivel_gasto = "elevado"
    elif porcentaje_gasto <= 90:
        score = 50
        nivel_gasto = "elevado"
    else:
        score = 30
        nivel_gasto = "riesgo"

    pago_sugerido_deuda = max(saldo * 0.30, 0) if deuda_total > 0 else 0.0

    ahorro_ideal_mensual = ingresos_totales * 0.20 if saldo > 0 else 0.0
    ahorro_semanal = ahorro_ideal_mensual / 4
    ahorro_anual = ahorro_ideal_mensual * 12

    meta_alcanzable = ahorro_anual >= meta_ahorro_anual if meta_ahorro_anual > 0 else None

    return {
        "ingresos_totales": ingresos_totales,
        "gastos_totales": gastos_totales,
        "saldo_disponible": saldo,
        "porcentaje_gasto": round(porcentaje_gasto, 1),
        "score_financiero": score,
        "nivel_gasto": nivel_gasto,
        "deuda_total": deuda_total,
        "pago_sugerido_deuda": pago_sugerido_deuda,
        "ahorro_semanal_sugerido": ahorro_semanal,
        "ahorro_mensual_sugerido": ahorro_ideal_mensual,
        "ahorro_anual_proyectado": ahorro_anual,
        "meta_ahorro_anual": meta_ahorro_anual,
        "meta_alcanzable": meta_alcanzable,
    }
