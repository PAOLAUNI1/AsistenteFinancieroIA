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

**Actualización:** el proyecto ya tiene un backend (FastAPI + MySQL) y una
app Android nativa (Kotlin + Jetpack Compose, marca **FinZen IA**) que lo
consume. Ver las secciones 40 a 46. El prototipo Streamlit se conserva
como referencia de las reglas de negocio.

------------------------------------------------------------------------

## 3. Tecnología actual

> Esta sección describe el **prototipo Streamlit**. El backend y la app
> Android están descritos en las secciones 40 a 46.

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

**Estado actual:** la persistencia ya está implementada en el backend con
**MySQL** (base `asistente_financiero`) mediante SQLAlchemy; ver la
sección 41. El prototipo Streamlit sigue usando `st.session_state`.

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
9.  ✅ Centralizar Mis deudas (en la app Android: sección "Mis deudas" del
    Inicio; falta la pantalla "Ver todas").
10. ✅ Persistencia (MySQL, sección 41).
11. Registro de pagos y movimientos.
12. Cálculo de endeudamiento.
13. Análisis de sobreendeudamiento.
14. Motor de recomendaciones.
15. IA personalizada.
16. Alertas y vencimientos.
17. Pruebas.
18. ⏳ Preparación Android (en curso: la app ya existe, sección 42).
19. Documentación del trabajo de grado.

**Estado de los siete formularios en la app Android (paso actual):**
hipotecario ✅, tarjeta de crédito ✅, crédito de vehículo ✅, educación ✅,
otros ✅; pendiente en la app: consumo (el endpoint ya existe). Libre
inversión y préstamo personal no se muestran en la app. Ver la sección 38.

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

Los **siete formularios de deuda** existen en el prototipo Streamlit
(`deudas/`) y los **ocho endpoints** existen en el backend. En la **app
Android** hay cinco flujos completos: hipotecario, tarjeta de crédito,
vehículo, educación y otros.

El siguiente trabajo es:

## 1. Completar el flujo de deuda que falta en la app

Consumo. Para él (y para cualquier otro tipo nuevo):

-   Recibir el diseño (mockup) del equipo y seguirlo pantalla por
    pantalla (sección 44).
-   Ajustar el backend solo si el diseño no pide algo que hoy es
    obligatorio, o pide algo que no se guarda (patrón usado en
    hipotecario, tarjeta y vehículo).
-   Verificar en el emulador y contra MySQL antes de darlo por cerrado.

## 2. Pendientes ya identificados

-   Tarjeta de crédito: "agregar compra a una tarjeta existente"
    (secciones 16 y 17; la tabla `compras_tarjeta` existe pero no hay
    endpoint ni pantalla) y el ciclo de facturación según corte/pago
    (sección 18). **No están hechos.**
-   Pago mínimo de la tarjeta: el diseño no lo pide, por eso hoy la
    tarjeta queda sin cuota y no aparece en "Próximos pagos" ni suma al
    análisis mensual. Decidir si se pide más adelante (etapa de pagos) o
    si se estima.
-   Pantalla "Mis deudas" completa ("Ver todas") y calendario de pagos.
-   Registrar gasto, registrar ahorro y "Analizar con IA".
-   Camino para que los usuarios antiguos sin contraseña la definan.
-   Renovación de tokens.

No modificar los flujos ya implementados salvo que aparezca un error o
el diseño cambie.

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

------------------------------------------------------------------------

# 40. Arquitectura actual: backend + app Android

``` text
App Android (FinZen IA)  --HTTP/JSON-->  Backend FastAPI  -->  MySQL
Kotlin + Jetpack Compose                 routers -> services    asistente_financiero
                                         -> models (SQLAlchemy)
```

Hay dos repositorios de trabajo:

-   **Backend** (este repositorio, carpeta `backend/`): FastAPI,
    SQLAlchemy 2, PyMySQL, Pydantic v2, bcrypt, pytest. Rama de trabajo:
    `DEV` (remoto `origin`).
-   **App Android**: `C:\Users\windows\AndroidStudioProjects\FrontAppIA`
    (todavía **no está en git**). Kotlin 2.2.10, AGP 9.3.3, Compose BOM
    2026.02.01, Retrofit 3.0.0 + kotlinx-serialization 1.9.0, `minSdk`
    24, `compileSdk`/`targetSdk` 37, paquete `com.example.frontappia`.
    Marca visible: **FinZen IA**.

La separación "orquestador / servicio de datos" se mantiene de forma
**lógica** dentro de un solo proceso: los routers orquestan y los
services + models hablan con la base de datos.

El prototipo Streamlit (`app.py`, `deudas/`, `modelo.py`,
`recomendaciones.py`) no se modifica: sigue siendo la referencia de las
reglas de negocio.

------------------------------------------------------------------------

# 41. Backend (carpeta `backend/`)

## Estructura

``` text
backend/
├── main.py            # FastAPI + routers + formato del 422 (sin eco del valor recibido)
├── database.py        # engine MySQL (credenciales en bd.env)
├── deps.py            # usuario_actual (lee el token Bearer)
├── models.py          # modelos SQLAlchemy (+ DETALLE_POR_TIPO: tabla de detalle de cada tipo)
├── tiempo.py          # ahora_utc() para lo guardado y hoy_colombia() para "hoy" (America/Bogota)
├── routers/           # usuarios, catalogos, deudas, perfil, analisis (solo traducen HTTP)
├── schemas/           # contratos Pydantic (usuario, deuda, perfil, analisis, catalogo)
├── services/          # reglas: deudas, repositorio_deudas, perfil, analisis, moneda, seguridad, tokens, limite_intentos
├── tests/             # pytest (241 pruebas)
└── postman/           # colección AsistenteFinancieroIA.postman_collection.json
db/
├── schema.sql         # estructura de las 14 tablas (generada desde la base real)
└── seed.sql           # catálogos: tipos de deuda y categorías de gasto
Dockerfile, .dockerignore, bd.env.example   # despliegue y configuración
backend/requirements.txt (versiones fijas, para ejecutar) y requirements-dev.txt (más pytest y httpx)
```

## Base de datos

MySQL, base `asistente_financiero`, 14 tablas: `usuarios`, `deudas`,
`deuda_tarjeta`, `deuda_vehiculo`, `deuda_educativo`, `deuda_otro`,
`compras_tarjeta`, `pagos_deuda`, `ingresos`, `gastos`, `categorias_gasto`,
`metas_ahorro`, `aportes_meta`, `tipos_deuda`.

-   `deudas` es la tabla base común a los siete tipos; `deuda_tarjeta`,
    `deuda_vehiculo` y `deuda_educativo` guardan el detalle propio de
    cada tipo (relación 1:1).
-   Columnas agregadas a `deudas` durante el desarrollo de la app:
    `nombre`, `fecha_inicio`, `descripcion` (se ejecutó `ALTER TABLE` en
    la base de desarrollo).
-   `tipos_deuda` tiene ocho códigos: `HIPOTECARIO`, `TARJETA`,
    `VEHICULO`, `EDUCATIVO`, `LIBRE_INVERSION`, `PRESTAMO_PERSONAL`,
    `CONSUMO` y `OTRO` ("Otras deudas", con su detalle en `deuda_otro`).
    La app solo ofrece seis: hipotecario, tarjeta, consumo, vehículo,
    educación y otro (el diseño no muestra libre inversión ni préstamo
    personal; sus endpoints siguen existiendo).
-   Las credenciales viven en `bd.env` (`DB_HOST`, `DB_PORT`,
    `DB_NAME`, `DB_USER`, `DB_PASSWORD`), que **no se sube a git**.
-   **Crear una base nueva:** `db/schema.sql` (estructura con todas las
    restricciones) y luego `db/seed.sql` (catálogos); verificado sobre una
    base vacía: 14 tablas, 8 tipos de deuda y 8 categorías. Si la
    estructura cambia, se regeneran con `mysqldump --no-data` (ver cómo en
    el historial del proyecto) y se actualizan los modelos a mano.

## Endpoints

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/health` | Estado del servicio |
| POST | `/usuarios` | Registro (exige aceptar términos y tratamiento de datos); devuelve el usuario y su `token` |
| POST | `/usuarios/login` | Inicio de sesión con contraseña; devuelve el usuario y su `token` |
| GET | `/usuarios/me` | El usuario dueño del token |
| GET | `/tipos-deuda`, `/categorias-gasto` | Catálogos |
| GET | `/deudas` | Deudas del usuario |
| POST | `/deudas/{hipotecario,tarjeta,vehiculo,educativo,libre_inversion,prestamo_personal,consumo,otros}` | Registrar deuda de cada tipo |
| DELETE | `/deudas/{id}` | Eliminar deuda |
| GET/PUT | `/perfil` | Ingresos, gastos y datos familiares |
| GET/PUT | `/meta-ahorro` | Meta de ahorro |
| POST | `/analisis` | Resumen financiero (ingresos, gastos, disponible, deuda) |

**Autenticación:** los endpoints de datos (`/deudas`, `/perfil`,
`/meta-ahorro`, `/analisis`, `/usuarios/me`) exigen
`Authorization: Bearer <token>` y solo devuelven datos del dueño del token.
El token es un JWT (HS256) firmado con la variable de entorno `JWT_SECRET`
(con `APP_ENV=production` es obligatoria y de 32 caracteres o más, si no el
servidor no arranca; fuera de producción, si falta, se genera una clave
temporal y las sesiones se pierden al reiniciar) y dura `JWT_DIAS` días (30 por defecto). Sin token, con token
alterado, vencido o sin vencimiento: 401; cuenta inactiva: 403. Ya no existe
el parámetro `usuario_id` ni el listado público de usuarios. Los tests usan
un cliente que convierte `params={"usuario_id": ...}` en el token de ese
usuario (`backend/tests/conftest.py`) y `test_autenticacion.py` cubre los
casos de seguridad. El inicio de sesión se bloquea con 429 (y `Retry-After`)
tras 5 contraseñas incorrectas por correo o 20 por IP en 15 minutos
(`services/limite_intentos.py`, en memoria: con varios procesos cada uno
llevaría su cuenta). Cada 401 se crea por petición (`deps._no_autorizado`).

## Reglas relevantes

-   Contraseña: de 8 a 72 bytes, guardada con **bcrypt**
    (`BCRYPT_ROUNDS`; las pruebas usan 4). Login: 200 si es correcto, 401
    (mismo mensaje para correo o contraseña incorrectos), 403 si la
    cuenta no está activa.
-   Estados de una deuda: `ACTIVA`, `PAGADA`, `CANCELADA`. Si el
    registro llega con `activa=false` queda `CANCELADA` y no cuenta en el
    análisis.
-   `cuotas_pendientes = plazo_meses - proxima_cuota + 1`. La app envía
    `cuota_proxima = cuotas_pagadas + 1`.
-   **Hipotecario / vehículo:** aceptan `nombre`, `fecha_inicio`,
    `descripcion`, `activa`; la fecha de inicio no puede ser posterior al
    próximo pago. Vehículo guarda `tipo_vehiculo = "OTRO"` cuando no se
    indica.
-   **Tarjeta:** `pago_minimo`, `cuota_manejo`, `franquicia` y
    `proximo_pago` son opcionales. Si no llega `proximo_pago`, se calcula
    con `dia_pago` (función `proxima_fecha_de_pago`, ajustada al último
    día del mes). Sin pago mínimo, `valor_cuota` queda nulo.
    Validaciones: saldo > 0, saldo <= cupo.
-   `saldo_actual` de las deudas con cuotas no puede superar el monto
    inicial (también en consumo y préstamo personal).
-   **Límites de entrada** (`schemas/`, alineados con las columnas de MySQL
    para que un dato fuera de rango dé 422 y no un 500): montos hasta
    `MAX_MONTO` (9.999.999.999.999), tasa hasta 100 y redondeada a 4
    decimales, años hasta 40, hijos hasta 30, `Infinity`/`NaN` rechazados y
    `max_length` en los textos (entidad 100, prestamista 60, artículo 30,
    etc.). Si MySQL aún rechaza el dato (`DataError`/`IntegrityError`), se
    hace rollback y se responde 422. El cuerpo del 422 solo trae `loc`, `msg`
    y `type`: nunca el valor recibido (podría ser una contraseña).
-   **Registro:** el router distingue `TerminosNoAceptados` (422) y
    `CorreoDuplicado` (409); un registro simultáneo con el mismo correo
    también da 409.
-   **Esquema de la base:** se crea solo con `db/schema.sql` + `db/seed.sql`.
    La aplicación ya no ejecuta `create_all` al arrancar (no crea los CHECK
    ni los catálogos y sus tipos de clave no coinciden); solo lo usan las
    pruebas, sobre SQLite.

## Cómo ejecutar y probar

``` bash
pip install -r backend/requirements-dev.txt   # para solo ejecutar basta requirements.txt
python -m uvicorn backend.main:app --port 8000
python -m pytest backend/tests -q
```

Configuración (variables de entorno o `bd.env`, ver `bd.env.example`):
`DB_HOST/DB_PORT/DB_NAME/DB_USER/DB_PASSWORD` en local, o `DATABASE_URL`
(`mysql://usuario:clave@host:puerto/base`) en un servidor en la nube;
`JWT_SECRET` (obligatoria con `APP_ENV=production`, de 32 caracteres o más; el
Dockerfile ya fija `APP_ENV`); opcionales `JWT_DIAS` y
`BCRYPT_ROUNDS`. El `Dockerfile` arranca con `uvicorn` en el puerto `$PORT`,
con un usuario sin privilegios y un `HEALTHCHECK` sobre `/health` (no se pudo
probar localmente: no hay Docker instalado).

La documentación interactiva queda en `/docs`. Las pruebas usan SQLite
en memoria con los catálogos sembrados, sin tocar MySQL.

------------------------------------------------------------------------

# 42. App Android (FinZen IA)

## Flujos construidos

1.  **Bienvenida** → "Crear mi cuenta" o "Iniciar sesión".
2.  **Registro** (2 pasos): datos personales (nombre, correo,
    contraseña, cantidad de hijos) y permisos (términos y tratamiento de
    datos, ambos obligatorios) → Cargando → Éxito. Llama a
    `POST /usuarios`.
3.  **Inicio de sesión**: correo y contraseña reales (`POST
    /usuarios/login`).
4.  **Inicio**: saludo, balance del mes (ingresos, gastos, disponible,
    ahorro), acciones rápidas, **Mis deudas** (hasta 3), **Próximos
    pagos** (hasta 3) y barra inferior. Los botones de pantallas aún no
    construidas muestran "Próximamente".
5.  **Registrar deuda**: lista de tipos (desde `/tipos-deuda`) y el flujo
    de cada tipo; ver la tabla siguiente.
6.  **Detalle de la deuda**.

La sesión vive **solo en memoria** (decisión del usuario): al cerrar la
app siempre se abre en Bienvenida. El token de la sesión (`SesionToken`) también
está solo en memoria y un interceptor de OkHttp lo envía como `Bearer` en cada
llamada. Si el servidor responde 401 en una llamada con sesión (token vencido o
servidor reiniciado con otra clave) la app muestra "Tu sesión venció" y vuelve
a Bienvenida; en el inicio de sesión un 401 sigue significando "correo o
contraseña incorrectos".

## Flujos de registro de deuda

| Tipo | Pasos | Particularidades |
|------|-------|------------------|
| Hipotecario | Básica → Pago → Adicional → Confirmar | El saldo no se pide: se estima por amortización (EA). Detalle con avance por cuotas |
| Tarjeta de crédito | Entidad (lista con buscador) → Datos → Adicional → Confirmar | Tasa mensual; día de corte y de pago con selector de día; no pide pago mínimo ni franquicia. Detalle sin cuotas; fila de Inicio con barra de uso, límite y disponible |
| Vehículo | Básica (entidad en lista desplegable) → Pago → Adicional → Confirmar | El saldo lo escribe la persona; periodicidad de la cuota solo "Mensual"; próxima fecha de pago en el paso 2 |
| Educación | Básica (entidad educativa, programa, monto, saldo, tasa, plazo en meses) → Pago → Adicional → Confirmar | Tasa 0 por defecto; plazo total en meses y cuotas pagadas |
| Otros | Básica (entidad o persona, tipo de otro crédito) → Pago → Adicional → Confirmar | Tipo nuevo `OTRO`; el subtítulo muestra "Juan Pérez (familiar)" |

La lista de tipos de la app muestra solo seis, en este orden: Hipotecario,
Tarjeta de crédito, Consumo, Vehículo, Educación y Otro. **Consumo** aún no
tiene flujo en la app (muestra "Próximamente"); libre inversión y préstamo
personal no se ofrecen en la app.

Pantalla de confirmación → "Registrando…" → éxito → "Ir a mis deudas"
(abre el detalle) o "Volver al inicio".

## Estructura del código (`app/src/main/java/com/example/frontappia/`)

``` text
MainActivity.kt
data/            # Modelos, repositorios (Usuario, Finanzas, Deudas), ejecutarApi
data/remote/     # Retrofit: ApiClient, *Api, *Dtos (snake_case con @SerialName)
ui/              # FinZenApp (navegación por enum Pantalla), FinZenViewModel, Mensajes
ui/components/   # campos y botones comunes (dinero, fecha, día, lista, contraseña)
ui/registro/     # bienvenida, datos personales, permisos, cargando, éxito
ui/login/        # inicio de sesión
ui/home/         # Inicio, componentes, formatos
ui/deuda/        # un archivo de formulario + pasos + confirmación por tipo,
                 # RegistroDeudaFlow, TipoDeudaScreen, Detalle*
ui/theme/        # colores y tipografía
```

-   Un único `FinZenViewModel` con `StateFlow` para usuario, registro,
    login, Inicio, tipos, formularios (uno por tipo de deuda), registro
    de deuda y deuda seleccionada.
-   Los formularios guardan texto tal cual lo escribe la persona; los
    cálculos y validaciones convierten al vuelo (reflejan las reglas del
    backend).
-   Los errores de red se traducen en `ErrorApi` (conflicto, no
    encontrado, datos inválidos, credenciales, cuenta inactiva, sin
    conexión).
-   El flujo de deudas usa `TipoFlujo` (Hipoteca, Tarjeta, Vehiculo,
    Educativo, Otros) para saber a qué pantalla volver y qué enviar.

## Compilar y ejecutar

-   `JAVA_HOME` = JDK que trae Android Studio (carpeta `jbr`).
-   `gradlew.bat :app:testDebugUnitTest :app:assembleDebug`
-   La URL del servidor se fija al compilar: por defecto
    `http://127.0.0.1:8000/`; para un servidor compartido,
    `gradlew assembleDebug -PapiBaseUrl=https://mi-servidor.example.com/`.
-   `API_BASE_URL` de depuración por defecto: `http://127.0.0.1:8000/` con
    `adb reverse tcp:8000 tcp:8000` (en el emulador o en el celular);
    hay una `network_security_config` solo para depuración que permite
    HTTP a `127.0.0.1`, `localhost` y `10.0.2.2`.
-   Para otro puerto del backend: `adb reverse tcp:8000 tcp:<puerto>`.

------------------------------------------------------------------------

# 43. Trabajo con diseños (mockups) del equipo

-   Los diseños llegan como imágenes de flujo de 10 pantallas. **Se
    siguen fielmente** (textos, orden de campos, colores).
-   Si el diseño **no pide** un dato que el backend exige, se hace
    opcional en el backend con un valor por defecto razonable y se
    documenta aquí (ejemplos: pago mínimo y franquicia de la tarjeta,
    tipo de vehículo).
-   Si el diseño **pide** algo que no se guarda, se agrega la columna
    (ejemplos: `nombre`, `fecha_inicio`, `descripcion`).
-   Las listas de entidades financieras llevan **solo nombres, sin
    logos** (decisión del usuario). "Otra entidad" abre un campo de
    texto.
-   Los porcentajes de tasa se muestran con dos decimales en vehículo y
    tarjeta (`14,50%`).
-   La fila de "Mis deudas" muestra "Saldo actual" (diseño más reciente)
    para las deudas con cuotas y una barra de uso del cupo para tarjetas.
-   Cada flujo se verifica en el emulador contra MySQL real y se limpia
    **solo** el usuario de prueba propio (nunca los usuarios reales del
    equipo).

------------------------------------------------------------------------

# 44. Pruebas

-   Backend: 241 pruebas de pytest (`backend/tests`): servicios de
    deudas, endpoints, registro, login, aislamiento por usuario y
    `test_registro_por_tipo.py`, que prueba los ocho tipos de deuda con los
    mismos casos (registro, saldo/cuotas/fechas inválidas, inactiva, borrado,
    aislamiento) y `test_mensajes_validadores.py`, que fija el texto exacto de
    cada error de validación (la app los muestra tal cual: cualquier cambio en
    los validadores debe mantenerlos).
-   App: 110 pruebas unitarias (`app/src/test`): validaciones, formularios
    (hipotecario, tarjeta, vehículo), contratos JSON con el backend,
    repositorios, formatos de moneda y fecha.
-   Verificación visual: emulador `Medium_Phone` y celular Xiaomi
    (instalación vía USB). Cada flujo nuevo se recorre completo hasta
    "Mis deudas".

------------------------------------------------------------------------

# 45. Entorno de desarrollo (máquina de Juan)

-   Python 3.14 y MySQL 8 instalados localmente; ninguno está en el
    `PATH`.
-   `adb` en `...\Android\Sdk\platform-tools`, emulador en
    `...\Android\Sdk\emulator` (AVD `Medium_Phone`).
-   El Xiaomi necesita "Instalar vía USB" habilitado.
-   Detalles del emulador al automatizar pruebas: `adb input text` no
    escribe tildes y a veces duplica teclas; el arranque en frío de la
    app es lento, por lo que conviene avanzar paso a paso.

------------------------------------------------------------------------

# 46. Pendientes transversales

-   **Servidor compartido** (en curso): el backend ya está preparado para la
    nube (tokens, `DATABASE_URL`, `JWT_SECRET`, `Dockerfile`, `db/*.sql`).
    Falta elegir el proveedor, crear la cuenta, desplegar, cargar
    `db/schema.sql` y `db/seed.sql`, y compilar el APK con
    `-PapiBaseUrl=https://...` para repartirlo (Firebase App Distribution,
    app `com.example.frontappia`). Mientras no exista, el APK apunta a
    `127.0.0.1` y solo funciona con el backend del propio PC.
-   Camino para definir contraseña a usuarios anteriores (ids 9, 10, 12).
-   Registro de pagos y movimientos (alimenta el pago mínimo de tarjetas,
    el saldo real y los vencimientos).
-   Cálculo de endeudamiento y sobreendeudamiento, motor de
    recomendaciones, IA personalizada, alertas y vencimientos (pasos 12 a
    16 de la sección 32).
-   Poner la app Android bajo control de versiones.
-   **Pendientes de la revisión de código de octubre 2026** (rama `DEV`).
    Resueltos: validaciones de entrada, `JWT_SECRET`, `create_all`, 401,
    errores de registro, límite de login, fecha de pago de la tarjeta con
    la zona `America/Bogota` (`tiempo.py`), Dockerfile (usuario sin
    privilegios, versiones fijas, `HEALTHCHECK`), calidad del backend
    (persistencia en `services/repositorio_deudas.py` con listado sin N+1, ocho
    endpoints `POST /deudas/*` generados desde `ESQUEMAS_POR_TIPO` y
    `VALIDADORES_POR_TIPO`, base común `_base_deuda`/`_base_credito` en los
    validadores, `/analisis` con `response_model`, pruebas por tipo),
    contrato antiguo de educación eliminado (`plazo_meses` es obligatorio) y,
    en la app, plazo máximo de 40 años y mensaje propio ante el 429.
    Siguen abiertos:
    -   Conexión a MySQL: sin TLS y con `root` sin contraseña por defecto si
        faltan las variables (necesario resolver con el servidor compartido).
    -   Dinero como `float` en schemas y servicios: pasar a `Decimal` antes
        del registro de pagos.
    -   Los validadores aún repiten las comprobaciones (entidad, saldo,
        cuotas) con textos distintos por tipo; unificarlos cambiaría los
        mensajes de error.
