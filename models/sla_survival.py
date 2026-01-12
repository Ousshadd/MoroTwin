# models/sla_survival.py
from lifelines import KaplanMeierFitter
import pandas as pd

class SLASurvivalModel:
    def __init__(self):
        self.kmf = KaplanMeierFitter()
        self.fitted = False

    def fit(self, df: pd.DataFrame):
        """
        duration = eta_minutes
        event = 1 si violation SLA, 0 sinon
        """
        durations = df["eta_minutes"]
        events = (df["eta_minutes"] > df["sla_minutes"]).astype(int)

        self.kmf.fit(durations, event_observed=events)
        self.fitted = True

    def violation_probability(self, eta: float):
        """
        P(violation SLA) = 1 - S(eta)
        """
        if not self.fitted:
            return 0.0

        survival = self.kmf.predict(eta)
        return float(1 - survival)
