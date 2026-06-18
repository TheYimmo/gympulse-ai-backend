"""SCRUM-31 — Partición temporal train / validate / test."""

from __future__ import annotations

import pandas as pd

# Corte temporal — train 2001-2021 (incluye COVID), val 2022, test 2023
# El modelo aprende la disrupción COVID directamente en training.
TRAIN_CUTOFF = 2021
VAL_CUTOFF = 2022


def temporal_split(
    df: pd.DataFrame,
    train_cutoff: int = TRAIN_CUTOFF,
    val_cutoff: int = VAL_CUTOFF,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Divide el DataFrame en conjuntos temporales.

    Se respeta la cronología para evitar data-leakage:
    - train : year <= train_cutoff
    - val   : train_cutoff < year <= val_cutoff
    - test  : year > val_cutoff
    """
    train = df[df["year"] <= train_cutoff].reset_index(drop=True)
    val = df[(df["year"] > train_cutoff) & (df["year"] <= val_cutoff)].reset_index(
        drop=True
    )
    test = df[df["year"] > val_cutoff].reset_index(drop=True)
    return train, val, test


def split_xy(
    split: pd.DataFrame,
    feature_cols: list[str],
    target_col: str,
) -> tuple[pd.DataFrame, pd.Series]:
    return split[feature_cols], split[target_col]
