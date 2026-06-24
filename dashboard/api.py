"""HTTP client for the GymPulse FastAPI backend."""
from __future__ import annotations

import os

import requests

BASE_URL = os.getenv("GYMPULSE_API_URL", "http://localhost:8000")
_TIMEOUT = 10


def _get(path: str, params: dict | None = None) -> dict:
    r = requests.get(f"{BASE_URL}{path}", params=params, timeout=_TIMEOUT)
    r.raise_for_status()
    return r.json()


def health() -> dict:
    return _get("/health")


def list_countries() -> list[str]:
    return _get("/predict/countries")["countries"]


def predict_penetration(
    country: str,
    year: int = 2023,
    include_history: bool = True,
) -> dict:
    return _get(
        "/predict/penetration",
        {"country": country, "year": year, "include_history": str(include_history).lower()},
    )


def predict_batch(
    year: int = 2023,
    region: str | None = None,
    top_n: int | None = None,
) -> dict:
    params: dict = {"year": year}
    if region:
        params["region"] = region
    if top_n:
        params["top_n"] = top_n
    return _get("/predict/penetration/batch", params)


def country_metrics(country: str) -> dict:
    return _get(f"/metrics/{country}")


def predict_whatif(
    country: str,
    year: int = 2023,
    gdp_delta_pct: float = 0.0,
    obesity_delta_pct: float = 0.0,
) -> dict:
    return _get(
        "/predict/whatif",
        {"country": country, "year": year, "gdp_delta_pct": gdp_delta_pct, "obesity_delta_pct": obesity_delta_pct},
    )
