# decision_engine.py
from utils import calculate_eta_impact, clamp, safe_get

ACTIONS = ("WAIT", "REROUTE", "EXPRESS")

def evaluate_actions(row, weights):
    sla = float(safe_get(row, "sla_minutes", 180))
    eta = float(safe_get(row, "eta_minutes", 180))
    penalty = float(safe_get(row, "penalty_mad", 2000))

    health = float(safe_get(row, "twin_health", 100))
    risk_weather = float(safe_get(row, "risk_weather", 0.2))
    risk_traffic = float(safe_get(row, "risk_traffic", 0.2))
    risk_mech = float(safe_get(row, "risk_mech", 0.2))

    sla_prob = float(safe_get(row, "sla_violation_prob", 0.5))

    costs = {
        "WAIT": penalty,
        "REROUTE": float(safe_get(row, "reroute_cost_mad", 1200)),
        "EXPRESS": float(safe_get(row, "express_cost_mad", 2500))
    }

    bad_health = 1.0 - clamp(health / 100, 0, 1)

    reliability = {
        "WAIT": 0.3 * (risk_weather + risk_traffic),
        "REROUTE": 0.2 * (risk_weather + risk_traffic),
        "EXPRESS": 0.4 * bad_health + 0.2 * risk_mech
    }

    scores = {}

    for a in ACTIONS:
        new_eta = calculate_eta_impact(eta, a)
        cost_norm = clamp(costs[a] / max(penalty, 1), 0, 2)

        score = (
            weights["w_cost"] * cost_norm +
            weights["w_sla"] * sla_prob +
            weights["w_rel"] * reliability[a]
        )

        # ❌ Pénaliser WAIT si SLA déjà violé
        if a == "WAIT" and eta > sla:
            score += 0.4

        scores[a] = score

    best_action = min(scores, key=scores.get)
    new_eta = calculate_eta_impact(eta, best_action)
    savings = max(0, penalty - costs[best_action])

    explanation = (
        f"Action={best_action}, ETA_après={new_eta:.1f}, "
        f"P(SLA violation)={sla_prob:.2f}, Health={health:.0f}"
    )

    return best_action, new_eta, savings, explanation, scores[best_action]


def get_best_resolution(row, weights):
    return evaluate_actions(row, weights)
