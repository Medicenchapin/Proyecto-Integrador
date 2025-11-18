from __future__ import annotations

import json
from typing import Iterable, List

import requests

from api import config, schemas


class OllamaClient:
    """Simple HTTP client for the local Ollama runtime."""

    def __init__(
        self,
        model_name: str = config.OLLAMA_MODEL_NAME,
        base_url: str = config.OLLAMA_BASE_URL,
        temperature: float = config.OLLAMA_TEMPERATURE,
        timeout: float = config.REQUEST_TIMEOUT_SECONDS,
    ) -> None:
        self.model_name = model_name
        self.base_url = base_url
        self.temperature = temperature
        self.timeout = timeout

    def _build_prompt(
        self,
        probability: float,
        features: Iterable[schemas.FeatureContribution],
        language: str,
    ) -> str:
        drivers = "\n".join(
            f"- {feat.name}: valor {feat.value:.3f} ({'+' if feat.contribution >= 0 else '-'}{abs(feat.contribution):.3f})"
            for feat in features
        )
        prompt = f"""
Eres un asesor de telemarketing de Tigo Guatemala.
Tu tarea es resumir los motivos principales de recomendación usando un tono profesional, en idioma {language}.
Probabilidad prevista de éxito: {probability:.2%}.
Principales impulsores:
{drivers}

Redacta un script corto con: apertura, 3 ideas clave, propuesta y cierre con llamada a la acción.
Evita términos técnicos como 'modelo' o 'probabilidad'.
"""
        return prompt.strip()

    def generate_pitch(
        self,
        probability: float,
        features: List[schemas.FeatureContribution],
        language: str = "es",
    ) -> str:
        payload = {
            "model": self.model_name,
            "prompt": self._build_prompt(probability, features, language),
            "stream": False,
            "options": {"temperature": self.temperature},
        }
        response = requests.post(self.base_url, json=payload, timeout=self.timeout)
        response.raise_for_status()
        body = response.json()
        # Ollama returns either `response` or `message`
        if "response" in body:
            return body["response"].strip()
        if "message" in body:
            return body["message"].get("content", "").strip()
        return json.dumps(body)

