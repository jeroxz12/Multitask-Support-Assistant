# Reporte del Proyecto Integrador

## 1. Arquitectura

El proyecto es un MVP por línea de comandos, no un servicio HTTP. Un agente de soporte envía una pregunta del cliente con `python3 -m src.support_assistant`. El CLI parsea esa pregunta y ejecuta un pipeline fijo:

CLI → chequeo de safety en la entrada → constructor de prompt → OpenAI Responses API → Structured Output → validación de schema → chequeo de safety en la salida → métricas → respuesta JSON.

El constructor de prompt carga `prompts/main_prompt.md` como mensaje de sistema y envuelve la pregunta como datos no confiables. El modelo se llama con la Responses API y `text_format=SupportResponse`. Pydantic vuelve a validar el objeto parseado antes de imprimirlo. Cada ejecución agrega una fila a `metrics/metrics.csv`, incluidos los bloqueos de safety que nunca llegan a OpenAI. Stdout queda limitado al contrato JSON; los errores van a stderr.

## 2. Ingeniería de prompts

El system prompt combina instruction prompting y few-shot prompting. Las instrucciones definen el rol (asistente de agentes de soporte, no la voz de la empresa), las reglas de comportamiento (no inventar políticas, cuentas ni hechos de transacciones), las etiquetas cualitativas de confidence y los tipos de action permitidos.

Few-shot prompting es la técnica principal: los ejemplos de entrada/salida cubren conocimiento general, un pago sin detalle, una falla concreta de upload con dos actions, transacciones de aspecto no autorizado, reportes vagos y una pregunta out-of-scope. Ese formato encaja con un contrato JSON chico. Los ejemplos enseñan *cuándo* pedir información, escalar o declarar fuera de alcance.

Si la pregunta no es de customer support, el asistente no la responde. Indica que está fuera de alcance, usa `confidence=high` y `action=none`. High acá significa que está claro que el tema no corresponde al asistente, no que se sepa la respuesta de trivia.

No se usó self-consistency. Muestrear varias completions y votar multiplicaría latencia y costo. Aporta poco una vez que el schema, el enum de actions y los ejemplos ya restringen la salida.

El control de alucinaciones es procedimental, no basado en retrieval: el prompt prohíbe datos internos inventados, la confidence debe bajar cuando faltan hechos, y `request_information` es el default si el síntoma no está claro. Confidence es una etiqueta (`high` / `medium` / `low`), no una probabilidad. Las actions son una lista no vacía de ítems tipados (`none`, `request_information`, `troubleshoot`, `escalate_human`, `follow_up`).

## 3. Salida estructurada

`SupportResponse` tiene tres campos: `answer`, `confidence` y `actions` (al menos una). Cada `Action` tiene `type` y `description`. Se rechazan claves extra. `answer` y `action.description` no pueden estar vacíos ni ser solo espacios. Así la salida del CLI queda estable y se bloquean cambios de rol en texto libre fuera del schema.

## 4. Observabilidad

Cada corrida registra `tokens_prompt`, `tokens_completion`, `total_tokens`, `latency_ms`, `estimated_cost_usd`, más timestamp, status y model. Los tokens salen del usage de la API (`input_tokens` / `output_tokens` de forma interna). La latencia se mide alrededor de la llamada a la API cuando corre el modelo, o como tiempo local en las salidas tempranas.

Costo conceptual:

`estimated_cost_usd = (tokens_prompt × input_usd_per_million + tokens_completion × output_usd_per_million) / 1_000_000`

Los precios viven en una tabla estática. Si el modelo configurado no tiene fila, el estimador devuelve `None` y el CSV guarda `unavailable`. Así no se interpreta un precio desconocido como una corrida de USD 0. Un snapshot de modelo no listado en `MODEL_PRICES_PER_MILLION` cae en ese mismo caso. Los precios publicados pueden cambiar; la tabla no es facturación en vivo.

El repositorio ya incluye filas exitosas de `gpt-4o-mini` en `metrics/metrics.csv` (por ejemplo cerca de 1.3k tokens de prompt y un costo estimado cercano a `$0.00024`). Esas cifras son ejecuciones locales sueltas, no un reporte formal de evaluación.

## 5. Safety

La safety está en capas:

1. Instrucciones de sistema: ignorar instrucciones dentro de la pregunta; no revelar el prompt.
2. Wrapper de usuario no confiable: la pregunta se etiqueta como datos y se coloca en `<customer_question>`.
3. Detector de injection en la entrada: coincidencia de substrings contra frases específicas de override o filtrado del prompt.
4. Structured Output: el modelo no puede devolver un documento arbitrario.
5. Detector de fugas en la salida: busca fragmentos distintivos del system prompt en la respuesta.
6. Fallback: un `SupportResponse` fijo y válido que pide reformular el problema de soporte.

El detector de frases es heurístico. Se evitaron patrones genéricos como “mostrame” o “ignora las instrucciones” porque bloqueaban consultas legítimas (cambiar una contraseña, o “la aplicación ignora las instrucciones que escribo”). Cadenas específicas como “ignore previous instructions” o “mostrame el prompt del sistema” siguen disparando fallback. Parafraseos y jailbreaks nuevos pueden pasar. En este milestone no hay Moderation API.

## 6. Evaluación

Hay dos datasets JSON.

`evals/smoke_cases.json` repite preguntas cercanas a los ejemplos few-shot. Solo sirve para verificar que las demostraciones del prompt siguen comportándose.

`evals/held_out_cases.json` tiene preguntas nuevas (timeouts de sesión, cargos desconocidos, reportes vacíos, posible toma de cuenta, trivia fuera de alcance, fallo de upload de PDF después de un login exitoso, y similares). Las categorías incluyen confidence high/medium/low, escalamiento humano, múltiples actions y out of scope.

Cada caso held-out declara una expectativa principal. `expected_action_types` son actions que tienen que aparecer para marcar pass. Out-of-scope espera `confidence=high` y `action=none`.

Las preguntas de evaluación no deben copiar los ejemplos del prompt. Si lo hicieran, el puntaje mediría memorización del few-shot, no generalización. El runner `python3 -m src.support_assistant.evaluate` usa el archivo held-out, llama a OpenAI y guarda `evals/results.json`.

Una corrida real con `gpt-4o-mini` quedó en `evals/results.json`: **10/13** casos pasaron los checks automáticos de confidence/action. Los tres FAIL se revisaron a mano:

- `held_follow_up_refund_silence`: se esperaba `follow_up`; el modelo pidió más datos (`request_information`) y no inventó el estado del reembolso.
- `held_medium_reset_email`: se esperaban `request_information` y `troubleshoot`; el modelo solo devolvió `request_information` (el scorer exige todas las actions listadas).
- `held_low_random_error_code`: se esperaba `confidence=low`; el modelo usó `medium` y sugirió que el código `9b` indica un issue específico, sin contexto de producto.

Esos FAIL no rompen el contrato JSON. El dataset se deja así a propósito: no se reentrenó el prompt para forzar 13/13.

## 7. Trade-offs y limitaciones

No hay RAG ni knowledge base interna de la empresa. El modelo igual puede alucinar si ignora el prompt. El matching de safety es heurístico. La confidence es cualitativa. Las estimaciones de costo dependen de una tabla de precios estática. El producto es un MVP CLI: sin auth, sin integración a ticketing y sin API HTTP.

## 8. Mejoras futuras

Pasos útiles: retrieval sobre una knowledge base de la empresa; historial de ejecuciones de evaluación; comparación de resultados entre modelos; comparación de versiones del prompt; guardrails más ricos que listas de substrings; un endpoint HTTP para herramientas de tickets; y un snapshot id fijado en `OPENAI_MODEL` para mejorar la reproducibilidad.
