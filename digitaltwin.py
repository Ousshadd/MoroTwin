# digitaltwin.py
import random
from utils import clamp
from models.sla_montecarlo import monte_carlo_sla_probability


class TruckDigitalTwin:
    """
    Digital Twin PRO avec détection progressive et réaliste
    """

    def __init__(self, truck_id, truck_data, what_if=None):
        self.truck_id = truck_id
        self.data = truck_data
        self.what_if = what_if or {}

        self.health = float(truck_data.get("twin_health", 100))
        self.risk_traffic = float(truck_data.get("risk_traffic", 0.2))
        self.risk_weather = float(truck_data.get("risk_weather", 0.15))
        self.risk_mech = float(truck_data.get("risk_mech", 0.1))

        self.incident_detected = False
        random.seed(hash(truck_id) % 10000)

    def step(self):
        # What-if
        traffic_peak = self.what_if.get("traffic_peak", False)
        severe_weather = self.what_if.get("severe_weather", False)
        strike = self.what_if.get("strike", False)

        # Dégradation progressive
        self.health -= random.uniform(0.3, 1.0)
        if strike:
            self.health -= 0.7

        self.risk_traffic += random.uniform(0.01, 0.04) + (0.10 if traffic_peak else 0)
        self.risk_weather += random.uniform(0.01, 0.04) + (0.12 if severe_weather else 0)
        self.risk_mech += random.uniform(0.01, 0.03) + (0.05 if self.health < 75 else 0)

        # Clamp
        self.health = clamp(self.health, 0, 100)
        self.risk_traffic = clamp(self.risk_traffic, 0, 1)
        self.risk_weather = clamp(self.risk_weather, 0, 1)
        self.risk_mech = clamp(self.risk_mech, 0, 1)

        self.data.update({
            "twin_health": self.health,
            "risk_traffic": self.risk_traffic,
            "risk_weather": self.risk_weather,
            "risk_mech": self.risk_mech
        })

    def predict_status(self, progress_pct: int):
        # Phase d'observation
        if progress_pct < 10:
            self.step()
            return "IN_TRANSIT"

        if self.incident_detected:
            return "INCIDENT_DETECTED"

        self.step()

        eta = float(self.data.get("eta_minutes", 0))
        sla = float(self.data.get("sla_minutes", 1))

        sla_prob = monte_carlo_sla_probability(
            eta, sla, self.risk_weather, self.risk_traffic
        )
        self.data["sla_violation_prob"] = sla_prob

        combined_risk = (
            0.4 * self.risk_traffic +
            0.35 * self.risk_weather +
            0.25 * self.risk_mech
        )

        # 🎯 Seuils adaptatifs (PRO)
        sla_threshold = 0.65 + (1 - progress_pct / 100) * 0.15
        risk_threshold = 0.55 - (progress_pct / 100) * 0.10

        if sla_prob > sla_threshold or combined_risk > risk_threshold or self.health < 70:
            self.incident_detected = True
            return "INCIDENT_DETECTED"

        return "IN_TRANSIT"

