# models/sla_ml.py
import xgboost as xgb
import numpy as np

class SLAViolationModel:
    def __init__(self):
        self.model = xgb.XGBClassifier(
            n_estimators=100,
            max_depth=4,
            learning_rate=0.1,
            eval_metric="logloss"
        )
        self.trained = False

    def fit(self, df):
        X = df[[
            "eta_minutes",
            "risk_traffic",
            "risk_weather",
            "risk_mech",
            "twin_health"
        ]]

        y = (df["eta_minutes"] > df["sla_minutes"]).astype(int)
        self.model.fit(X, y)
        self.trained = True

    def predict_proba(self, row):
        if not self.trained:
            return 0.0

        X = np.array([[
            row["eta_minutes"],
            row["risk_traffic"],
            row["risk_weather"],
            row["risk_mech"],
            row["twin_health"]
        ]])

        return float(self.model.predict_proba(X)[0, 1])
