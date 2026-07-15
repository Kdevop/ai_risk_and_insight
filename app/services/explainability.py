from pathlib import Path
from datetime import datetime, timezone
import json
from typing import Any
import numpy as np
import shap
from sklearn.linear_model import LinearRegression

LOCAL_LOG_PATH = Path(__file__).resolve().parent.parent / "logs" / "application_logs.jsonl"
LOCAL_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

def log_event(event_type: str, payload: dict[str, Any]) -> None: 
    record = {
        "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "event_type": event_type, 
        "data": payload
    }

    with LOCAL_LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n") 

def explain_risk_score(features: dict, risk_score: float, weights: dict):
    """
    Explain a risk score using SHAP-style feature contributions.
    """

    feature_names = list(features.keys())

    # Single sample
    X = np.array([[float(features[name]) for name in feature_names]])

    # Background dataset: ZERO baseline
    background = np.zeros_like(X)

    # Build dummy linear regression model
    model = LinearRegression()
    model.coef_ = np.array([float(weights[name]) for name in feature_names])
    model.intercept_ = 0.0

    # SHAP explainer with zero baseline
    explainer = shap.Explainer(model, background)
    shap_values = explainer(X)[0].values
    expected_value = float(explainer.expected_value)

    shap_dict = dict(zip(feature_names, shap_values))

    # Human-readable summary
    sorted_features = sorted(shap_dict.items(), key=lambda kv: abs(kv[1]), reverse=True)
    summary_lines = []
    for name, value in sorted_features:
        direction = "increases" if value > 0 else "reduces"
        summary_lines.append(
            f"{name} {direction} the risk score by approximately {value:.3f}."
        )

    text_summary = (
        f"The customer's risk score is {risk_score:.3f}. "
        f"Relative to the expected baseline of {expected_value:.3f}, "
        f"the main drivers are: "
        + " ".join(summary_lines)
    )

    return {
        "expected_value": expected_value,
        "shap_values": shap_dict,
        "summary": text_summary
    }

