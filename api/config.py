from __future__ import annotations

import os
from pathlib import Path
from typing import Dict, List, Tuple

# Feature order must match the columns used during training/export.
_FEATURE_PAIRS: List[Tuple[str, str]] = [
    ("state_name", "state_name"),
    ("previous_classification_not_interested", "previous_classification_NOT INTERESTED"),
    ("previous_classification_new_client", "previous_classification_NEW CLIENT"),
    ("previous_classification_not_effective", "previous_classification_NOT EFFECTIVE"),
    ("previous_calls", "previous_calls"),
    ("client_age", "client_age"),
    ("network_age_years", "network_age_years"),
    ("banking", "banking"),
    ("arpu_90_days", "arpu_90_days"),
    ("minutes_in", "minutes_in"),
    ("validity_average", "validity_average"),
    ("average_performance", "average_performance"),
    ("start_using_months", "start_using_months"),
    ("contacts", "contacts"),
    ("high_frequency_contacts", "high_frequency_contacts"),
    ("plan_postpaid", "plan_postpaid"),
    ("sn_banking", "sn_banking"),
    ("digital_index_mean", "digital_index_mean"),
    ("connected_days", "connected_days"),
    ("charged_days", "charged_days"),
    ("apps_days", "apps_days"),
    ("music_gb", "music_gb"),
]

FEATURE_API_FIELDS: List[str] = [api_name for api_name, _ in _FEATURE_PAIRS]
FEATURE_COLUMN_ORDER: List[str] = [col_name for _, col_name in _FEATURE_PAIRS]
API_TO_COLUMN: Dict[str, str] = dict(_FEATURE_PAIRS)

MODEL_PATH = Path(os.getenv("XGB_MODEL_PATH", "models/xgb_sales.json"))
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/api/generate")
OLLAMA_MODEL_NAME = os.getenv("OLLAMA_MODEL", "llama3.1")
OLLAMA_TEMPERATURE = float(os.getenv("OLLAMA_TEMPERATURE", "0.3"))
TOP_K_FEATURES = int(os.getenv("TOP_K_FEATURES", "3"))

REQUEST_TIMEOUT_SECONDS = float(os.getenv("REQUEST_TIMEOUT_SECONDS", "30"))

