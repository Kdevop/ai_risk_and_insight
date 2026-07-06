import pandas as pd
from uuid import uuid4

# ---------------------------------------------------------
# GLOBAL DATAFRAME REGISTRY
# ---------------------------------------------------------
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
    df = pd.DataFrame(rows, columns=columns)
    df_name = f"df_{uuid4().hex[:8]}"
    save_dataframe(df_name, df)

    preview = df.head(5).astype(str).values.tolist()

    return {
        "df_name": df_name,
        "columns": list(df.columns),
        "row_count": len(df),
        "preview": preview
    }

# ---------------------------------------------------------
# PREVIEW TOOL (OPTIONAL DIAGNOSTIC)
# ---------------------------------------------------------

def preview_dataframe(df_name: str):
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
        "preview": df.head(5).astype(str).values.tolist()
    }

# ---------------------------------------------------------
# PREVIEW TOOL (OPTIONAL DIAGNOSTIC)
# ---------------------------------------------------------

def _base_metadata(df_name: str, df: pd.DataFrame):
    """Shared metadata block for all tools."""
    return {
        "df_name": df_name,
        "columns": list(df.columns),
        "row_count": len(df),
        "preview": df.head(5).astype(str).values.tolist()
    }