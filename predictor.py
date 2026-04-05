import pickle, json
import numpy as np

_model  = None
_scaler = None
_metrics = None

def _load():
    global _model, _scaler, _metrics
    if _model is None:
        _model   = pickle.load(open('models/rf_model.pkl', 'rb'))
        _scaler  = pickle.load(open('models/scaler.pkl',   'rb'))
        _metrics = json.load(open('models/metrics.json'))

FEATURE_NAMES = ['age','sex','trestbps','chol','thalach','smoking','exercise','exang','ca']

def predict_risk(age, sex, bp, chol, hr, smoking, exercise, exang, ca):
    _load()
    import pandas as pd
    features = pd.DataFrame([[age, sex, bp, chol, hr, smoking, exercise, exang, ca]],
                             columns=FEATURE_NAMES)
    features_scaled = _scaler.transform(features)
    prob  = _model.predict_proba(features_scaled)[0][1]
    score = round(prob * 100, 1)
    return score

def get_label_color(score):
    if score >= 65:
        return "High Risk", "#e74c3c"
    elif score >= 35:
        return "Moderate Risk", "#f39c12"
    else:
        return "Low Risk", "#27ae60"

def get_metrics():
    _load()
    return _metrics

def get_recommendations(score, smoking, exercise, chol, bp, age):
    recs = []
    if score >= 65:
        recs.append(("🏥", "Consult a cardiologist immediately", "urgent"))
        recs.append(("💊", "Get a full cardiac evaluation and ECG", "urgent"))
    if smoking == 1:
        recs.append(("🚭", "Quit smoking — it doubles your heart risk", "high"))
    if chol > 200:
        recs.append(("🥗", "Reduce saturated fats; consider a cholesterol test", "medium"))
    if bp > 130:
        recs.append(("🧂", "Reduce salt intake and monitor BP weekly", "medium"))
    if exercise == 0:
        recs.append(("🏃", "Start 30 min of walking daily — reduces risk by 35%", "medium"))
    if age > 50:
        recs.append(("📅", "Schedule an annual heart health checkup", "low"))
    recs.append(("🍎", "Eat more fruits, vegetables, and whole grains", "low"))
    recs.append(("😴", "Get 7–8 hours of sleep every night", "low"))
    return recs
