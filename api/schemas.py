from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field

from api import config


class FeatureVector(BaseModel):
    """Input payload with engineered features ready for the XGB model."""

    state_name: float = Field(..., description="Target-encoded region/state value.")
    previous_classification_not_interested: float = Field(...)
    previous_classification_new_client: float = Field(...)
    previous_classification_not_effective: float = Field(...)
    previous_calls: float = Field(...)
    client_age: float = Field(...)
    network_age_years: float = Field(...)
    banking: float = Field(...)
    arpu_90_days: float = Field(...)
    minutes_in: float = Field(...)
    validity_average: float = Field(...)
    average_performance: float = Field(...)
    start_using_months: float = Field(...)
    contacts: float = Field(...)
    high_frequency_contacts: float = Field(...)
    plan_postpaid: float = Field(...)
    sn_banking: float = Field(...)
    digital_index_mean: float = Field(...)
    connected_days: float = Field(...)
    charged_days: float = Field(...)
    apps_days: float = Field(...)
    music_gb: float = Field(...)

    def as_model_row(self) -> List[float]:
        """Return features sorted according to the model column order."""
        data = self.dict()
        return [data[field] for field in config.FEATURE_API_FIELDS]

    def as_model_dict(self) -> dict:
        """Return mapping of original column names => values."""
        raw = {}
        values = self.dict()
        for api_name, column_name in config.API_TO_COLUMN.items():
            raw[column_name] = values[api_name]
        return raw


class PredictionResponse(BaseModel):
    probability: float
    decision: bool
    threshold: float
    top_features: List["FeatureContribution"]


class FeatureContribution(BaseModel):
    name: str
    contribution: float
    direction: str
    value: float


class PitchRequest(FeatureVector):
    customer_id: Optional[str] = Field(None, description="Identifier used only for logging.")
    language: str = Field("es", description="Target language for the generated speech.")
    threshold: float = Field(0.5, description="Decision threshold applied to the model output.")


class PitchResponse(BaseModel):
    customer_id: Optional[str]
    probability: float
    decision: bool
    speech: str
    top_features: List[FeatureContribution]


PredictionResponse.update_forward_refs()

