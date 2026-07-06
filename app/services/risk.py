import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression

from app.services.data_access import get_dataframe
from app.services.analytics import generate_statistical_analysis

# ---------------------------------------------------------
# RISK ANALYSIS TOOLS
# ---------------------------------------------------------

def calculate_volatility(tx_df_name: str):
    """Calculate volatility of transaction amounts."""
    tx = get_dataframe(tx_df_name)
    if tx is None or "amount" not in tx.columns:
        return 0.0

    amounts = tx["amount"].astype(float).tolist()
    if len(amounts) < 2:
        return 0.0

    return float(np.std(amounts) / (np.mean(amounts) + 1e-9))


def calculate_balance_trend(tx_df_name: str, accounts_df_name: str):
    """Calculate balance trend using cumulative balances."""
    transactions_df = get_dataframe(tx_df_name)
    accounts_df = get_dataframe(accounts_df_name)

    if transactions_df is None or accounts_df is None:
        return 0.0

    if "account_id" not in transactions_df.columns or "balance" not in accounts_df.columns:
        return 0.0

    if "timestamp" not in transactions_df.columns:
        return 0.0

    df = transactions_df.copy()
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    df = df.dropna(subset=["timestamp"])

    merged = df.merge(
        accounts_df[["account_id", "balance"]],
        on="account_id",
        how="left"
    )

    if merged.empty:
        return 0.0

    merged = merged.sort_values("timestamp")
    merged["cumulative_balance"] = merged["balance"] + merged["amount"].cumsum()

    if len(merged) < 2:
        return 0.0

    X = merged["timestamp"].astype(np.int64).values.reshape(-1, 1)
    y = merged["cumulative_balance"].values

    model = LinearRegression()
    model.fit(X, y)

    return float(model.coef_[0])


def calculate_product_diversity(customer_products_df_name: str, products_df_name: str):
    """Calculate product diversity using real product ownership."""
    customer_products_df = get_dataframe(customer_products_df_name)
    products_df = get_dataframe(products_df_name)

    if customer_products_df is None or products_df is None:
        return 0.0

    # Must have product_id and category
    if "product_id" not in customer_products_df.columns:
        return 0.0
    if "product_id" not in products_df.columns or "category" not in products_df.columns:
        return 0.0

    # Merge ownership → product categories
    merged = customer_products_df.merge(
        products_df[["product_id", "category"]],
        on="product_id",
        how="left"
    )

    # Drop missing categories
    merged = merged.dropna(subset=["category"])
    if merged.empty:
        return 0.0

    # Count distinct categories owned
    owned_categories = merged["category"].nunique()

    # Total categories available in products table
    total_categories = products_df["category"].nunique()

    if total_categories == 0:
        return 0.0

    return float(owned_categories / total_categories)

def calculate_num_anomalies(tx_df_name: str):
    """Count anomalies using analytics tool."""
    result = generate_statistical_analysis(
        tx_df_name,
        "anomaly_detection",
        column="amount"
    )
    return result["analysis_result"]["anomaly_count"]


def extract_features(tx_df_name, accounts_df_name, products_df_name, customer_products_df_name):
    """Extract all features needed for risk scoring."""
    return {
        "volatility": calculate_volatility(tx_df_name),
        "balance_trend": calculate_balance_trend(tx_df_name, accounts_df_name),
        "num_anomalies": calculate_num_anomalies(tx_df_name),
        "product_diversity": calculate_product_diversity(customer_products_df_name, products_df_name)
    }

def calculate_risk_score(tx_df_name, accounts_df_name, products_df_name, customer_products_df_name):
    """Weighted risk scoring model."""
    weights = {
        "volatility": 0.3,
        "balance_trend": -0.2,
        "num_anomalies": 0.4,
        "product_diversity": -0.1,
    }

    features = extract_features(
        tx_df_name,
        accounts_df_name,
        products_df_name,
        customer_products_df_name
    )

    contributions = {}
    score = 0.0

    for factor, value in features.items():
        w = weights.get(factor, 0)
        contrib = value * w
        contributions[factor] = contrib
        score += contrib

    return score, contributions
