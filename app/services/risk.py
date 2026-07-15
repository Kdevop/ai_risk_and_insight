import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression

from app.services.data_access import get_dataframe
from app.services.analytics import generate_statistical_analysis
from app.services.explainability import explain_risk_score

# ---------------------------------------------------------
# RISK ANALYSIS TOOLS
# ---------------------------------------------------------

import numpy as np

def calculate_volatility(df_name: str):
    """
    Calculate spending volatility safely.
    Isolates out-of-pocket expenses and uses absolute values 
    to avoid mean cancellation and standard deviation skewing.
    """
    tx = get_dataframe(df_name)
    
    error_fallback = {
        "analysis_type": "volatility",
        "analysis_result": {"volatility": 0.0}
    }
    
    if tx is None or "amount" not in tx.columns:
        return error_fallback

    # 1. Convert to float safely
    tx_copy = tx.copy()
    tx_copy["amount"] = tx_copy["amount"].astype(float)
    
    # 2. Filter for actual spending/outflows (negative values)
    # If your dataset represents expenses as positive, drop this filter.
    spending = tx_copy[tx_copy["amount"] < 0]["amount"].abs().tolist()
    
    # Fallback if the user has no outbound transactions in this dataframe
    if len(spending) < 2:
        return error_fallback

    mean_spend = np.mean(spending)
    std_spend = np.std(spending)
    
    # 3. Calculate CV safely
    if mean_spend == 0:
        return error_fallback
        
    vol = round(float(std_spend / mean_spend), 4)

    return {
        "analysis_type": "volatility",  # Match system prompt enum updates
        "analysis_result": {
            "volatility": vol,
            "mean_spending": round(float(mean_spend), 2),
            "std_spending": round(float(std_spend), 2),
            "transaction_count": len(spending)
        }
    }

def calculate_balance_trend(df_name: str, accounts_df_name: str):
    """
    Calculate the linear slope of a customer's total balance trend over time.
    Strict, explicit two-parameter signature to prevent execution layer timeouts.
    """
    transactions_df = get_dataframe(df_name)
    accounts_df = get_dataframe(accounts_df_name)

    error_fallback = {
        "analysis_type": "monthly_trend",
        "analysis_result": {"balance_trend": 0.0}
    }

    if transactions_df is None:
        return error_fallback

    # Fallback: If agent passed an already-joined transaction/account dataframe into the first slot
    if "timestamp" in transactions_df.columns and "amount" in transactions_df.columns and "balance" in transactions_df.columns:
        df = transactions_df.copy()
    else:
        if accounts_df is None or "account_id" not in transactions_df.columns or "balance" not in accounts_df.columns:
            return error_fallback
        df = transactions_df.merge(accounts_df[["account_id", "balance"]], on="account_id", how="left")

    if "timestamp" not in df.columns or "amount" not in df.columns:
        return error_fallback

    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    df = df.dropna(subset=["timestamp", "amount"])

    if df.empty:
        return error_fallback

    # Reconstruct true historical balance sequence moving forward
    df = df.sort_values("timestamp", ascending=True)
    df["balance_progression"] = df["amount"].cumsum()

    if len(df) < 2:
        return error_fallback

    # Linear Regression to extract trend direction/slope
    X = df["timestamp"].astype(np.int64).values.reshape(-1, 1)
    y = df["balance_progression"].values

    model = LinearRegression()
    model.fit(X, y)
    
    slope = float(model.coef_[0])

    return {
        "analysis_type": "monthly_trend",
        "analysis_result": {
            "balance_trend": round(slope * 1e14, 4),
            "direction": "upward" if slope > 0 else "downward" if slope < 0 else "stable",
            "transaction_count": len(df)
        }
    }

def calculate_product_diversity(customer_products_df_name: str, products_df_name: str):
    """
    Calculate product diversity safely using real product ownership.
    Handles both raw dataframes and pre-joined dataframes automatically.
    """
    customer_products_df = get_dataframe(customer_products_df_name)
    products_df = get_dataframe(products_df_name)

    # Standard fallback schema matching the System Prompt enum configuration
    error_fallback = {
        "analysis_type": "none", 
        "analysis_result": {"product_diversity": 0.0}
    }

    if customer_products_df is None or products_df is None:
        return error_fallback

    # Strategy A: If the agent already pre-joined the tables in SQL
    if "category" in customer_products_df.columns:
        owned_categories = customer_products_df["category"].dropna().nunique()
    
    # Strategy B: Fallback to pandas merge if tables are raw
    elif "product_id" in customer_products_df.columns and "product_id" in products_df.columns and "category" in products_df.columns:
        merged = customer_products_df.merge(
            products_df[["product_id", "category"]],
            on="product_id",
            how="left"
        )
        owned_categories = merged["category"].dropna().nunique()
    
    # Neither strategy works because required data columns are missing
    else:
        return error_fallback

    # Calculate total available categories globally
    if "category" in products_df.columns:
        total_categories = products_df["category"].dropna().nunique()
    else:
        total_categories = 0

    if total_categories == 0:
        return error_fallback

    diversity_score = round(float(owned_categories / total_categories), 2)

    return {
        "analysis_type": "none",  # Kept as 'none' to adhere to System Prompt constraints, or update prompt enum
        "analysis_result": {
            "product_diversity": diversity_score,
            "owned_categories_count": owned_categories,
            "total_categories_count": total_categories
        }
    }

def calculate_num_anomalies(df_name: str):
    """Count anomalies using analytics tool."""
    result = generate_statistical_analysis(
        df_name,
        "anomaly_detection",
        column="amount"
    )
    return {"num_anomalies": result["analysis_result"]["anomaly_count"]}


def extract_features(tx_df_name, accounts_df_name, products_df_name, customer_products_df_name):
    """Extract all features needed for risk scoring."""
    return {
        "volatility": calculate_volatility(tx_df_name),
        "balance_trend": calculate_balance_trend(tx_df_name, accounts_df_name),
        "num_anomalies": calculate_num_anomalies(tx_df_name),
        "product_diversity": calculate_product_diversity(customer_products_df_name, products_df_name)
    }

def calculate_risk_score(tx_df_name, accounts_df_name, products_df_name, customer_products_df_name):
    """Weighted risk scoring model with safe dict-unpacking."""
    weights = {
        "volatility": 0.3,
        "balance_trend": -0.2,
        "num_anomalies": 0.4,
        "product_diversity": -0.1,
    }

    # Fetch raw tool results
    features = extract_features(
        tx_df_name,
        accounts_df_name,
        products_df_name,
        customer_products_df_name
    )

    # 1. Safely extract raw float metrics from nested response structures
    raw_metrics = {
        "volatility": features["volatility"].get("analysis_result", {}).get("volatility", 0.0),
        "balance_trend": features["balance_trend"].get("analysis_result", {}).get("balance_trend", 0.0),
        "num_anomalies": features["num_anomalies"].get("num_anomalies", 0.0),
        "product_diversity": features["product_diversity"].get("analysis_result", {}).get("product_diversity", 0.0)
    }

    contributions = {}
    score = 0.0

    # 2. Compute risk scoring safely
    for factor, val in raw_metrics.items():
        w = weights.get(factor, 0)
        contrib = round(float(val * w), 4)
        contributions[factor] = contrib
        score += contrib

    # 3. Scale score to be human-readable and cap between 0 and 100
    # Linear scale offset based on weights
    final_score = max(0.0, min(100.0, round((score * 10) + 50, 2)))

    # SHAP explainability (no recomputation)
    shap_output = explain_risk_score(raw_metrics, final_score, weights)

    return {
        "analysis_type": "risk_score",
        "analysis_result": {
            "risk_score": final_score,
            "contributions": contributions,
            "raw_features": raw_metrics,
            "shap_values": shap_output["shap_values"],
            "expected_value": shap_output["expected_value"],
            "explanation": shap_output["summary"]
        }
    }
