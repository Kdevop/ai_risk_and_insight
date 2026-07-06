import pandas as pd
from uuid import uuid4
import os
from datetime import datetime
import numpy as np

# Headless plotting
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns

from app.services.data_access import get_dataframe, _base_metadata

CHART_DIR = "app\static\charts"
os.makedirs(CHART_DIR, exist_ok=True)

# # ---------------------------------------------------------
# # GLOBAL DATAFRAME REGISTRY
# # ---------------------------------------------------------

def retrieve_dataframe(name: str) -> pd.DataFrame | None:
    """Retrieve a DataFrame from the registry."""
    return get_dataframe(name)

# ---------------------------------------------------------
# STATISTICAL ANALYSIS TOOL
# ---------------------------------------------------------

def generate_statistical_analysis(
    df_name: str,
    analysis_type: str,
    columns: list = None,
    x: str = None,
    y: str = None,
    column: str = None,
    z_threshold: float = 3.0
):
    df = retrieve_dataframe(df_name)
    if df is None:
        return {
            "status": "error",
            "analysis_type": "none",
            "df_name": df_name,
            "analysis_result": {},
            "summary": f"DataFrame '{df_name}' not found."
        }

    try:
        # 1. SUMMARY STATS
        if analysis_type == "summary_stats":
            if not columns:
                # default to numeric columns
                columns = df.select_dtypes(include="number").columns.tolist()

            if not columns:
                return {
                    "status": "error",
                    "analysis_type": "summary_stats",
                    "df_name": df_name,
                    "analysis_result": {},
                    "summary": "No numeric columns available to summarize."
                }

            stats = df[columns].describe().to_dict()

            response = {
                "status": "success",
                "analysis_type": "summary_stats",
                "analysis_result": {
                    "metrics": stats,
                    "anomalies": [],
                    "anomaly_count": 0,
                    "image_path": "",
                    "correlation": None,
                    "regression_coefficients": []
                },
                "summary": f"Summary statistics computed for columns: {columns}."
            }
            response.update(_base_metadata(df_name, df))
            return response

        # 2. CORRELATION
        elif analysis_type == "correlation":
            if not x or not y:
                return {
                    "status": "error",
                    "analysis_type": "correlation",
                    "df_name": df_name,
                    "analysis_result": {},
                    "summary": "Parameters 'x' and 'y' are mandatory for correlation."
                }

            try:
                corr_series = df[[x, y]].corr().iloc[0, 1]
                corr = float(corr_series) if not pd.isna(corr_series) else None
            except Exception:
                corr = None

            if corr is None:
                summary = f"Correlation between '{x}' and '{y}' could not be computed."
            else:
                summary = f"Correlation between '{x}' and '{y}' is {corr:.4f}."

            response = {
                "status": "success",
                "analysis_type": "correlation",
                "analysis_result": {
                    "metrics": {"correlation": corr},
                    "anomalies": [],
                    "anomaly_count": 0,
                    "image_path": "",
                    "correlation": corr,
                    "regression_coefficients": []
                },
                "summary": summary
            }
            response.update(_base_metadata(df_name, df))
            return response

        # 3. ANOMALY DETECTION
        elif analysis_type == "anomaly_detection":
            if not column:
                return {
                    "status": "error",
                    "analysis_type": "anomaly_detection",
                    "df_name": df_name,
                    "analysis_result": {},
                    "summary": "Parameter 'column' is mandatory for anomaly detection."
                }

            working_df = df.copy()
            series = pd.to_numeric(working_df[column], errors='coerce')
            mean, std = series.mean(), series.std()

            if std == 0 or pd.isna(std):
                anomalies_preview = []
                anomaly_count = 0
                summary = "Standard deviation is zero or undefined; no anomalies identified."
            else:
                working_df["z_score"] = (series - mean) / std
                anomalies = working_df[abs(working_df["z_score"]) > z_threshold]
                anomalies_sorted = anomalies.reindex(
                    anomalies["z_score"].abs().sort_values(ascending=False).index
                )
                anomalies_preview = anomalies_sorted.head(20).astype(str).to_dict(orient="records")
                anomaly_count = int(len(anomalies))
                summary = f"Detected {anomaly_count} anomalies in '{column}' using z-score threshold {z_threshold}."

            response = {
                "status": "success",
                "analysis_type": "anomaly_detection",
                "analysis_result": {
                    "metrics": {},
                    "anomalies": anomalies_preview,
                    "anomaly_count": anomaly_count,
                    "image_path": "",
                    "correlation": None,
                    "regression_coefficients": []
                },
                "summary": summary
            }
            response.update(_base_metadata(df_name, df))
            return response

        else:
            return {
                "status": "error",
                "analysis_type": "none",
                "df_name": df_name,
                "analysis_result": {},
                "summary": f"Unknown analysis_type '{analysis_type}'."
            }

    except Exception as e:
        return {
            "status": "error",
            "analysis_type": analysis_type,
            "df_name": df_name,
            "analysis_result": {},
            "summary": f"Statistical tool error: {str(e)}"
        }

# ---------------------------------------------------------
# VISUAL ANALYSIS TOOL
# ---------------------------------------------------------
def generate_visual_analysis(
    df_name: str,
    analysis_type: str,
    date_column: str = None,
    value_column: str = None,
    category_column: str = None,
    x: str = None,
    y: str = None,
    degree: int = 1
):
    df = retrieve_dataframe(df_name)
    if df is None:
        return {
            "status": "error",
            "analysis_type": "none",
            "df_name": df_name,
            "analysis_result": {},
            "summary": f"DataFrame '{df_name}' not found."
        }

    try:
        fig, ax = plt.subplots(figsize=(10, 5))
        analysis_result = {}

        # 1. MONTHLY TREND
        if analysis_type == "monthly_trend":
            if not date_column or not value_column:
                plt.close(fig)
                return {
                    "status": "error",
                    "analysis_type": "monthly_trend",
                    "df_name": df_name,
                    "analysis_result": {},
                    "summary": "Missing 'date_column' or 'value_column' for monthly_trend."
                }

            working_df = df.copy()
            working_df[date_column] = pd.to_datetime(working_df[date_column])
            working_df[value_column] = pd.to_numeric(working_df[value_column], errors='coerce')

            monthly = working_df.groupby(working_df[date_column].dt.to_period("M"))[value_column].sum()
            monthly.index = monthly.index.to_timestamp()

            sns.lineplot(x=monthly.index, y=monthly.values, ax=ax, marker='o')
            ax.set_title(f"Monthly Trend of {value_column}")
            ax.set_xlabel("Month")
            ax.set_ylabel(value_column)

            summary = f"Monthly trend chart generated for '{value_column}' over time."

        # 2. CATEGORY BREAKDOWN
        elif analysis_type == "category_breakdown":
            if not category_column or not value_column:
                plt.close(fig)
                return {
                    "status": "error",
                    "analysis_type": "category_breakdown",
                    "df_name": df_name,
                    "analysis_result": {},
                    "summary": "Missing 'category_column' or 'value_column' for category_breakdown."
                }

            working_df = df.copy()
            working_df[value_column] = pd.to_numeric(working_df[value_column], errors='coerce')
            grouped = working_df.groupby(category_column)[value_column].sum().sort_values(ascending=False)

            sns.barplot(x=grouped.index, y=grouped.values, ax=ax)
            ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right')
            ax.set_title(f"Category Breakdown of {value_column}")
            ax.set_xlabel(category_column)
            ax.set_ylabel(value_column)

            summary = f"Category breakdown chart generated for '{value_column}' by '{category_column}'."

        # 3. SCATTER
        elif analysis_type == "scatter":
            if not x or not y:
                plt.close(fig)
                return {
                    "status": "error",
                    "analysis_type": "scatter",
                    "df_name": df_name,
                    "analysis_result": {},
                    "summary": "Missing column targets 'x' or 'y' for scatter plot."
                }

            sns.scatterplot(data=df, x=x, y=y, ax=ax)
            ax.set_title(f"Scatter Plot: {x} vs {y}")
            ax.set_xlabel(x)
            ax.set_ylabel(y)

            summary = f"Scatter plot generated for '{x}' vs '{y}'."

        # 4. REGRESSION
        elif analysis_type == "regression":
            if not x or not y:
                plt.close(fig)
                return {
                    "status": "error",
                    "analysis_type": "regression",
                    "df_name": df_name,
                    "analysis_result": {},
                    "summary": "Missing column targets 'x' or 'y' for regression plot."
                }

            x_vals = pd.to_numeric(df[x], errors='coerce').dropna()
            y_vals = pd.to_numeric(df[y], errors='coerce').dropna()
            common_idx = x_vals.index.intersection(y_vals.index)
            x_vals, y_vals = x_vals.loc[common_idx], y_vals.loc[common_idx]

            if len(x_vals) < degree + 1:
                plt.close(fig)
                return {
                    "status": "error",
                    "analysis_type": "regression",
                    "df_name": df_name,
                    "analysis_result": {},
                    "summary": f"Not enough data points ({len(x_vals)}) to fit a degree-{degree} regression."
                }

            sns.scatterplot(x=x_vals, y=y_vals, ax=ax)

            coeffs = np.polyfit(x_vals, y_vals, degree)
            poly = np.poly1d(coeffs)
            xs = np.linspace(x_vals.min(), x_vals.max(), 200)
            ys = poly(xs)

            ax.plot(xs, ys, color="red", linewidth=2)
            ax.set_title(f"Regression Plot ({degree}-degree): {x} vs {y}")
            ax.set_xlabel(x)
            ax.set_ylabel(y)

            analysis_result["regression_coefficients"] = coeffs.tolist()
            summary = f"Regression plot (degree {degree}) generated for '{x}' vs '{y}'."

        else:
            plt.close(fig)
            return {
                "status": "error",
                "analysis_type": "none",
                "df_name": df_name,
                "analysis_result": {},
                "summary": f"Unknown analysis_type '{analysis_type}'."
            }

        # Save chart
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        filename = f"{analysis_type}_{timestamp}.png"
        filepath = os.path.join(CHART_DIR, filename)
        fig.savefig(filepath, bbox_inches="tight")
        plt.close(fig)

        analysis_result["image_path"] = filepath

        response = {
            "status": "success",
            "analysis_type": analysis_type,
            "analysis_result": analysis_result,
            "summary": summary
        }
        response.update(_base_metadata(df_name, df))
        return response

    except Exception as e:
        return {
            "status": "error",
            "analysis_type": analysis_type,
            "df_name": df_name,
            "analysis_result": {},
            "summary": f"Visual engineering tool error: {str(e)}"
        }

