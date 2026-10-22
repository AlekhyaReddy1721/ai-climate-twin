"""
AI Climate Predictor — uses linear regression + trend extrapolation.
Replace with trained ML models (LSTM, XGBoost) for production.
"""
import numpy as np
from sklearn.linear_model import LinearRegression
from .climate_data import TEMP_ANOMALY_1900_2025, CO2_1900_2025, SEA_LEVEL_1900_2025


def _fit_model(data_dict):
    years = np.array(list(data_dict.keys())).reshape(-1, 1)
    values = np.array(list(data_dict.values()))
    model = LinearRegression()
    model.fit(years, values)
    return model


def predict_temperature(target_year: int) -> dict:
    model = _fit_model(TEMP_ANOMALY_1900_2025)
    base = float(model.predict([[target_year]])[0])
    # Accelerating warming factor post-2025
    accel = max(0, (target_year - 2025) * 0.005)
    predicted = round(base + accel, 2)
    confidence = max(50, 95 - abs(target_year - 2025) * 0.3)
    return {
        "year": target_year,
        "temp_anomaly": predicted,
        "absolute_temp": round(14.0 + predicted, 2),
        "confidence": round(confidence, 1),
        "scenario": _temp_scenario(predicted),
    }


def predict_co2(target_year: int) -> dict:
    model = _fit_model(CO2_1900_2025)
    predicted = round(float(model.predict([[target_year]])[0]), 1)
    return {"year": target_year, "co2_ppm": predicted}


def predict_sea_level(target_year: int) -> dict:
    model = _fit_model(SEA_LEVEL_1900_2025)
    predicted = round(float(model.predict([[target_year]])[0]), 1)
    return {"year": target_year, "sea_level_mm": predicted}


def predict_disasters(region: str, temp_anomaly: float) -> dict:
    # Region-specific base risk profiles — each region has a distinct vulnerability signature
    REGION_PROFILES = {
        "Global":             {"flood": 0.35, "drought": 0.30, "cyclone": 0.25, "heatwave": 0.40, "wildfire": 0.28},
        "Arctic":             {"flood": 0.15, "drought": 0.10, "cyclone": 0.08, "heatwave": 0.20, "wildfire": 0.05},
        "Amazon":             {"flood": 0.72, "drought": 0.55, "cyclone": 0.12, "heatwave": 0.48, "wildfire": 0.60},
        "Sahara":             {"flood": 0.10, "drought": 0.88, "cyclone": 0.05, "heatwave": 0.92, "wildfire": 0.20},
        "South Asia":         {"flood": 0.85, "drought": 0.45, "cyclone": 0.75, "heatwave": 0.80, "wildfire": 0.22},
        "Europe":             {"flood": 0.42, "drought": 0.35, "cyclone": 0.18, "heatwave": 0.50, "wildfire": 0.30},
        "North America":      {"flood": 0.48, "drought": 0.52, "cyclone": 0.45, "heatwave": 0.55, "wildfire": 0.60},
        "Pacific Islands":    {"flood": 0.78, "drought": 0.30, "cyclone": 0.88, "heatwave": 0.60, "wildfire": 0.10},
        "Australia":          {"flood": 0.40, "drought": 0.70, "cyclone": 0.50, "heatwave": 0.82, "wildfire": 0.85},
        "Sub-Saharan Africa": {"flood": 0.55, "drought": 0.78, "cyclone": 0.20, "heatwave": 0.75, "wildfire": 0.45},
    }
    # Sensitivity of each disaster type to temperature anomaly (per °C)
    TEMP_SENSITIVITY = {
        "flood":    0.08,
        "drought":  0.10,
        "cyclone":  0.09,
        "heatwave": 0.14,
        "wildfire": 0.11,
    }
    profile = REGION_PROFILES.get(region, REGION_PROFILES["Global"])
    risks = {
        k: min(0.99, profile[k] + temp_anomaly * TEMP_SENSITIVITY[k])
        for k in profile
    }
    return {
        "region": region,
        "temp_anomaly": temp_anomaly,
        "risks": {k: round(v * 100, 1) for k, v in risks.items()},
        "highest_risk": max(risks, key=risks.get),
    }


def run_simulation(co2_change: float, deforestation: float, renewables: float) -> dict:
    """Simulate environmental impact of parameter changes."""
    temp_impact = co2_change * 0.008 + deforestation * 0.003 - renewables * 0.002
    rainfall_impact = -deforestation * 0.5 - co2_change * 0.1
    biodiversity_impact = -deforestation * 0.8 - temp_impact * 10
    sea_level_impact = temp_impact * 15

    return {
        "inputs": {
            "co2_change_ppm": co2_change,
            "deforestation_percent": deforestation,
            "renewables_percent": renewables,
        },
        "impacts": {
            "temperature_change_c": round(temp_impact, 3),
            "rainfall_change_mm": round(rainfall_impact, 1),
            "biodiversity_loss_percent": round(max(0, -biodiversity_impact), 1),
            "sea_level_rise_mm": round(max(0, sea_level_impact), 1),
        },
        "severity": _severity(temp_impact),
    }


def simulate_policy(carbon_reduction: float, renewable_investment: float, reforestation: float) -> dict:
    temp_benefit = carbon_reduction * 0.006 + reforestation * 0.002 + renewable_investment * 0.003
    co2_benefit = carbon_reduction * 1.2 + reforestation * 0.5
    return {
        "policy": {
            "carbon_reduction_percent": carbon_reduction,
            "renewable_investment_billion": renewable_investment,
            "reforestation_million_ha": reforestation,
        },
        "benefits": {
            "temperature_reduction_c": round(temp_benefit, 3),
            "co2_reduction_ppm": round(co2_benefit, 1),
            "lives_saved_thousands": round(temp_benefit * 500, 0),
        },
        "effectiveness": _effectiveness(temp_benefit),
    }


def _temp_scenario(anomaly):
    if anomaly < 1.0: return "Safe"
    if anomaly < 1.5: return "Moderate Risk"
    if anomaly < 2.0: return "High Risk"
    if anomaly < 3.0: return "Dangerous"
    return "Catastrophic"


def _severity(delta):
    if abs(delta) < 0.1: return "Minimal"
    if abs(delta) < 0.3: return "Moderate"
    if abs(delta) < 0.6: return "Severe"
    return "Catastrophic"


def _effectiveness(benefit):
    if benefit < 0.1: return "Low"
    if benefit < 0.3: return "Moderate"
    if benefit < 0.6: return "High"
    return "Transformative"
