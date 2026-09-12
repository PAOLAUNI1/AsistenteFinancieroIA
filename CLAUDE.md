# CLAUDE.md --- Contexto completo del proyecto IA Financiera

## Propósito

Este documento reúne el contexto funcional, académico y técnico del
proyecto **IA Financiera / Asistente Financiero Inteligente** para que
el asistente de IA (actualmente Claude Code) pueda continuar el
desarrollo sin perder decisiones ya tomadas.

### Reglas para el asistente

-   No reinventar decisiones funcionales ya tomadas sin indicación
    explícita.
-   Trabajar por etapas, en orden, con cambios concretos y comprobables.
-   Si se solicita un archivo completo, entregar el archivo completo.
-   No modificar funcionalidades no relacionadas con la tarea actual.
-   Respetar la estructura existente.
-   Cuidar especialmente la indentación de Python y la compatibilidad
    con Streamlit.

------------------------------------------------------------------------

## 1. Proyecto

**Nombre:** Asistente Financiero Inteligente\
**Proyecto interno:** IA_FINANCIERA

Es una aplicación de Inteligencia Artificial para analizar y controlar
la situación financiera personal.

Busca registrar ingresos, gastos, deudas y metas de ahorro; calcular
indicadores; detectar riesgos de endeudamiento y generar recomendaciones
personalizadas.

------------------------------------------------------------------------

## 2. Contexto académico

Es un trabajo de grado de **Ingeniería de Software**, con una duración
aproximada de **5 meses**.

El profesor señaló:

-   El proyecto contempla una aplicación móvil.
-   Se deben considerar múltiples variables relacionadas con el ahorro.
-   Se deben considerar diferentes comportamientos de los individuos.
-   Hay que evaluar la viabilidad de cubrir Android/iPhone en el tiempo
    disponible.
-   Se debe diferenciar **gestión** de **control**.
-   Se debe validar que la solución no sea simplemente equivalente a
    preguntar a una IA generativa comercial como ChatGPT, Claude o
    Gemini.

### Decisión actual

La plataforma objetivo definida es **Android**. No se pretende
desarrollar simultáneamente Android e iPhone.

La solución debe diferenciarse de un chatbot genérico mediante datos
financieros estructurados, reglas de negocio, cálculos, historial,
seguimiento y recomendaciones específicas.

------------------------------------------------------------------------

## 3. Tecnología actual

El prototipo actual utiliza:

-   Python
-   Streamlit
-   `modelo.py`
-   `recomendaciones.py`
-   `dataset.csv`

Estructura actual:

``` text
IA_FINANCIERA/
├── app.py
├── dataset.csv
├── modelo.py
├── recomendaciones.py
├── utils.py
└── deudas/
    ├── __init__.py
    ├── consumo.py
    ├── educativo.py
    ├── hipotecario.py
    ├── libre_inversion.py
    ├── prestamo_personal.py
    ├── tarjeta.py
    └── vehiculo.py
```

`utils.py` contiene las funciones de formato/parseo monetario descritas
en la sección 11 (`campo_moneda`, `campo_moneda_decimal`,
`limpiar_moneda`, `limpiar_moneda_decimal`, `mostrar_moneda`).

Para ejecutar localmente, preferir:

``` bash
python -m streamlit run app.py
```

------------------------------------------------------------------------

## 4. Interfaz actual

### Título

**Asistente Financiero Inteligente**

Subtítulo:

> Aplicación de Inteligencia Artificial para analizar ingresos, gastos,
> ahorro y nivel financiero.

### Ingresos

-   Salario mensual
-   Otros ingresos

### Familia y educación

-   Cantidad de hijos
-   Pago de colegio
-   Pago de universidad

### Gastos mensuales

-   Alimentación
-   Transporte
-   Vestimenta
-   Entretenimiento
-   Arriendo o hipoteca
-   Servicios públicos

### Deudas

Selector desplegable:

1.  Crédito hipotecario
2.  Tarjeta de crédito
3.  Crédito de vehículo
4.  Crédito educativo
5.  Préstamo de libre inversión
6.  Préstamo personal
7.  Crédito de consumo

La selección debe mostrar únicamente el formulario correspondiente.

------------------------------------------------------------------------

## 5. Flujo general de deudas

``` text
Deudas
  ↓
Seleccionar tipo
  ↓
Aparece formulario específico
  ↓
Registrar datos
  ↓
Validar
  ↓
Guardar deuda
  ↓
Ocultar formulario
  ↓
Mostrar en Mis deudas
```

Una deuda registrada no debe obligar al usuario a volver a ingresar sus
datos.

------------------------------------------------------------------------

# 6. Crédito hipotecario

Este es el primer formulario implementado y probado.

### Campos

-   Entidad financiera
-   Monto inicial del crédito
-   Saldo actual
-   Tasa de interés
-   Periodicidad de la tasa
-   Tipo de tasa
-   Años
-   Meses
-   Valor de la cuota
-   Próxima cuota a pagar
-   Fecha del próximo pago

### Periodicidad

Opciones actuales:

-   Efectiva anual (EA)
-   Mensual

### Tipo de tasa

-   Fija
-   Variable

------------------------------------------------------------------------

## 7. Plazo hipotecario

El usuario no debe tener que convertir manualmente años a meses.

Se ingresan:

``` text
Años
Meses
```

y el sistema calcula:

``` text
total_cuotas = años * 12 + meses
```

Ejemplo:

``` text
20 años + 0 meses = 240 cuotas
```

Otro ejemplo:

``` text
1 año + 6 meses = 18 meses
```

------------------------------------------------------------------------

## 8. Cuotas hipotecarias

Campo:

**Próxima cuota a pagar**

Ejemplo:

``` text
22
```

Si el crédito tiene 240 cuotas:

``` text
cuotas_pendientes = 240 - 22 + 1
```

Resultado:

``` text
219
```

La fecha del próximo pago es importante porque permitirá posteriormente
implementar recordatorios y control de vencimientos.

No se considera necesario pedir "fecha del último extracto".

------------------------------------------------------------------------

## 9. Ejemplo utilizado

Se utilizó un extracto real como referencia de diseño con valores
similares a:

``` text
Valor a pagar: $994.114,88
Saldo: $93.779.719,02
Tasa: 11,00% EA
Valor desembolso: $96.145.520,00
Plazo total: 240 meses
Número de cuota a cancelar: 022
Cuotas pendientes: 219
```

También se probó:

``` text
Entidad: Bancolombia
Monto inicial: $100.000.000,00
Saldo actual: $90.000.000,00
Tasa: 11.00%
Tipo: Fija
Plazo: 20 años
Valor cuota: $994.114,88
Próxima cuota: 22
```

------------------------------------------------------------------------

## 10. Validaciones hipotecarias

Actualmente deben validarse:

-   Entidad no vacía.
-   Monto inicial \> 0.
-   Saldo actual \> 0.
-   Saldo actual \<= monto inicial.
-   Tasa \> 0.
-   Plazo \> 0.
-   Próxima cuota \<= total de cuotas.
-   Valor de cuota \> 0.

------------------------------------------------------------------------

## 11. Formato monetario

La interfaz utiliza formato colombiano.

Campos normales:

``` text
$5.000.000
```

Campos hipotecarios con decimales:

``` text
$96.145.520,00
$93.779.719,02
$994.114,88
```

Internamente los valores deben convertirse a números para permitir
cálculos.

La aplicación tiene funciones para:

-   capturar moneda;
-   capturar moneda con decimales;
-   limpiar moneda;
-   limpiar moneda decimal;
-   mostrar moneda.

No crear funciones duplicadas que hagan lo mismo.

------------------------------------------------------------------------

## 12. Mis deudas

Después del registro debe aparecer algo como:

``` text
Mis deudas

🏠 Crédito hipotecario

Saldo actual       Valor de la cuota       Cuotas pendientes
$93.779.719,02     $994.114,88             219

Entidad: Bancolombia

Próxima cuota: 22 de 240

Tasa: 11,0% Efectiva anual (EA)

Próximo pago: 2026-09-17
```

Los importes largos no deben aparecer cortados con `...`.

Se redujo el tamaño visual de los importes para solucionar ese problema.

------------------------------------------------------------------------

## 13. Comportamiento al registrar

Al pulsar:

``` text
Registrar crédito hipotecario
```

debe:

1.  Validar.
2.  Guardar en `st.session_state.deudas`.
3.  Mostrar confirmación.
4.  Cambiar el selector a `Seleccionar...`.
5.  Ejecutar `st.rerun()`.
6.  Ocultar el formulario.
7.  Mantener la deuda visible en `Mis deudas`.

El selector utiliza:

``` python
key="tipo_deuda"
```

y la solución acordada para ocultar el formulario es:

``` python
st.session_state.tipo_deuda = "Seleccionar..."
st.rerun()
```

No es necesario mantener una variable separada como
`formulario_hipotecario_registrado`.

------------------------------------------------------------------------

# 14. Persistencia

Actualmente las deudas se almacenan temporalmente mediante:

``` python
st.session_state.deudas
```

Esto sirve para el prototipo.

Posteriormente se debe implementar almacenamiento permanente, por
ejemplo mediante SQLite u otra base de datos adecuada.

No adelantar esta etapa antes de estabilizar los siete formularios.

------------------------------------------------------------------------

# 15. Tarjeta de crédito

Tiene lógica diferente al hipotecario.

Datos definidos:

-   Cupo total
-   Deuda actual
-   Tasa de interés
-   Número de cuotas
-   Fecha de corte
-   Fecha de pago

Debe contemplarse que algunas tarjetas pueden no cobrar intereses si la
compra se paga a una cuota, mientras que otras condiciones pueden
variar.

No asumir una regla universal.

------------------------------------------------------------------------

## 16. Compras con tarjeta

Una tarjeta registrada no debe volver a registrarse para cada compra.

Flujo:

``` text
Tarjeta registrada
  ↓
Agregar compra
  ↓
Asociar compra a la tarjeta existente
```

La nueva compra solo debe solicitar sus datos propios.

------------------------------------------------------------------------

## 17. Cupo de tarjeta

Ejemplo:

``` text
Cupo: $800.000
Disponible: $200.000
```

El sistema debe impedir registrar una compra que exceda el cupo
disponible.

El objetivo es controlar registros y saldos, no explicar al usuario una
obviedad.

------------------------------------------------------------------------

## 18. Corte y pago de tarjeta

Ejemplo:

``` text
Fecha de corte: día 15
Fecha de pago: día 5
```

Una compra realizada después del corte pertenece al siguiente ciclo de
facturación.

Ejemplo conceptual:

``` text
Corte: 15 de agosto
Compra: 16 de agosto
↓
No pertenece al extracto que acaba de cerrar
↓
Pasa al siguiente ciclo
```

La implementación debe considerar correctamente el ciclo de facturación
y, cuando se implemente, verificarse con fuentes confiables y
condiciones reales de las entidades.

------------------------------------------------------------------------

# 19. Crédito de vehículo

Es uno de los siete formularios.

Debe diferenciarse de un préstamo personal.

Debe permitir controlar, según corresponda:

-   monto financiado;
-   saldo;
-   tasa;
-   plazo;
-   cuota;
-   cuotas;
-   fecha de pago;
-   información básica del vehículo.

No convertirlo en un formulario genérico que pierda las características
del producto.

------------------------------------------------------------------------

# 20. Crédito educativo

Debe contemplar que algunas modalidades tienen intereses y otras no.

El plazo debe aceptar años + meses.

Ejemplo:

``` text
1 año + 6 meses
=
18 meses
```

No obligar al usuario a hacer conversiones manuales.

------------------------------------------------------------------------

# 21. Préstamo de libre inversión

Debe mantenerse separado de:

-   crédito de consumo;
-   préstamo personal;
-   tarjeta de crédito.

Debe controlar:

-   monto inicial;
-   saldo;
-   tasa;
-   plazo;
-   cuota;
-   cuotas pendientes;
-   fecha de pago.

------------------------------------------------------------------------

# 22. Préstamo personal

Definición adoptada:

> Dinero prestado por un familiar, amigo o particular.

Puede no existir entidad financiera.

Debe poder manejar:

-   prestamista;
-   monto;
-   saldo;
-   interés o ausencia de interés;
-   cuota;
-   plazo;
-   fecha de pago.

------------------------------------------------------------------------

# 23. Crédito de consumo

Debe mantenerse separado de libre inversión.

Conceptualmente, el crédito de consumo se orienta a financiar bienes o
servicios de consumo, mientras que libre inversión permite un uso más
libre del dinero.

Debe controlar:

-   monto;
-   saldo;
-   tasa;
-   plazo;
-   cuota;
-   cuotas;
-   fecha de pago.

------------------------------------------------------------------------

# 24. Opción descartada

No incluir como tipo independiente:

``` text
Compra financiada
```

porque puede corresponder a una tarjeta u otra modalidad de
financiación.

------------------------------------------------------------------------

# 25. Arriendo

Por ahora no se implementará como una deuda independiente.

Se mantiene como gasto mensual:

``` text
Arriendo o hipoteca
```

------------------------------------------------------------------------

# 26. Análisis financiero

El sistema debe analizar:

-   ingresos;
-   gastos;
-   ahorro;
-   deudas;
-   capacidad de pago;
-   nivel de endeudamiento;
-   sobreendeudamiento;
-   metas.

No basta con mostrar sumas. Los datos deben convertirse en indicadores y
recomendaciones útiles.

------------------------------------------------------------------------

# 27. Ahorro

Base:

``` text
Ingresos - Gastos = Dinero disponible
```

El sistema puede calcular:

-   capacidad de ahorro;
-   ahorro mensual;
-   ahorro anual;
-   ahorro requerido para una meta.

El prototipo actual usa como referencia inicial un 20% de los ingresos,
pero esto no debe tratarse como una regla universal.

A futuro, la recomendación debe depender del perfil financiero.

------------------------------------------------------------------------

# 28. Sobreendeudamiento

Es un componente importante del proyecto.

Debe analizar la relación entre:

``` text
Ingresos
Gastos
Cuotas de deuda
```

y clasificar el nivel de riesgo, por ejemplo:

-   saludable;
-   elevado;
-   riesgo de sobreendeudamiento.

No depender únicamente de la percepción del usuario.

El sistema debe calcularlo a partir de los datos registrados.

------------------------------------------------------------------------

# 29. Gestión vs. control

### Gestión

Incluye:

-   registrar;
-   organizar;
-   actualizar;
-   consultar;
-   administrar deudas;
-   establecer metas;
-   planificar.

### Control

Incluye:

-   seguimiento;
-   vencimientos;
-   cumplimiento;
-   evolución del saldo;
-   cuotas pendientes;
-   capacidad de pago;
-   alertas;
-   desviaciones frente al presupuesto;
-   detección de riesgo.

El proyecto debe demostrar claramente ambos conceptos.

------------------------------------------------------------------------

# 30. Diferencia frente a una IA generativa comercial

No presentar el proyecto como:

> "Una aplicación que le pregunta a una IA qué hacer con su dinero."

La propuesta debe ser:

``` text
Datos financieros estructurados
        ↓
Modelo financiero
        ↓
Reglas de negocio
        ↓
Cálculos
        ↓
Indicadores
        ↓
Perfil financiero
        ↓
Análisis
        ↓
Recomendaciones
        ↓
Seguimiento
```

La IA generativa puede complementar el sistema, pero no debe sustituir:

-   modelo de datos;
-   reglas;
-   cálculos;
-   validaciones;
-   historial;
-   seguimiento.

------------------------------------------------------------------------

# 31. Arquitectura conceptual futura

``` text
                 USUARIO
                    │
                    ▼
             INTERFAZ ANDROID
                    │
                    ▼
             API / BACKEND
                    │
        ┌───────────┴───────────┐
        ▼                       ▼
 MODELO FINANCIERO         BASE DE DATOS
        │
        ├── Ingresos
        ├── Gastos
        ├── Deudas
        ├── Ahorro
        └── Movimientos
        │
        ▼
 MOTOR DE REGLAS
        │
        ├── Capacidad de pago
        ├── Endeudamiento
        ├── Sobreendeudamiento
        ├── Ahorro
        └── Vencimientos
        │
        ▼
 MOTOR IA
        │
        ▼
 RECOMENDACIONES PERSONALIZADAS
```

El Streamlit actual es un prototipo; no asumir que será necesariamente
la arquitectura final Android.

------------------------------------------------------------------------

# 32. Orden de desarrollo

Seguir este orden:

1.  ✅ Estabilizar estructura base.
2.  ✅ Completar crédito hipotecario.
3.  ✅ Completar tarjeta de crédito.
4.  ✅ Completar crédito de vehículo.
5.  ✅ Completar crédito educativo.
6.  ✅ Completar préstamo de libre inversión.
7.  ✅ Completar préstamo personal.
8.  ✅ Completar crédito de consumo.
9.  ⏳ Centralizar Mis deudas. **(paso actual)**
10. Persistencia.
11. Registro de pagos y movimientos.
12. Cálculo de endeudamiento.
13. Análisis de sobreendeudamiento.
14. Motor de recomendaciones.
15. IA personalizada.
16. Alertas y vencimientos.
17. Pruebas.
18. Preparación Android.
19. Documentación del trabajo de grado.

------------------------------------------------------------------------

# 33. Problemas ya solucionados

### IndentationError

Se producía por bloques `if` con indentación incorrecta.

### Pérdida de `campo_moneda`

Se solucionó manteniendo separadas:

``` python
campo_moneda()
campo_moneda_decimal()
```

### Valores monetarios cortados

Se solucionó mediante una presentación con tamaño controlado en "Mis
deudas".

### Formulario persistente después de registrar

La solución acordada es devolver el selector a:

``` text
Seleccionar...
```

y ejecutar:

``` python
st.rerun()
```

------------------------------------------------------------------------

# 34. Reglas para modificar el código

Antes de modificar:

1.  Identificar el bloque exacto.
2.  No tocar funcionalidades no relacionadas.
3.  Mantener nombres existentes cuando sea posible.
4.  Mantener lógica ya validada.
5.  Probar después de cada etapa.
6.  Si se solicita un archivo completo, entregar un archivo completo.
7.  Evitar funciones duplicadas.
8.  No cambiar siete formularios por uno genérico si eso elimina
    diferencias funcionales.

------------------------------------------------------------------------

# 35. Forma de trabajo

Avanzar directamente.

No desviarse con preguntas innecesarias cuando la siguiente etapa ya
está definida.

Flujo:

``` text
Etapa actual
↓
Implementación
↓
Prueba
↓
Corrección
↓
Siguiente etapa
```

Si existe una decisión técnica indispensable, explicarla brevemente y
aplicar la opción más adecuada.

------------------------------------------------------------------------

# 36. Objetivo funcional final

La aplicación debe ofrecer una visión integral de la situación
financiera personal.

Ejemplo:

``` text
PERFIL FINANCIERO

Ingresos
$5.000.000

Gastos
$2.500.000

Deudas
$3.500.000

Cuotas mensuales
$1.200.000

Ahorro
$800.000

Nivel de endeudamiento
Moderado

Riesgo de sobreendeudamiento
Medio

Meta de ahorro
$10.000.000

Recomendación
Priorizar deuda de mayor costo
y mantener ahorro de emergencia.
```

------------------------------------------------------------------------

# 37. Objetivo académico

El sistema debe poder demostrarse como un proyecto de Ingeniería de
Software con:

-   requisitos;
-   análisis;
-   diseño;
-   arquitectura;
-   modelo de datos;
-   interfaz;
-   lógica de negocio;
-   pruebas;
-   componente de IA;
-   trazabilidad;
-   gestión financiera;
-   control financiero;
-   documentación.

No debe quedar como una simple interfaz de formularios.

------------------------------------------------------------------------

# 38. Próximo paso inmediato

Los **siete formularios de deuda ya están implementados** (hipotecario,
tarjeta, vehículo, educativo, libre inversión, préstamo personal y
consumo), cada uno en su propio módulo dentro de `deudas/` y
registrados en `deudas/__init__.py` mediante `TIPOS_DEUDAS`.

Pendiente dentro de tarjeta de crédito: el flujo de "agregar compra
asociada a una tarjeta existente" (sección 16) y el manejo del ciclo de
facturación según corte/pago (sección 18) aún no están confirmados como
completos; verificar antes de darlos por cerrados.

El siguiente trabajo según el orden de la sección 32 es:

## Centralizar "Mis deudas"

-   Unificar la presentación de los siete tipos de deuda en una sola
    sección `Mis deudas` (ver formato de ejemplo en la sección 12).
-   Reutilizar los datos ya guardados en `st.session_state.deudas` sin
    duplicar lógica de formato entre tipos de deuda.
-   Mantener el ícono, etiquetas y formato monetario específicos de
    cada tipo de deuda.

No modificar los formularios ya implementados salvo que aparezca un
error.

------------------------------------------------------------------------

# 39. Principio general

La aplicación no debe ser solamente:

> "Un formulario que guarda deudas."

Debe evolucionar a:

> **Un sistema inteligente de gestión y control financiero personal que
> estructura la información económica del usuario, calcula indicadores
> financieros, identifica riesgos y genera recomendaciones
> personalizadas mediante reglas de negocio y técnicas de Inteligencia
> Artificial.**
