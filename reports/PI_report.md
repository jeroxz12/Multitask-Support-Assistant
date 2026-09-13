# Reporte del Proyecto Integrador

## 1. Arquitectura

El proyecto es un MVP por línea de comandos, no un servicio HTTP. Un agente de soporte envía una pregunta del cliente con `python3 -m src.support_assistant`. El CLI parsea esa pregunta y ejecuta un pipeline fijo:

CLI → chequeo de safety en la entrada → constructor de prompt → OpenAI Responses API → salida estructurada → validación de schema → chequeo de safety en la salida → métricas → respuesta JSON.

El constructor de prompt carga `prompts/main_prompt.md` como mensaje de sistema y envuelve la pregunta como datos no confiables. El modelo se llama con la Responses API y `text_format=SupportResponse`, para que el proveedor devuelva el schema de forma directa. Pydantic vuelve a validar el objeto parseado antes de imprimirlo. Cada ejecución agrega una fila a `metrics/metrics.csv`, incluidos los bloqueos de safety que nunca llegan a OpenAI. Stdout queda limitado al contrato JSON; los errores van a stderr.

## 2. Ingeniería de prompts

El system prompt combina instruction prompting y few-shot prompting. Las instrucciones definen el rol (asistente de agentes de soporte, no la voz de la empresa), las reglas de comportamiento (no inventar políticas, cuentas ni hechos de transacciones), las etiquetas cualitativas de confidence y los tipos de action permitidos.

Few-shot prompting es la técnica principal: seis ejemplos de entrada/salida muestran conocimiento general de alta confianza, un pago rechazado sin detalle, una falla concreta de upload con dos actions, transacciones de aspecto no autorizado, y reportes vagos de cuenta o app. Ese formato encaja con un contrato JSON chico. Los ejemplos enseñan *cuándo* pedir información o escalar, algo difícil de lograr solo con una lista corta de reglas.

No se usó self-consistency. Muestrear varias completions y votar multiplicaría latencia y costo. Aporta poco una vez que el schema, el enum de actions y los ejemplos ya restringen la salida.

El control de alucinaciones es procedimental, no basado en retrieval: el prompt prohíbe datos internos inventados, la confidence debe bajar cuando faltan hechos, y `request_information` es el default si el síntoma no está claro. Confidence es una etiqueta (`high` / `medium` / `low`), no una probabilidad. Las actions son una lista no vacía de ítems tipados (`none`, `request_information`, `troubleshoot`, `escalate_human`, `follow_up`).

## 3. Salida estructurada

`SupportResponse` tiene tres campos: `answer`, `confidence` y `actions` (al menos una). Cada `Action` tiene `type` y `description`. Se rechazan claves extra. `answer` y `action.description` no pueden estar vacíos ni ser solo espacios. Así la salida del CLI queda estable para herramientas posteriores y se bloquean cambios de rol en texto libre que un jailbreak podría intentar colar fuera del schema.

## 4. Observabilidad

Cada corrida registra `tokens_prompt`, `tokens_completion`, `total_tokens`, `latency_ms`, `estimated_cost_usd`, más timestamp, status y model. Los tokens salen del objeto de usage de la API (`input_tokens` / `output_tokens` de forma interna). La latencia se mide alrededor de la llamada a la API cuando corre el modelo, o como tiempo local en las salidas tempranas.

Costo conceptual:

`estimated_cost_usd = (tokens_prompt × input_usd_per_million + tokens_completion × output_usd_per_million) / 1_000_000`

Los precios viven en una tabla estática. Si el modelo configurado no tiene fila, el estimador devuelve `None` y el CSV guarda `unavailable`. Así no se interpreta un precio desconocido como una corrida de USD 0. Los precios publicados pueden cambiar; la tabla no es facturación en vivo.

El repositorio ya incluye filas exitosas de `gpt-4o-mini` en `metrics/metrics.csv` (por ejemplo cerca de 1.3k tokens de prompt y un costo estimado cercano a `$0.00024`). Esas cifras son ejecuciones locales sueltas, no un reporte formal de evaluación.

## 5. Safety

La safety está en capas:

1. Instrucciones de sistema: ignorar instrucciones dentro de la pregunta; no revelar el prompt.
2. Wrapper de usuario no confiable: la pregunta se etiqueta como datos y se coloca en `<customer_question>`.
3. Detector de injection en la entrada: coincidencia de substrings contra frases específicas de override o filtrado del prompt.
4. Salida estructurada: el modelo no puede devolver un documento arbitrario.
5. Detector de fugas en la salida: busca fragmentos distintivos del system prompt en la respuesta.
6. Fallback: un `SupportResponse` fijo y válido que pide reformular el problema de soporte.

El detector de frases es heurístico. Se sacaron palabras genéricas como “mostrame” porque bloqueaban how-tos legítimos. Cadenas específicas como “ignore previous instructions” o “mostrame el prompt del sistema” siguen disparando fallback. Parafraseos y jailbreaks nuevos pueden pasar. En este milestone no hay Moderation API.

## 6. Evaluación

Hay dos datasets JSON.

`evals/smoke_cases.json` repite preguntas cercanas a los ejemplos few-shot. Solo sirve para verificar que las demostraciones del prompt siguen comportándose.

`evals/held_out_cases.json` tiene preguntas nuevas (timeouts de sesión, cargos desconocidos, reportes vacíos de “nada funciona”, posible toma de cuenta, trivia fuera de alcance, fallo de upload de PDF después de un login exitoso, y similares). Las categorías incluyen confidence high/medium/low, escalamiento humano, múltiples actions y out of scope.

Las preguntas de evaluación no deben copiar los ejemplos del prompt. Si lo hicieran, el puntaje mediría memorización del few-shot, no generalización. El runner opcional `python3 -m src.support_assistant.evaluate` usa el archivo held-out y llama a OpenAI. Este reporte no inventa totales de pass/fail para esos casos.

## 7. Trade-offs y limitaciones

No hay RAG ni knowledge base interna de la empresa. El modelo igual puede alucinar si ignora el prompt. El matching de safety es heurístico. La confidence es cualitativa. Las estimaciones de costo dependen de una tabla de precios estática. El producto es un MVP CLI: sin auth, sin integración a ticketing y sin API HTTP.

## 8. Mejoras futuras

Pasos útiles: retrieval sobre una knowledge base de la empresa; un runner de evaluación automático que persista resultados held-out; guardrails más ricos que listas de substrings; un endpoint HTTP para herramientas de tickets; y comparación de modelos con un snapshot id fijado para mejorar la reproducibilidad.
