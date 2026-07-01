import pandas as pd
import plotly.express as px
from scipy import stats


def coerce_datetime_columns(df, min_success_ratio=0.9):
    """Detect text columns that are actually dates and convert them.

    Pandas reads dates from CSV/Excel as plain text, so without this step
    a "date" column never shows up as a datetime column and the time
    series chart option is never available.
    """
    df = df.copy()
    for col in df.select_dtypes(include=["object"]).columns:
        parsed = pd.to_datetime(df[col], errors="coerce")
        non_null = df[col].notna().sum()
        if non_null > 0 and parsed.notna().sum() / non_null >= min_success_ratio:
            df[col] = parsed
    return df


def detect_column_types(df):
    numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
    categorical_cols = df.select_dtypes(include=["object"]).columns.tolist()
    datetime_cols = df.select_dtypes(include=["datetime"]).columns.tolist()
    return numeric_cols, categorical_cols, datetime_cols


def plot_histogram(df, col):
    return px.histogram(df, x=col, title=f"Distribution of {col}")


def plot_scatter(df, col_x, col_y):
    clean = df[[col_x, col_y]].dropna()

    try:
        fig = px.scatter(df, x=col_x, y=col_y, trendline="ols", title=f"{col_x} vs {col_y}")
    except Exception:
        # statsmodels isn't installed / trendline fit failed - still show the points
        fig = px.scatter(df, x=col_x, y=col_y, title=f"{col_x} vs {col_y}")

    if len(clean) > 2:
        r, p = stats.pearsonr(clean[col_x], clean[col_y])
        fig.add_annotation(
            text=f"r = {r:.3f}, p = {p:.4f}",
            xref="paper", yref="paper",
            x=0.05, y=0.95,
            showarrow=False,
            font=dict(size=14),
        )
    return fig


def plot_boxplot(df, cat_col, num_col):
    fig = px.box(df, x=cat_col, y=num_col, title=f"{num_col} by {cat_col}")
    fig.update_xaxes(tickangle=45)
    return fig


def plot_time_series(df, date_col, num_col):
    df_sorted = df.sort_values(by=date_col)
    return px.line(df_sorted, x=date_col, y=num_col, title=f"{num_col} over time")
