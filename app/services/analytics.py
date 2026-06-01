import pandas as pd
from uuid import uuid4
import matplotlib.pyplot as plt
import seaborn as sns
import os
from datetime import datetime
import numpy as np

CHART_DIR = "static/charts"
os.makedirs(CHART_DIR, exist_ok=True)

# ---------------------------------------------------------
# GLOBAL DATAFRAME REGISTRY
# ---------------------------------------------------------

# Stores DataFrames for the current session.
# Keys: df_name (string)
# Values: Pandas DataFrame
dataframes = {}


def save_dataframe(name: str, df: pd.DataFrame):
    """Save a DataFrame into the session registry."""
    dataframes[name] = df


def get_dataframe(name: str) -> pd.DataFrame | None:
    """Retrieve a DataFrame from the registry."""
    return dataframes.get(name)


# ---------------------------------------------------------
# SQL RESULT REGISTRATION
# ---------------------------------------------------------

def register_sql_result(rows, columns):
    """
    Convert SQL rows + columns into a DataFrame,
    store it in the registry, and return lightweight metadata.
    """
    # Build DataFrame
    df = pd.DataFrame(rows, columns=columns)

    # Generate a unique name for this DataFrame
    df_name = f"df_{uuid4().hex[:8]}"

    # Save to registry
    save_dataframe(df_name, df)

    # Prepare a preview (first 5 rows)
    preview = df.head(5).to_dict(orient="records")

    # Return metadata to the agent
    return {
        "df_name": df_name,
        "columns": columns,
        "row_count": len(df),
        "preview": preview
    }


# ---------------------------------------------------------
# PREVIEW TOOL (OPTIONAL BUT VERY USEFUL)
# ---------------------------------------------------------

def preview_dataframe(df_name: str):
    """
    Return column names, dtypes, and a preview of the DataFrame.
    Useful for the agent to understand the structure before analysis.
    """
    df = get_dataframe(df_name)
    if df is None:
        return {
            "status": "error",
            "message": f"DataFrame '{df_name}' not found."
        }

    return {
        "status": "success",
        "df_name": df_name,
        "columns": list(df.columns),
        "dtypes": df.dtypes.astype(str).to_dict(),
        "preview": df.head(5).to_dict(orient="records")
    }

# ---------------------------------------------------------
# STATISTICAL ANALYSIS TOOL
# ---------------------------------------------------------

def generate_statistical_analysis(df_name: str, analysis_type: str, params: dict):
    """
    Perform non-visual statistical analysis on a stored DataFrame.
    Supported analysis types:
      - summary_stats
      - correlation
      - anomaly_detection
    """

    df = get_dataframe(df_name)
    if df is None:
        return {
            "status": "error",
            "message": f"DataFrame '{df_name}' not found."
        }

    try:
        # -------------------------------------------------
        # 1. SUMMARY STATISTICS
        # -------------------------------------------------
        if analysis_type == "summary_stats":
            cols = params.get("columns", df.select_dtypes(include="number").columns.tolist())
            stats = df[cols].describe().to_dict()
            return {
                "status": "success",
                "analysis_type": "summary_stats",
                "df_name": df_name,
                "metrics": stats,
                "summary": f"Summary statistics computed for {cols}."
            }

        # -------------------------------------------------
        # 2. CORRELATION
        # -------------------------------------------------
        if analysis_type == "correlation":
            x = params["x"]
            y = params["y"]

            corr = df[[x, y]].corr().iloc[0, 1]

            return {
                "status": "success",
                "analysis_type": "correlation",
                "df_name": df_name,
                "metrics": {
                    "correlation": corr
                },
                "summary": f"Correlation between '{x}' and '{y}' is {corr:.4f}."
            }

        # -------------------------------------------------
        # 3. ANOMALY DETECTION (Z-SCORE)
        # -------------------------------------------------
        if analysis_type == "anomaly_detection":
            col = params["column"]
            threshold = params.get("z_threshold", 3.0)

            series = df[col]
            mean = series.mean()
            std = series.std()

            df["z_score"] = (series - mean) / std
            anomalies = df[abs(df["z_score"]) > threshold]

            return {
                "status": "success",
                "analysis_type": "anomaly_detection",
                "df_name": df_name,
                "anomaly_count": len(anomalies),
                "anomalies": anomalies.head(20).to_dict(orient="records"),
                "summary": f"Detected {len(anomalies)} anomalies in '{col}'."
            }

        # -------------------------------------------------
        # UNKNOWN ANALYSIS TYPE
        # -------------------------------------------------
        return {
            "status": "error",
            "message": f"Unknown analysis_type '{analysis_type}'."
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }


# ---------------------------------------------------------
# VISUAL ANALYSIS TOOL
# ---------------------------------------------------------

def _generate_chart_filename(prefix="chart"):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    return f"{prefix}_{timestamp}.png"


def generate_visual_analysis(df_name: str, analysis_type: str, params: dict):
    """
    Generate visual charts from a stored DataFrame.
    Supported analysis types:
      - monthly_trend
      - category_breakdown
      - scatter
      - regression
    """

    df = get_dataframe(df_name)
    if df is None:
        return {
            "status": "error",
            "message": f"DataFrame '{df_name}' not found."
        }

    try:
        # -------------------------------------------------
        # 1. MONTHLY TREND (line chart)
        # -------------------------------------------------
        if analysis_type == "monthly_trend":
            date_col = params["date_column"]
            value_col = params["value_column"]

            df[date_col] = pd.to_datetime(df[date_col])
            monthly = df.groupby(df[date_col].dt.to_period("M"))[value_col].sum()
            monthly.index = monthly.index.to_timestamp()

            plt.figure(figsize=(10, 5))
            sns.lineplot(x=monthly.index, y=monthly.values)
            plt.title(f"Monthly Trend of {value_col}")
            plt.xlabel("Month")
            plt.ylabel(value_col)

            filename = _generate_chart_filename("monthly_trend")
            filepath = os.path.join(CHART_DIR, filename)
            plt.savefig(filepath, bbox_inches="tight")
            plt.close()

            return {
                "status": "success",
                "analysis_type": "monthly_trend",
                "df_name": df_name,
                "image_path": filepath,
                "summary": f"Monthly trend chart generated for '{value_col}'."
            }

        # -------------------------------------------------
        # 2. CATEGORY BREAKDOWN (bar chart)
        # -------------------------------------------------
        if analysis_type == "category_breakdown":
            cat_col = params["category_column"]
            val_col = params["value_column"]

            grouped = df.groupby(cat_col)[val_col].sum().sort_values()

            plt.figure(figsize=(10, 5))
            sns.barplot(x=grouped.index, y=grouped.values)
            plt.xticks(rotation=45)
            plt.title(f"Category Breakdown of {val_col}")
            plt.xlabel(cat_col)
            plt.ylabel(val_col)

            filename = _generate_chart_filename("category_breakdown")
            filepath = os.path.join(CHART_DIR, filename)
            plt.savefig(filepath, bbox_inches="tight")
            plt.close()

            return {
                "status": "success",
                "analysis_type": "category_breakdown",
                "df_name": df_name,
                "image_path": filepath,
                "summary": f"Category breakdown chart generated for '{val_col}'."
            }

        # -------------------------------------------------
        # 3. SCATTER PLOT
        # -------------------------------------------------
        if analysis_type == "scatter":
            x = params["x"]
            y = params["y"]

            plt.figure(figsize=(8, 5))
            sns.scatterplot(data=df, x=x, y=y)
            plt.title(f"Scatter Plot: {x} vs {y}")

            filename = _generate_chart_filename("scatter")
            filepath = os.path.join(CHART_DIR, filename)
            plt.savefig(filepath, bbox_inches="tight")
            plt.close()

            return {
                "status": "success",
                "analysis_type": "scatter",
                "df_name": df_name,
                "image_path": filepath,
                "summary": f"Scatter plot generated for '{x}' vs '{y}'."
            }

        # -------------------------------------------------
        # 4. REGRESSION PLOT (linear or polynomial)
        # -------------------------------------------------
        if analysis_type == "regression":
            x = params["x"]
            y = params["y"]
            degree = params.get("degree", 1)

            plt.figure(figsize=(8, 5))
            sns.scatterplot(data=df, x=x, y=y)

            # Fit polynomial regression
            coeffs = np.polyfit(df[x], df[y], degree)
            poly = np.poly1d(coeffs)

            xs = np.linspace(df[x].min(), df[x].max(), 200)
            ys = poly(xs)

            plt.plot(xs, ys, color="red")
            plt.title(f"Regression Plot ({degree}-degree): {x} vs {y}")

            filename = _generate_chart_filename("regression")
            filepath = os.path.join(CHART_DIR, filename)
            plt.savefig(filepath, bbox_inches="tight")
            plt.close()

            return {
                "status": "success",
                "analysis_type": "regression",
                "df_name": df_name,
                "image_path": filepath,
                "summary": f"{degree}-degree regression plot generated for '{x}' vs '{y}'."
            }

        # -------------------------------------------------
        # UNKNOWN ANALYSIS TYPE
        # -------------------------------------------------
        return {
            "status": "error",
            "message": f"Unknown analysis_type '{analysis_type}'."
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }
