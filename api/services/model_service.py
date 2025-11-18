from __future__ import annotations

from dataclasses import dataclass
from typing import List

import pandas as pd
import xgboost as xgb

from api import config, schemas


@dataclass
class PredictionResult:
    probability: float
    decision: bool
    threshold: float
    contributions: List[schemas.FeatureContribution]


class XGBSalesModel:
    """Thin wrapper around the exported booster with pred_contribs support."""

    def __init__(self, model_path=config.MODEL_PATH):
        self.model_path = model_path
        self._booster = self._load()
        self._api_to_column = config.API_TO_COLUMN
        self._column_to_api = {v: k for k, v in config.API_TO_COLUMN.items()}

    def _load(self) -> xgb.Booster:
        booster = xgb.Booster()
        booster.load_model(str(self.model_path))
        return booster

    def reload(self) -> None:
        self._booster = self._load()

    def predict(self, payload: schemas.FeatureVector, threshold: float = 0.5) -> PredictionResult:
        df = pd.DataFrame([payload.as_model_dict()])
        dmatrix = xgb.DMatrix(df[config.FEATURE_COLUMN_ORDER])
        probability = float(self._booster.predict(dmatrix)[0])
        contrib_matrix = self._booster.predict(dmatrix, pred_contribs=True)
        contributions = contrib_matrix[0][:-1]  # last element is bias term
        feature_values = df.iloc[0].to_dict()

        feature_contribs = []
        for column_name, contribution in zip(config.FEATURE_COLUMN_ORDER, contributions):
            api_name = self._column_to_api.get(column_name, column_name)
            feature_contribs.append(
                schemas.FeatureContribution(
                    name=api_name,
                    value=float(feature_values[column_name]),
                    contribution=float(contribution),
                    direction="pro" if contribution >= 0 else "contra",
                )
            )

        feature_contribs.sort(key=lambda item: abs(item.contribution), reverse=True)
        top = feature_contribs[: config.TOP_K_FEATURES]
        decision = probability >= threshold
        return PredictionResult(probability=probability, decision=decision, threshold=threshold, contributions=top)

