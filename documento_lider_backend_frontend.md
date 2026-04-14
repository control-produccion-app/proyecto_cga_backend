# Control de Producción y Gestión Alimenticia
## Documento líder de traspaso técnico para Backend y Frontend

**Versión:** v1  
**Objetivo:** documento guía maestro para que Backend y Frontend puedan diseñar, implementar y validar el sistema con apoyo de IA sin perder el contexto real del negocio.  
**Estado actual:** base de datos relacional ya modelada y probada en PostgreSQL; dataset de prueba cargado; consultas de validación ya ejecutadas; una función útil en PL/pgSQL ya definida (`fn_stock_insumo_fecha`).  
**Tecnologías objetivo actuales:** PostgreSQL + Django/Python (backend API) + Angular (frontend).

---

## 1. Propósito del documento

Este documento cumple cuatro funciones al mismo tiempo:

1. **Concentrar el contexto real del negocio** en un solo lugar.
2. **Traducir la base de datos a lenguaje funcional** para que backend entienda qué debe implementar.
3. **Dar una guía clara a frontend** sobre qué módulos y datos deben mostrarse.
4. **Servir como insumo para una IA** que ayude a construir backend o frontend sin inventar requisitos fuera del alcance actual.

Este documento debe leerse junto al script SQL canónico del proyecto, que es el anexo técnico principal y representa la verdad estructural actual del sistema.

---

## 2. Problema que resuelve el sistema

Hoy el negocio opera con un Excel que funciona como registro operativo y visual principal del administrador. Ese Excel concentra información que en la práctica mezcla:

- fecha
- cliente
- producto
- precio
- kilos o cantidad
- venta
- cancelación
- deuda / saldo pendiente
- seguimiento diario del negocio

El problema del escenario actual no es solo “guardar datos”, sino que el control diario depende de una herramienta manual que:

- obliga a consolidar información a mano
- dificulta la trazabilidad
- mezcla cálculo con registro
- vuelve más lento detectar deudas, producción o stock
- no escala bien cuando hay más jornadas, clientes o movimientos

La nueva solución **no debe alejarse de lo que el administrador ya mira a diario**. Debe conservar la utilidad operativa del Excel, pero con una base de datos sólida, consultas reutilizables, backend estructurado y frontend claro.

---

## 3. Visión funcional del sistema

El sistema debe permitir que el administrador tenga en una aplicación web una vista centralizada de:

- producción diaria por jornada y turno
- stock y movimientos de bodega
- pedidos y despacho a clientes
- cobros y saldos pendientes
- reportes equivalentes o superiores a los que hoy se obtienen en Excel

La idea no es construir un ERP gigante. El objetivo es un sistema académico, realista y defendible, centrado en la operación diaria de una panadería con foco en control.

---

## 4. Arquitectura objetivo

### 4.1 Componentes

- **Base de datos:** PostgreSQL
- **Backend:** Django / Python
- **Frontend:** Angular
- **Integración esperada:** el frontend consume API del backend; el frontend no se conecta directamente a PostgreSQL.

### 4.2 Regla de separación de responsabilidades

#### Base de datos
Responsable de:
- persistencia
- integridad relacional
- restricciones
- vistas útiles
- funciones de apoyo
- lógica sensible y reusable en PL/pgSQL

#### Backend
Responsable de:
- exponer endpoints
- orquestar casos de uso
- validar entradas
- aplicar reglas de negocio no visuales
- servir datos listos para frontend
- llamar a consultas, vistas o funciones de la BD cuando corresponda

#### Frontend
Responsable de:
- mostrar información
- capturar datos del administrador
- filtrar, ordenar y navegar
- presentar reportes y resúmenes de forma legible
- nunca concentrar la lógica principal del negocio

---

## 5. Usuarios y actores

### 5.1 Administrador
Es el usuario principal del sistema.  
En la práctica, es quien hoy revisa y utiliza el Excel como vista diaria del negocio.

Debe poder:
- ver el estado diario
- registrar o consultar producción
- revisar stock
- revisar pedidos y despachos
- revisar cobros y saldos
- consumir reportes

### 5.2 Encargado de turno
No necesariamente será usuario intensivo del sistema.  
Su información puede ser traspasada al administrador.

### 5.3 Repartidor / distribución
En el negocio real, importa más el nombre del repartidor que una “ruta formal”.  
Por eso el modelo actual usa distribución asociada a nombres como Ricardo, Osvaldo o retiro en panadería.

### 5.4 Cliente
No usa el sistema directamente en esta etapa, pero es una entidad central para:
- pedidos
- despacho
- descuento
- pagos
- saldo pendiente

---

## 6. Alcance funcional actual

### 6.1 Lo que sí cubre el modelo actual

- clientes
- productos
- tipos de producción
- jornadas
- turnos
- pedidos
- detalle de pedidos
- producción
- movimientos de bodega
- conteos de bodega
- detalle de despacho / movimiento comercial
- vistas de venta y saldo
- una función PL/pgSQL para stock por fecha

### 6.2 Lo que no debe asumirse todavía

- facturación tributaria real
- boletas o documentos fiscales
- multi-sucursal avanzada
- permisos complejos por múltiples roles
- integración con pagos electrónicos
- aplicación móvil específica
- analítica avanzada o predicción

---

## 7. Reglas de negocio consolidadas

### 7.1 Producción

Un día normal se piensa con tres turnos o jornadas internas:

- Madrugada
- Mañana
- Tarde

En el dataset de prueba se usó una lógica diaria de tres turnos para poder probar consultas por día, turno y acumulado.

### 7.2 Tipos de producción

El sistema maneja tres grupos principales:

- **Pan corriente**
- **Pan integral**
- **Pan especial**

### 7.3 Productos base del sistema actual

#### Pan corriente
- Hallulla
- Batido
- Colisa

#### Pan integral
- Bollo integral
- Molde integral

#### Pan especial
- Frica
- Completo
- Colisa especial

### 7.4 Unidades de venta

El modelo ya fue ajustado para soportar ventas por peso y por cantidad.

#### Pan corriente
- principalmente por kilo
- puede existir venta puntual por unidad

#### Pan especial
- se trabaja por kilo en el estado actual consolidado del proyecto

#### Pan integral
- Bollo integral: por kilo
- Molde integral: por unidad

### 7.5 Descuentos

- El descuento siempre se modela como **porcentaje**
- No se mezcla IVA con descuento
- Los porcentajes de ejemplo ya usados en la base son principalmente 0% y 5%

### 7.6 Precios base confirmados por la panadería

#### Por kilo
- Pan corriente: **2390 CLP/kg**
- Pan especial: **2690 CLP/kg**
- Pan integral: **3100 CLP/kg**

#### Por unidad
Algunos productos unitarios se cargaron con valores ficticios coherentes para pruebas porque aún no se definieron de manera oficial en el negocio. Backend debe considerar estos valores como **temporales de prueba**, no definitivos de producción real.

### 7.7 Bodega

El modelo deja preparada la posibilidad de:
- ENTRADA
- SALIDA
- AJUSTE

Para el dataset de prueba actual se simplificó la lógica de stock para facilitar validaciones, pero el modelo quedó listo para soportar reabastecimiento futuro.

### 7.8 Dinero y reportes

A nivel de almacenamiento, los montos se guardan como numéricos.  
A nivel de consultas y reportes, todos los montos deben mostrarse como **CLP legible**, con:

- signo $
- separador de miles
- sin decimales innecesarios

Esta regla es importante para frontend y reportes del backend.

### 7.9 Saldo

El saldo representa **lo que todavía falta pagar**.

Fórmula base:
- saldo = venta - cancelación / pago

En el proyecto existen dos niveles:
- saldo del día
- saldo acumulado por cliente

---

## 8. Módulos funcionales del sistema

### 8.1 Dashboard

#### Objetivo
Entregar al administrador una vista rápida del estado del día o período.

#### Información esperada
- ventas del día
- pagos del día
- saldo pendiente total
- producción por turno
- stock actual de insumos clave
- clientes con mayor deuda
- alertas simples

#### Backend debe entregar
- resumen diario
- resumen por cliente
- resumen por turno
- resumen de stock

#### Frontend debe mostrar
- tarjetas KPI
- tabla resumida
- filtros por fecha
- acceso rápido a módulos operativos

---

### 8.2 Producción

#### Objetivo
Registrar y consultar cuánto se produjo por jornada, turno y tipo de producción.

#### Datos principales
- jornada
- turno
- tipo de producción
- quintales

#### Backend debe permitir
- crear registros de producción
- consultar producción por día
- consultar producción por turno
- consultar producción por tipo

#### Frontend debe mostrar
- formulario de registro
- historial filtrable
- tablas y resúmenes

---

### 8.3 Bodega

#### Objetivo
Controlar movimientos y stock de insumos.

#### Datos principales
- insumo
- tipo de movimiento
- fecha
- cantidad
- jornada / turno opcional
- conteo físico

#### Backend debe permitir
- registrar salida
- registrar entrada
- registrar ajuste
- consultar stock por fecha
- consultar historial de movimientos

#### Frontend debe mostrar
- stock actual
- historial por insumo
- conteos de bodega
- alertas si el stock es bajo o inconsistente

---

### 8.4 Pedidos y despacho

#### Objetivo
Registrar qué pidió un cliente, por qué medio se distribuye y qué se entregó realmente.

#### Datos principales
- cliente
- distribución
- fecha de pedido
- fecha de entrega
- producto
- cantidad solicitada
- unidad
- precio
- descuento

#### Backend debe permitir
- registrar pedido
- registrar detalle del pedido
- consultar pedidos por día
- consultar pedidos por cliente
- consultar pedidos por repartidor

#### Frontend debe mostrar
- listado de pedidos
- detalle de cada pedido
- filtros por cliente, fecha y repartidor

---

### 8.5 Clientes y saldos

#### Objetivo
Controlar venta, pago y deuda pendiente.

#### Datos principales
- cliente
- venta acumulada
- pago acumulado
- saldo

#### Backend debe permitir
- consultar saldo acumulado por cliente
- consultar resumen diario por cliente
- consultar pagos realizados

#### Frontend debe mostrar
- clientes con mayor saldo pendiente
- detalle por cliente
- vistas tipo reporte similares a Excel

---

### 8.6 Reportes

#### Objetivo
Replicar y mejorar la utilidad operativa del Excel.

#### Reportes clave
- ventas por cliente
- saldo acumulado
- producción por turno
- stock por fecha
- consumo de insumos
- productos más vendidos
- despachos por repartidor

#### Regla de presentación
Todos los montos monetarios deben formatearse como CLP legible.

---

## 9. Modelo de datos actual explicado

### 9.1 jornada_diaria
Representa cada día operativo del sistema.

### 9.2 turno
Catálogo de turnos. Actualmente:
- Madrugada
- Mañana
- Tarde

### 9.3 distribucion
Catálogo de forma de despacho o encargado de distribución.  
Se modela con el nombre que el negocio reconoce operativamente.

### 9.4 insumo
Catálogo de insumos controlados por bodega.

Campos importantes:
- nombre
- unidad de control
- stock inicial / sugerido
- activo

### 9.5 tipo_produccion
Agrupa el tipo de pan o línea productiva:
- corriente
- integral
- especial

### 9.6 producto
Producto concreto que se vende.

Campos importantes:
- nombre
- precio sugerido
- unidad_venta_base
- tipo de producción asociado

### 9.7 cliente
Cliente del negocio.

Campos importantes:
- RUT
- DV
- nombre
- ciudad
- dirección
- teléfono
- descuento aplicado

### 9.8 pedido
Cabecera del pedido.

### 9.9 detalle_pedido
Líneas del pedido.

Puntos importantes:
- soporta cantidad
- soporta unidad de medida
- soporta precio cobrado
- soporta descuento por línea

### 9.10 produccion
Registro de producción por jornada, turno y tipo de producción.

### 9.11 movimiento_bodega
Registro de entradas, salidas y ajustes de insumos.

### 9.12 conteo_bodega
Conteo físico para control o contraste.

### 9.13 detalle_movimiento
Es la tabla comercial más importante del sistema en esta etapa.

Representa lo efectivamente entregado o registrado para cliente y permite calcular:
- venta
- pago
- saldo

Puntos clave:
- soporta cantidad_entregada
- soporta unidad_medida
- soporta cancelación
- soporta descuento por línea

---

## 10. Objetos de apoyo ya disponibles en la base de datos

### 10.1 Vista `vw_resumen_cliente_dia`
Resume por día y cliente:
- venta del día
- pago del día
- saldo del día

### 10.2 Vista `vw_saldo_acumulado_cliente`
Acumula el saldo por cliente a partir del resumen diario.

### 10.3 Función `fn_stock_insumo_fecha`
Función PL/pgSQL ya creada para obtener stock de un insumo hasta una fecha dada.

#### Utilidad
- validaciones
- reportes
- backend
- futura lógica de stock negativo

---

## 11. Lógica PL/pgSQL actual y backlog inmediato

### 11.1 Hecho
- `fn_stock_insumo_fecha`

### 11.2 Próximo backlog recomendado, pero no obligatorio para comenzar backend
1. Trigger que impida stock negativo
2. Trigger que impida cancelación mayor que venta
3. Función de rinde ideal de pan corriente
4. Procedimiento de cierre de jornada

### 11.3 Criterio de prioridad
Backend puede arrancar ya con la base actual.  
Las piezas PL siguientes deben entrar como mejora controlada, no como requisito bloqueante.

---

## 12. Qué debe hacer el backend

### 12.1 Responsabilidad general
Backend debe transformar la estructura de BD en casos de uso comprensibles para frontend.

### 12.2 Casos de uso mínimos

#### Dashboard
- obtener resumen diario
- obtener saldo acumulado por cliente
- obtener stock actual

#### Producción
- registrar producción
- consultar producción por jornada
- consultar producción por turno
- consultar producción por tipo

#### Bodega
- registrar movimiento de bodega
- consultar stock por fecha
- consultar historial por insumo
- consultar conteos físicos

#### Pedidos / despacho
- crear pedido
- crear detalle de pedido
- consultar pedidos y detalle
- consultar despacho por cliente o repartidor

#### Clientes / saldos
- consultar listado de clientes
- consultar saldo por cliente
- consultar movimientos comerciales del cliente

### 12.3 Regla crítica
Backend debe evitar lógica duplicada e incoherente.  
Lo que ya se resuelve bien en la BD (vistas, función, constraints) no debe reprogramarse de manera contradictoria.

---

## 13. Requerimientos de API sugeridos

> Esto no es contrato cerrado; es una guía inicial.

### Dashboard
- `GET /api/dashboard/resumen`
- `GET /api/dashboard/clientes-con-saldo`
- `GET /api/dashboard/stock-clave`

### Producción
- `GET /api/produccion`
- `POST /api/produccion`
- `GET /api/produccion/resumen-dia`
- `GET /api/produccion/resumen-turno`

### Bodega
- `GET /api/bodega/stock`
- `GET /api/bodega/movimientos`
- `POST /api/bodega/movimiento`
- `GET /api/bodega/conteos`
- `POST /api/bodega/conteo`

### Pedidos
- `GET /api/pedidos`
- `POST /api/pedidos`
- `GET /api/pedidos/{id}`
- `POST /api/pedidos/{id}/detalle`

### Clientes
- `GET /api/clientes`
- `GET /api/clientes/saldos`
- `GET /api/clientes/{id}/resumen`
- `GET /api/clientes/{id}/movimientos`

### Reportes
- `GET /api/reportes/ventas-por-cliente`
- `GET /api/reportes/stock-por-fecha`
- `GET /api/reportes/produccion-por-turno`
- `GET /api/reportes/despacho-por-repartidor`

---

## 14. Qué debe mostrar frontend

### Pantallas mínimas recomendadas
1. Dashboard
2. Producción
3. Bodega
4. Pedidos / Despacho
5. Clientes / Saldos
6. Reportes

### Comportamiento esperado
- filtros por fecha
- filtros por cliente
- filtros por repartidor
- tablas claras
- montos formateados en CLP
- vistas similares a la utilidad del Excel, pero ordenadas por módulo

### Regla visual importante
No basta con mostrar tablas.  
El valor del frontend está en:
- resumir
- ordenar
- filtrar
- destacar alertas y pendientes

---

## 15. Formato y presentación de datos

### 15.1 Dinero
Mostrar como:
- `$ 46.980`
- no `46980.0000`

### 15.2 RUT
Guardar limpio en BD, pero formatear en consultas o frontend:
- `44.444.444-4`

### 15.3 Teléfono
Guardar como texto; presentar legible si se muestra.

### 15.4 Fechas
Usar formato consistente y filtrable.

---

## 16. Integración entre base, backend y frontend

### Regla 1
Frontend nunca consulta directo a PostgreSQL.

### Regla 2
Backend usa la BD como fuente de verdad.

### Regla 3
La lógica de negocio crítica no debe quedar solo en frontend.

### Regla 4
La presentación bonita de montos, RUT y reportes puede resolverse en backend o frontend, pero sin alterar el dato base guardado.

### Regla 5
Los nombres visibles en UI pueden diferir del nombre técnico interno, pero deben mapearse claramente.

---

## 17. Decisiones ya tomadas y que no deben reabrirse sin motivo

- PostgreSQL como base de datos
- Django/Python como backend
- Angular como frontend
- uso de `unidad_venta_base` en producto
- uso de `unidad_medida` en detalle_pedido
- uso de `cantidad_entregada` + `unidad_medida` en detalle_movimiento
- descuentos en porcentaje
- soporte de ventas por kilo y por unidad
- uso de vistas para resumen y saldo
- uso de formato CLP para reportes

---

## 18. Supuestos temporales actualmente vigentes

Estos supuestos existen para permitir desarrollo y pruebas. No son decisiones comerciales finales.

- algunos precios unitarios son referenciales
- el dataset actual es de prueba
- la autenticación definitiva aún no está cerrada
- el despliegue definitivo aún no está documentado aquí
- no todos los triggers de validación están implementados todavía

---

## 19. Pendientes abiertos

1. Confirmar precios unitarios reales faltantes
2. Definir si habrá un solo rol operativo o más de uno en backend
3. Definir estrategia de autenticación/autorización
4. Confirmar qué reportes del Excel son imprescindibles en v1
5. Decidir qué lógica futura irá en BD y cuál en backend
6. Implementar backlog de validaciones PL/pgSQL si el equipo lo considera conveniente

---

## 20. Qué debe leer el desarrollador backend junto a este documento

### Obligatorio
- este documento
- script SQL canónico vigente del proyecto
- dataset de prueba actual
- lista de consultas de validación que ya fueron probadas

### Recomendado
- Excel operativo original como referencia visual del negocio
- lista de módulos acordados
- decisiones futuras de autenticación y despliegue

---

## 21. Instrucciones de uso de este documento con una IA

Si este documento se cargará en una IA para ayudar a construir backend o frontend, la instrucción recomendada es:

- no inventar nuevas reglas de negocio
- respetar el modelo actual
- usar PostgreSQL como fuente de verdad
- proponer solo cambios compatibles con las decisiones ya tomadas
- separar claramente lógica de BD, backend y frontend
- pedir confirmación antes de rediseñar módulos o tablas

---

## 22. Cierre

La base de datos ya se encuentra en un estado suficientemente sólido para iniciar coordinación real con backend.  
El siguiente paso no es seguir agregando lógica sin control, sino usar esta base como contrato funcional y técnico del sistema.

La prioridad inmediata del equipo debe ser:

1. tomar este documento como guía
2. usar el script SQL vigente como anexo técnico
3. definir endpoints y pantallas a partir de los módulos ya acordados
4. mantener coherencia con el Excel original sin replicar su desorden

---

## Anexo A. Script técnico canónico

Este documento asume como anexo técnico el archivo SQL maestro vigente del proyecto.  
Ese archivo es el que backend debe usar para:
- recrear la BD
- revisar tablas
- revisar constraints
- revisar vistas
- revisar dataset de prueba

## Anexo B. Estado actual de madurez del proyecto

### Ya resuelto
- modelo base
- poblamiento de prueba
- consultas de validación
- formato de reportes monetarios
- primera función PL/pgSQL útil

### En coordinación inmediata
- documento líder
- traspaso a backend
- definición de pantallas principales

### En backlog controlado
- triggers y validaciones avanzadas
- rinde ideal
- cierre de jornada
- mejoras de reportes
