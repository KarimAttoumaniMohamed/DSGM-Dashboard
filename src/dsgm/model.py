import numpy as np
import pandas as pd

def simulate_dsgm(T=20, alpha=0.85, beta=0.10, gamma=0.05, delta=0.12,
                  policy_start=5, P0=0.20):
    """
    Simple DSGM-like time-series:
    P(t+1) = alpha*P(t) + beta*S(t) - gamma*O(t) + delta*pi(t)
    We emulate 3 scenarios: baseline (no policy), moderate, aggressive.
    """
    t = np.arange(T+1)
    P_base = np.zeros(T+1); P_mod = np.zeros(T+1); P_agg = np.zeros(T+1)
    P_base[0] = P_mod[0] = P_agg[0] = P0

    for k in range(T):
        pi_mod = 0.0 if k < policy_start else 0.3
        pi_agg = 0.0 if k < policy_start else 0.6
        S = 0.5; O = 0.4
        P_base[k+1] = alpha*P_base[k] + beta*S - gamma*O + delta*0.0
        P_mod[k+1]  = alpha*P_mod[k]  + beta*S - gamma*O + delta*pi_mod
        P_agg[k+1]  = alpha*P_agg[k]  + beta*S - gamma*O + delta*pi_agg

    return pd.DataFrame({"t": t, "P_baseline": P_base, "P_moderate": P_mod, "P_aggressive": P_agg})
