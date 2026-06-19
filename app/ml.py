"""Singleton: carga el modelo XGBoost y el dataset una sola vez al startup."""

from __future__ import annotations

import threading
from pathlib import Path
from typing import Optional

import pandas as pd
from xgboost import XGBRegressor

from gympulse.config import DEFAULT_CSV
from gympulse.features import build_feature_matrix
from gympulse.model import save_model_report

_lock = threading.Lock()
_model: Optional[XGBRegressor] = None
_df_raw: Optional[pd.DataFrame] = None
_region_codes: Optional[dict] = None


def get_model() -> tuple[XGBRegressor, pd.DataFrame, dict]:
    """Devuelve (model, df_raw, region_codes); entrena si aún no existe."""
    global _model, _df_raw, _region_codes
    if _model is None:
        with _lock:
            if _model is None:
                _model, _ = save_model_report()
                _df_raw = pd.read_csv(DEFAULT_CSV).sort_values(["country", "year"]).reset_index(drop=True)
                _, _region_codes = build_feature_matrix()
    return _model, _df_raw, _region_codes
