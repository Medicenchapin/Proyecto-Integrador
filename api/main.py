from __future__ import annotations

from functools import lru_cache

from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import JSONResponse

from api import config, schemas
from api.services.llm_service import OllamaClient
from api.services.model_service import PredictionResult, XGBSalesModel

app = FastAPI(
    title="Tigo Sales Assistant API",
    description="Realtime scoring API combining the XGBoost model and an Ollama LLM.",
    version="1.0.0",
)


@lru_cache
def get_model() -> XGBSalesModel:
    try:
        return XGBSalesModel(model_path=config.MODEL_PATH)
    except FileNotFoundError as exc:
        raise RuntimeError(
            f"Model file not found at {config.MODEL_PATH}. "
            "Export the booster from the notebook or update XGB_MODEL_PATH."
        ) from exc


@lru_cache
def get_llm_client() -> OllamaClient:
    return OllamaClient()


@app.on_event("startup")
def warm_up() -> None:
    # Force lazy singletons to load so errors surface early.
    get_model()


@app.get("/health", tags=["health"])
def healthcheck() -> JSONResponse:
    return JSONResponse({"status": "ok"})


def _build_prediction_response(result: PredictionResult) -> schemas.PredictionResponse:
    return schemas.PredictionResponse(
        probability=result.probability,
        decision=result.decision,
        threshold=result.threshold,
        top_features=result.contributions,
    )


@app.post("/predict", response_model=schemas.PredictionResponse, tags=["scoring"])
def predict(
    payload: schemas.FeatureVector,
    threshold: float = 0.5,
    model: XGBSalesModel = Depends(get_model),
) -> schemas.PredictionResponse:
    try:
        result = model.predict(payload, threshold=threshold)
    except Exception as exc:  # pragma: no cover - surfaced as HTTP error
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return _build_prediction_response(result)


@app.post("/pitch", response_model=schemas.PitchResponse, tags=["pitch"])
def generate_pitch(
    payload: schemas.PitchRequest,
    model: XGBSalesModel = Depends(get_model),
    llm_client: OllamaClient = Depends(get_llm_client),
) -> schemas.PitchResponse:
    try:
        prediction = model.predict(payload, threshold=payload.threshold)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    try:
        speech = llm_client.generate_pitch(prediction.probability, prediction.contributions, language=payload.language)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Ollama error: {exc}") from exc

    return schemas.PitchResponse(
        customer_id=payload.customer_id,
        probability=prediction.probability,
        decision=prediction.decision,
        speech=speech,
        top_features=prediction.contributions,
    )

