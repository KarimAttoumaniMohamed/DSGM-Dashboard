# src/dsgm/model.py
# -----------------------------------------------------------------------------
# Dynamic Stakeholder Graph Model (DSGM)
# - Core time-series simulator
# - Shannon diversity and Inclusivity Index utilities
# - Helper to append metrics to a time series
# -----------------------------------------------------------------------------

from __future__ import annotations
import numpy as np
import pandas as pd


# --- Core Simulation ----------------------------------------------------------
def simulate_dsgm(
    T: int = 20,
    alpha: float = 0.85,
    beta: float = 0.10,
    gamma: float = 0.05,
    delta: float = 0.12,
    policy_start: int = 5,
    P0: float = 0.20,
) -> pd.DataFrame:
    """
    Simulate DSGM participation time-series for 3 policy scenarios:
      - baseline (no intervention)
      - moderate intervention (from t >= policy_start)
      - aggressive intervention (from t >= policy_start)

    Recurrence:
        P(t+1) = alpha * P(t) + beta * S(t) - gamma * O(t) + delta * pi(t)

    Parameters
    ----------
    T : int
        Time horizon (inclusive). Returns 0..T (length T+1).
    alpha, beta, gamma, delta : float
        DSGM coefficients: persistence, support, obstacles, policy.
    policy_start : int
        Time step when policy switches on (for moderate/aggressive).
    P0 : float
        Initial participation level at t=0.

    Returns
    -------
    pd.DataFrame
        Columns: t, P_baseline, P_moderate, P_aggressive
    """
    t = np.arange(T + 1, dtype=int)
    P_base = np.zeros(T + 1, dtype=float)
    P_mod = np.zeros(T + 1, dtype=float)
    P_agg = np.zeros(T + 1, dtype=float)

    P_base[0] = P_mod[0] = P_agg[0] = float(P0)

    # Simple constants for illustration; you may parameterize them
    S = 0.5  # institutional support level
    O = 0.4  # structural obstacles level

    for k in range(T):
        # Policy intensity by scenario
        pi_mod = 0.0 if k < policy_start else 0.3
        pi_agg = 0.0 if k < policy_start else 0.6

        # Update rules
        P_base[k + 1] = alpha * P_base[k] + beta * S - gamma * O + delta * 0.0
        P_mod[k + 1] = alpha * P_mod[k] + beta * S - gamma * O + delta * pi_mod
        P_agg[k + 1] = alpha * P_agg[k] + beta * S - gamma * O + delta * pi_agg

    return pd.DataFrame(
        {
            "t": t,
            "P_baseline": P_base,
            "P_moderate": P_mod,
            "P_aggressive": P_agg,
        }
    )


# --- Diversity & Inclusivity Utilities ---------------------------------------
def shannon_diversity(
    proportions: np.ndarray,
    *,
    base: float = np.e,
    normalize: bool = True,
) -> float:
    """
    Compute Shannon diversity H for a distribution over stakeholder groups.

    Parameters
    ----------
    proportions : np.ndarray
        Non-negative values (counts or proportions) per group.
        If counts are provided, they are internally normalized to sum to 1.
    base : float
        Log base (e for nats, 2 for bits, 10 for bans).
    normalize : bool
        If True, returns H / log(n) in [0,1], where n is the number of
        nonzero-mass groups.

    Returns
    -------
    float
        Shannon diversity H (normalized if normalize=True).
    """
    p = np.asarray(proportions, dtype=float)
    total = p.sum()
    if total <= 0:
        return 0.0
    p = p / total

    # Avoid 0*log(0)
    p = p[p > 0]
    if p.size == 0:
        return 0.0

    H = -(p * (np.log(p) / np.log(base))).sum()

    if not normalize:
        return float(H)

    n = p.size
    if n <= 1:
        return 0.0
    H_max = np.log(n) / np.log(base)
    return float(H / H_max)


def inclusivity_index(
    P: np.ndarray,
    weights: np.ndarray | None = None,
) -> float:
    """
    Compute Inclusivity Index:
        I(t) = (1/|V|) * sum_i (P_i / P_max) * w_i

    Parameters
    ----------
    P : np.ndarray
        Non-negative participation levels across |V| stakeholder groups at time t.
    weights : np.ndarray | None
        Optional non-negative weights w_i (equity corrections). If None, uses ones.

    Returns
    -------
    float
        Inclusivity index; typically in [0, 1] when weights are non-negative.
    """
    P = np.asarray(P, dtype=float)
    if P.size == 0:
        return 0.0

    P_max = P.max()
    if P_max <= 0:
        return 0.0

    if weights is None:
        weights = np.ones_like(P, dtype=float)
    else:
        weights = np.asarray(weights, dtype=float)
        if weights.shape != P.shape:
            raise ValueError("weights must have the same shape as P")
        weights = np.clip(weights, a_min=0.0, a_max=None)

    V = P.size
    return float((1.0 / V) * np.sum((P / P_max) * weights))


def diversity_and_inclusivity_from_counts(
    counts: dict[str, float],
    weights: dict[str, float] | None = None,
    *,
    base: float = np.e,
    normalize_diversity: bool = True,
) -> tuple[float, float]:
    """
    Convenience wrapper when your data is per group, e.g.:
        counts = {"gov": 12, "private": 8, "cso": 14, "tech": 6, "academia": 5}
        weights = {"gov": 1.0, "private": 1.0, "cso": 1.2, "tech": 1.1, "academia": 1.1}

    Returns
    -------
    (H, I) : tuple[float, float]
        H = Shannon diversity (normalized if normalize_diversity=True)
        I = Inclusivity index
    """
    keys = list(counts.keys())
    P = np.array([counts[k] for k in keys], dtype=float)

    w = None
    if weights is not None:
        w = np.array([weights.get(k, 1.0) for k in keys], dtype=float)

    H = shannon_diversity(P, base=base, normalize=normalize_diversity)
    I = inclusivity_index(P, weights=w)
    return H, I


def add_metrics_to_timeseries(
    df: pd.DataFrame,
    cols: list[str],
    weights: dict[str, float] | None = None,
    *,
    base: float = np.e,
    normalize_diversity: bool = True,
    out_H: str = "H_shannon",
    out_I: str = "I_inclusivity",
) -> pd.DataFrame:
    """
    Compute Shannon diversity and Inclusivity Index per time step and append to DataFrame.

    Parameters
    ----------
    df : pd.DataFrame
        Must contain time column (e.g., 't') and participation columns for groups in `cols`.
    cols : list[str]
        Column names representing participation per stakeholder group at each t.
        NOTE: Ideally, these should be *groups* (e.g., gov/private/cso/tech/academia).
        If you pass scenario columns (baseline/moderate/aggressive), H/I will describe
        scenario spread rather than stakeholder diversity.
    weights : dict[str, float] | None
        Optional mapping from group/column to weight w_i.
    base : float
        Log base for Shannon diversity.
    normalize_diversity : bool
        Whether to normalize H by log(n).
    out_H : str
        Output column name for Shannon diversity.
    out_I : str
        Output column name for Inclusivity Index.

    Returns
    -------
    pd.DataFrame
        Copy of df with two new columns: out_H and out_I.
    """
    df = df.copy()
    W = None
    if weights is not None:
        W = np.array([weights.get(c, 1.0) for c in cols], dtype=float)

    H_vals, I_vals = [], []
    for _, row in df.iterrows():
        P_vec = row[cols].to_numpy(dtype=float)
        H_vals.append(shannon_diversity(P_vec, base=base, normalize=normalize_diversity))
        I_vals.append(inclusivity_index(P_vec, weights=W))

    df[out_H] = H_vals
    df[out_I] = I_vals
    return df


# --- Optional convenience: simulate + metrics in one call ---------------------
def simulate_with_metrics(
    T: int = 20,
    cols_for_metrics: list[str] | None = None,
    weights: dict[str, float] | None = None,
    **sim_kwargs,
) -> pd.DataFrame:
    """
    Run simulate_dsgm(), then append H_shannon and I_inclusivity across the
    specified columns.

    Parameters
    ----------
    T : int
        Time horizon for simulation.
    cols_for_metrics : list[str] | None
        Columns to use for H/I. Default: ["P_baseline","P_moderate","P_aggressive"].
        Prefer stakeholder-group columns if available.
    weights : dict[str, float] | None
        Optional weights for inclusivity index (per column).
    sim_kwargs : dict
        Forwarded to simulate_dsgm().

    Returns
    -------
    pd.DataFrame
        Simulation frame with H_shannon and I_inclusivity added.
    """
    df = simulate_dsgm(T=T, **sim_kwargs)
    if cols_for_metrics is None:
        cols_for_metrics = ["P_baseline", "P_moderate", "P_aggressive"]
    return add_metrics_to_timeseries(df, cols=cols_for_metrics, weights=weights)
