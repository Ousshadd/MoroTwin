# utils.py
import numpy as np

def calculate_eta_impact(eta_minutes: float, action: str) -> float:
    """
    Retourne un ETA estimé après action.
    - WAIT : ajoute du temps
    - REROUTE : réduit modérément
    - EXPRESS : réduit fortement
    """
    eta = float(eta_minutes)

    if action == "WAIT":
        return eta + 60  # +1h
    if action == "REROUTE":
        return max(eta * 0.85, eta - 45)  # -15% (min -45min)
    if action == "EXPRESS":
        return max(eta * 0.70, eta - 90)  # -30% (min -90min)

    return eta


# utils.py

def clamp(value, min_value, max_value):
    """
    Limite une valeur entre min_value et max_value
    """
    return max(min_value, min(value, max_value))

def sigmoid(x: float) -> float:
    return 1 / (1 + np.exp(-x))


def safe_get(row, key, default):
    try:
        v = row.get(key, default) if hasattr(row, "get") else row[key]
        if v is None or (isinstance(v, float) and np.isnan(v)):
            return default
        return v
    except Exception:
        return default
