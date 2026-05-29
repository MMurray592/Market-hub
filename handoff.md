# Handoff — Revisar formato del informe digest-semanal

## Contexto

Mateo tiene un scheduled task `digest-semanal-viernes` que corre todos los viernes a las 19:04 y genera el "Daily's" (digest semanal de economía y mercados para Argentina y el mundo) usando la skill `digest-semanal`.

**Estado actual:**
- Permisos pre-aprobados para los 3 write tools (Notion create-database, Notion create-pages, Gmail create_draft). Confirmado en MODO TEST 2.
- Próximo run real: viernes 29-may 19:04.
- Pendiente de hacer manualmente: borrar la DB TEST en Notion y el draft TEST en Gmail.

## Objetivo de esta nueva conversación

**Revisar y refinar el formato del informe del digest semanal** antes del próximo run automático.

Mateo quiere mirar cómo queda estructurado el output del digest — qué secciones tiene, cómo se ven, qué falta, qué sobra, qué tono usa, cómo se renderiza el widget interactivo, cómo se ve el email/Notion page.

## Cómo arrancar

1. Leer la skill: `/var/folders/s9/c9f27n_92pb7jh94ngtx9y5r0000gn/T/claude-hostloop-plugins/c6d26f3cdad63430/skills/digest-semanal/SKILL.md` para entender el flujo y formato actual.
2. Revisar digests previos en `/Users/mateomurray/Desktop/Digests` para ver outputs reales.
3. Mirar los PDFs fuente en `/Users/mateomurray/Desktop/Claude/Projects/Market Analysis`.
4. Preguntarle a Mateo qué quiere cambiar específicamente: estructura, secciones, tono, longitud, formato del widget, contenido del email, etc.

## Componentes del output actual (según skill)

- Análisis con estructura **Leer-Conectar-Defender**.
- Verificación de datos contra fuentes oficiales: BCRA IMD, INDEC, A3 Mercados.
- Web search de keywords relevantes.
- Widget interactivo dark mode.
- Guardado local en carpeta Digests.
- Notion DB + page por semana.
- Email draft via Gmail.

## Preferencias de Mateo

- Respuestas breves y directas, sin cortesías.
- Usuario de Mac.
- Compromiso fuerte con honestidad y precisión: marcar incertidumbre, no inventar fuentes ni stats, recordar cutoff de conocimiento.
- Español argentino.

## Lo que NO hay que hacer

- No ejecutar el digest real ahora — el scheduled task lo hace solo el viernes.
- No tocar la DB TEST ni el draft TEST en Notion/Gmail — Mateo los borra manualmente.
- No modificar la skill sin que Mateo lo pida explícitamente.
