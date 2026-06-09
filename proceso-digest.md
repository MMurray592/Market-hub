# Proceso de generación de Digests

Documento de referencia para reciclar el flujo del digest semanal y adaptarlo a digests diarios cuando corresponda.

## Resumen del flujo (vigente para semanales)

**Skill:** `digest-semanal`
**Path skill:** `~/Library/.../skills/digest-semanal/SKILL.md`
**Scheduled task:** `digest-semanal-viernes` (deshabilitado del auto-run; se ejecuta manual)

### Inputs

1. **PDFs locales** de brokers/analistas. Carpeta de entrada: `/Users/mateomurray/Desktop/Digests/inbox-pdfs/`
2. **Mails de brokers** (vie a vie, últimos 7 días) en modo snippet-first:
   - `from:news@bloomberglinea.com`
   - `from:contacto@mailing.portfoliopersonal.com`
   - `from:informes@gruposbs.com`

### Pasos (orden de ejecución)

1. **Keywords de la semana** (5 máx): IPC, Dólar, Tasas, Crédito, Global, Política.
2. **Extraer PDFs** con `markitdown` (fallback `pdftotext`). NO usar `Read` directo — output va a `/tmp/digest-pdfs/*.md`. Luego `grep -c` para conteo de keywords y `grep -A 3 -B 1` para extraer contexto puntual.
3. **Revisar mails brokers (snippet-first):** primero solo subject + snippet. Abrir thread con `get_thread` SOLO si contiene triggers: licitación, IPC, default, Fed, FOMC, halt, calificación, etc. Máximo 8 threads abiertos por run.
4. **Verificar dato oficial:** máximo 1 fetch oficial por run (BCRA IMD / INDEC / MECON) y solo si hay contradicción entre fuentes. NO hacer web search general.
5. **Armar análisis por tab** con estructura Leer-Conectar-Defender:
   - Qué cambió (azul `#74ACDF`)
   - Por qué le importa al mercado (amarillo `#F6B40E`)
   - Posición analista (gris `#c0c0c0`)
   - Contraargumento (rojo `#f87171`)
6. **Generar HTML standalone** dark mode con 6 tabs:
   - Dólar & BCRA · Tasas · IPC · Crédito · Global · Radar
   - Métricas (4 cards) + gráfico de barras horizontales + 4 cards de análisis + watch pills
   - Radar: señales alcistas/bajistas + posiciones core + catalizadores 4 semanas
7. **Guardar HTML** en: `/Users/mateomurray/Desktop/Digests/Market Analysis/semanales/`
   Nombre obligatorio: `digest-semanal-YYYY-MM-DD.html` (YYYY-MM-DD = viernes de cierre de la semana). El hub `actualizar_hub.py` filtra por `fname.startswith('digest-semanal-')`.

### Output: integración con el hub

- Hub local: `/Users/mateomurray/Desktop/Digests/Market Analysis/index.html`
- Hub online: https://mmmarkethub.netlify.app
- Script: `actualizar_hub.py` lee `semanales/`, `digests-diarios/html/`, `Pre-Markets/` y arma el índice.
- Deploy: `actualizar_y_pushear.sh` empuja a Netlify (~30 seg).

**Constraint del parser:** el script extrae metadata por regex de:
- `<h1>...</h1>` → título
- `<p class="sub">...</p>` → subtítulo / fechas
- `<span class="badge">...</span>` → badge de rango semanal
- `<title>...</title>` → fallback
- `<button class="tab...">...</button>` → tabs

No cambiar esas etiquetas sin actualizar también el script.

## Reglas críticas (no negociables)

1. **Datos siempre con fuente visible** en cada card (ej: "SBS Comentario 28-may").
2. **No inventar datos.** Si una métrica no está en los PDFs/mails verificados, decirlo o saltarla.
3. **Tono directo**, sin "es importante destacar" ni "cabe señalar".
4. **Cap de consumo: ~100k input tokens.** Si se va a exceder, parar y avisar.
5. **Contraargumentos reales**, no strawmen.
6. **Tasa cortas en negativo real / horizonte temporal** siempre que se mencione una posición.

## Adaptación para Digest Diario (cuando se haga)

Tomar este flujo como base, con estos cambios mínimos:

| Campo | Semanal | Diario |
|---|---|---|
| Carpeta output | `Market Analysis/semanales/` | `Market Analysis/digests-diarios/html/` |
| Nombre archivo | `digest-semanal-YYYY-MM-DD.html` | `Digest Diario - YYYY-MM-DD.html` o `Daily's - YYYY-MM-DD.html` (ver parser) |
| Ventana mails | `newer_than:7d` | `newer_than:1d` |
| Ventana PDFs | semana completa | día previo (cierre) + premarket del día |
| Tabs | 6 temáticos + Radar | 4-5 más reducidos (sugerido: Mercado AR / Mercado Global / Flujos / Watch) |
| Análisis 4 cards | Sí (Leer-Conectar-Defender + Contraargumento) | Probablemente reducir a 2-3 cards (más sintético) |
| Estructura Radar | Sí | Posiblemente eliminar — reemplazar por "trades del día" más cortos |

### Lo que NO cambia

- Estilo visual dark mode (paleta, tipografías, espaciado)
- `markitdown` para PDFs, snippet-first para mails
- Reglas críticas (fuentes, no inventar, tono)
- Constraint del parser del hub (estructura HTML)

### Inputs adicionales para diario

Para el digest diario probablemente sirvan también:
- Cierre de mercado previo (precios spot, índices, tasas)
- Pre-market US y AR (futuros)
- Eventos del día (calendario macro, licitaciones, earnings)

Definir si vienen vía mails de brokers (SBS Nota Diaria, PPI Daily Mercados ya cubren mucho) o si hay que sumar otras fuentes.

## Cambios pendientes en SKILL.md (28-may)

Identificados con Claude Code, pendientes de aplicar:

1. **Línea 15 y 31**: ruta de PDFs hardcodeada vieja → cambiar a `Digests/inbox-pdfs/`.
2. **Línea 16 y 173**: ruta de output vieja → cambiar a `Digests/Market Analysis/semanales/`.
3. **Línea 173-174**: nombre del archivo dice `Daily's — DD de mes YYYY.html` → debe ser `digest-semanal-YYYY-MM-DD.html` para que el hub lo levante.
4. **Línea 199**: nota sobre "carpeta Informes" desactualizada → mencionar `inbox-pdfs/`.

## Historial

- **2026-05-28**: primer run manual exitoso. Output: `digest-semanal-2026-05-28.html` (semana 22–28 may 2026). Flujo nuevo aplicado: markitdown + mails snippet-first + sin web search. Reducción consumo ~60% vs. versión original.
- **2026-05-28**: hub publicado en Netlify (https://mmmarkethub.netlify.app).
- **2026-05-28**: Notion descartado como output (no replica el HTML interactivo).
