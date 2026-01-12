# models/sla_montecarlo.py
import numpy as np

def monte_carlo_sla_probability(eta, sla, risk_weather, risk_traffic, n=1000):
    """
    Simule des ETA possibles et calcule P(ETA > SLA)
    """
    std = eta * (0.05 + 0.3 * (risk_weather + risk_traffic))
    samples = np.random.normal(eta, std, n)
    return float((samples > sla).mean())
