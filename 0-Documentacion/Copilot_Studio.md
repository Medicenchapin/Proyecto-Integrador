# Target operativo (batch mensual)

* **Input**: dataset scoring + **SHAP precomputado** por `customer_id` (tu pipeline actual).
* **Orquestación**: job mensual (Databricks/Azure ML/SQL + Power Automate o cron) que:

  1. Calcula **Top-K features por |SHAP|** y su **signo** (pro/contra conversión).
  2. Aplica **plantillas** o un **LLM offline** para fabricar un **script** por cliente.
  3. Empaqueta todo en **JSON canónico** y lo persiste con **versionado**.
* **Output**: repositorio gobernado (Dataverse/SQL/Blob/SharePoint) con un **JSON por cliente** listo para ser consumido por CRM, Teams o **Copilot Studio** (como conocimiento).

# Esquema JSON

Ejemplo:

```json
{
  "batch_id": "2025-10",
  "customer_id": "11998877",
  "profile": { "segment": "C+", "plan": "Prepago", "state_name": "GUATEMALA" },
  "top_features": [
    {"name": "arpu_90_days", "value": 148.7, "shap": 0.29, "direction": "pro"},
    {"name": "sn_banking",  "value": 1,     "shap": 0.42, "direction": "pro"},
    {"name": "minutes_in",  "value": 220,   "shap": -0.12,"direction": "contra"}
  ],
  "script": {
    "opening": "Hola, [Nombre]…",
    "insight_summary": [
      "Consumo de datos consistente y por encima de 5 GB.",
      "Cliente bancarizado: acceso a beneficios/financiación.",
      "ARPU alto: perfil con potencial de upgrade."
    ],
    "value_props": [
      "Plan con +20GB y redes incluidas.",
      "Financiación de equipo sin pago inicial."
    ],
    "objections": [
      {"cue":"Precio","reply":"Baja el costo efectivo por GB vs tu patrón actual."},
      {"cue":"Cambio de plan","reply":"Conservas tu número; migración guiada."}
    ],
    "cta": "¿Agendamos el cambio hoy?",
    "compliance_notes": ["No prometer velocidades. Leer TyC 2025-Q4."]
  },
  "quality": { "rules_version": "v1.2", "checks": ["no PII", "tokens < 350"] },
  "timestamps": { "generated_at": "2025-10-12T06:00:00Z", "valid_from": "2025-10-15", "valid_to": "2025-11-14" }
}
```

> Claves: **`batch_id`**, **`model_version`**, **ventana de validez** y **compliance** embebido. Esto habilita auditoría, rollbacks y QA.

## Copilot Studio 

Copilot Studio **consume** y explica/expone.

* **Knowledge Source**: publica los JSON (o su representación markdown) en un **SharePoint/OneDrive** dedicado o **Dataverse**. Copilot Studio “Grounded Q&A” puede **localizar** y **resumir** el script por `customer_id`, segmento, región, etc.
* **Prompt del agente (alto nivel)**:

  * “Cuando el usuario pida el guion de un cliente, **busca el JSON del batch vigente**, no inventes. Si hay varios, usa `valid_from/valid_to` y `batch_id` más reciente. Responde con secciones: Apertura, Insights (3 bullets), Propuesta (≤3 bullets), Objeciones (2), Cierre, y un bloque final de *Compliance*.”
* **Acceso**:

  * En **Teams**: el vendedor pregunta “Dame el script de GT-998877” → Copilot devuelve el contenido **ya generado** (o un resumen ejecutivo).
  * En **CRM**: una pestaña renderiza el JSON en UI (sin Copilot), y Copilot se usa solo para **explicar** o **simular** variantes de pitch a partir del mismo JSON.

# Generación del script (en tu batch)

**B. LLM offline (templado, controlado)**

* Promptea un LLM **en batch** con un **“content schema”**: le pasas `top_features`, segmentación y un **style guide**.
* Forzar **output JSON válido** con campos obligatorios (usa validadores; si falla, reintenta con temperatura baja).
* Ventajas: matices lingüísticos y personalización por micro-segmentos.
* Recomendación: **cache** del prompt por segmento + **post-edición automática** (reglas de tono/compliance).


# Copilot Studio: prompts y experiencia

**Prompt de consumo (Copilot Studio – conocimiento ya precargado)**:

> “Eres asesor de Tigo. Cuando el usuario pida el script de un cliente, **localiza el JSON del batch vigente** y **preséntalo** en español (es-GT) con secciones: Apertura, Insights (3), Propuesta (≤3), Objeciones (2), Cierre y *Compliance*.
> Si no encuentras el JSON del mes vigente, informa: ‘No hay script vigente para este cliente’ y sugiere `customer_id` o revisar el batch.”

**Prompt de explicación (opcional)**:

> “Si el usuario pregunta *por qué* el guion sugiere X, explica usando el **campo `top_features` y sus SHAP**. No expongas PII ni model weights. Usa lenguaje claro y breve.”