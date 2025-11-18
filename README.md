# Proyecto Integrador — Tigo Guatemala (Millicom)
## Cuadro Informativo Inteligente de Cliente

**Equipo:** Ignacio José Aguilar García, Alejandro Calderón Aguilar, Ricardo Mar Cupido  
**Área patrocinadora:** Telemarketing y Profiling — Tigo Guatemala  
**Dominio de aplicación:** Sistemas de recomendación  
**Periodo:** 15-sep-2025 a 14-nov-2025  
**Responsable/stakeholder:** Martin Luis Harold Guzmán (Telemarketing)

---

## 1) Propósito
Unificar en un **cuadro único** la información clave del cliente y entregar **recomendaciones explicables** (basadas en *Shapley values/SHAP*) para que el agente construya en **tiempo real** un speech de venta **personalizado, preciso y consistente**.

## 2) Contexto y problema de negocio
Hoy los agentes navegan múltiples pantallas/fuentes, invirtiendo ~minutos para armar el guion y con riesgo de abordajes poco pertinentes, afectando **AHT**, **eficiencia operativa** y **conversión**. El proyecto concentra datos y prioriza la **información relevante por cliente** para acelerar y mejorar la interacción comercial.

## 3) Solución (visión funcional)
- **Widget/UI del agente:** perfil resumido + **Top-3 razones SHAP** + **speech sugerido**.
- **Motor de scoring** (batch/near-real-time) con **explicabilidad local** por cliente.
- **Monitoreo** de estabilidad de datos y ranking de variables (explicabilidad global).
- **Gobernanza:** data cards, auditoría de razones, resguardo de PII y acceso por roles.

> Esta definición se alinea a “Nombre/alcance, objetivos, beneficios, indicadores, riesgos y mitigaciones” descritos en el documento **Datos Generales** de la materia (Equipo 25).

## 4) Objetivo general
Implementar un sistema de recomendación **explicable** que permita a los agentes generar discursos **personalizados** y eficientes, reduciendo el tiempo de análisis previo y elevando la **tasa de conversión**.

## 5) Objetivos específicos
1. Integrar modelos de ML **explicables** (Shapley Values) para identificar **variables clave** por cliente.
2. Desplegar el **cuadro único** con datos relevantes y explicaciones accionables para el agente.
3. **Aumentar cobertura** de base gestionada por agente.
4. Mejorar **KPIs comerciales** (Conversión, ARPU uplift) en Home, Prepago y Postpago.

## 6) Alcance (MVP)
- Sistema de recomendación para Home, Prepago y Postpago.
- Pilotos con agentes reales y **QA** supervisando muestra representativa.
- Medición de impacto: **Conversión, Objeciones resueltas, ARPU uplift, AHT**.
- Feedback loop para iterar guiones y razones mostradas.

## 7) Beneficios esperados
- **Menor AHT** por llamada.  
- **Mayor conversión** con speech adaptado al perfil.  
- **Menor ramp-up** de nuevos agentes (homogeneización del discurso).  
- **Mejor experiencia** percibida por el cliente.

## 8) Indicadores sugeridos
- **Conversión (%).**
- **ARPU uplift.**
- **Objeciones resueltas (%).**
- **Precisión/Utilidad del guion** (vía feedback loop).

## 9) Riesgos y mitigaciones (síntesis)
- **Plazos:** planificación granular, ownership claro y comunicación con sponsor.
- **PII/sensibilidad:** pseudonimización, hashing, acceso por roles, no compartir PII.
- **Sesgo/fairness:** monitoreo de métricas por segmento y exclusión de atributos sensibles.
- **Atribución del efecto:** **A/B testing** y registro de contexto/resultado.

## 11) Contacto
- **Sponsor de negocio:** Martin Luis Harold Guzmán  
- **Equipo académico:** Equipo 25 — MNA, Dra. Grettel Barceló

---

## FastAPI + Ollama Serving Layer

El directorio `api/` contiene un microservicio FastAPI que expone el **modelo XGBoost** con explicaciones (`pred_contribs`) y genera el speech comercial con un **LLM local vía Ollama**.

### 1. Preparar el modelo XGB
1. Desde el notebook `5-final_model/Avance5_Equipo25.ipynb` exporta el booster entrenado:
   ```python
   booster = final_model.get_booster()
   booster.save_model("models/xgb_sales.json")
   ```
2. Ajusta la variable `XGB_MODEL_PATH` si decides guardar el archivo en otra ruta.

### 2. Dependencias
```
pip install -r api/requirements.txt
```
Además, instala y levanta Ollama con el modelo deseado (ej. `ollama pull llama3.1`).

### 3. Variables de entorno clave
```
XGB_MODEL_PATH=models/xgb_sales.json
OLLAMA_MODEL=llama3.1
OLLAMA_BASE_URL=http://localhost:11434/api/generate
TOP_K_FEATURES=3
```

### 4. Ejecutar la API
```
uvicorn api.main:app --reload
```

#### ¿Prefieres contenedor?
```
docker build -t tigo-sales-api .
docker run -p 8000:8000 \
  -e XGB_MODEL_PATH=/app/models/xgb_sales.json \
  -v $(pwd)/models:/app/models \
  tigo-sales-api
```
> Monta `models/` con el archivo `xgb_sales.json` exportado y asegúrate de que
> Ollama esté accesible (por defecto `http://host.docker.internal:11434`) para que el contenedor pueda invocar al LLM.

### 5. Endpoints
- `GET /health`: verificación básica.
- `POST /predict`: ingiere las 22 features ya transformadas (target encoding/one-hot) y devuelve probabilidad + top drivers.
- `POST /pitch`: usa el mismo payload y construye un script con el LLM de Ollama.

Ejemplo mínimo:
```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d @sample_request.json
```
Consulta `api/schemas.py` para el nombre exacto de cada campo (ej. `previous_classification_new_client`).
