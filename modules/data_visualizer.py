import warnings

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from scipy import stats

from modules.style import apply_report_theme, PALETTE


def coerce_datetime_columns(df, min_success_ratio=0.9):
    """Detect text columns that are actually dates and convert them.

    Pandas reads dates from CSV/Excel as plain text, so without this step
    a "date" column never shows up as a datetime column and the time
    series chart option is never available.
    """
    df = df.copy()
    for col in df.select_dtypes(include=["object"]).columns:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)
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


def plot_distribution(df, col):
    """JMP-style "Distribution" panel: histogram stacked over a boxplot for one column."""
    clean = df[col].dropna()

    fig = make_subplots(
        rows=2, cols=1, shared_xaxes=True, row_heights=[0.25, 0.75],
        vertical_spacing=0.05,
    )
    fig.add_trace(
        go.Box(x=clean, boxmean=True, marker_color=PALETTE[0], name=col, showlegend=False),
        row=1, col=1,
    )
    fig.add_trace(
        go.Histogram(x=clean, marker_color=PALETTE[0], opacity=0.85, name=col, showlegend=False),
        row=2, col=1,
    )
    fig.update_layout(title=f"Distribution of {col}", bargap=0.05)
    fig.update_yaxes(showticklabels=False, row=1, col=1)
    fig.update_xaxes(title_text=col, row=2, col=1)
    fig.update_yaxes(title_text="Count", row=2, col=1)
    return apply_report_theme(fig)


def plot_histogram(df, col):
    fig = px.histogram(df, x=col, title=f"Distribution of {col}")
    return apply_report_theme(fig)


def plot_scatter(df, col_x, col_y):
    clean = df[[col_x, col_y]].dropna()

    try:
        fig = px.scatter(df, x=col_x, y=col_y, trendline="ols", title=f"{col_x} vs {col_y}")
        fig.data[1].update(line=dict(color=PALETTE[1], width=2))
    except Exception:
        # statsmodels isn't installed / trendline fit failed - still show the points
        fig = px.scatter(df, x=col_x, y=col_y, title=f"{col_x} vs {col_y}")

    fig.data[0].update(marker=dict(color=PALETTE[0], size=8, line=dict(width=0.5, color="white")))

    if len(clean) > 2:
        r, p = stats.pearsonr(clean[col_x], clean[col_y])
        slope, intercept, _, _, _ = stats.linregress(clean[col_x], clean[col_y])
        sign = "+" if intercept >= 0 else "-"
        fig.add_annotation(
            text=(
                f"y = {slope:.3f}x {sign} {abs(intercept):.3f}<br>"
                f"R² = {r ** 2:.3f}   p = {p:.4f}   n = {len(clean)}"
            ),
            xref="paper", yref="paper",
            x=0.02, y=0.98,
            showarrow=False,
            align="left",
            font=dict(size=13),
            bgcolor="rgba(255,255,255,0.7)",
        )
    return apply_report_theme(fig)


def plot_boxplot(df, cat_col, num_col):
    """Grouped boxplot with a mean marker and each group's sample size, JMP-style."""
    fig = go.Figure()
    order = (
        df.groupby(cat_col)[num_col]
        .median()
        .sort_values(ascending=False)
        .index
    )
    for i, group in enumerate(order):
        values = df.loc[df[cat_col] == group, num_col].dropna()
        fig.add_trace(
            go.Box(
                y=values,
                name=f"{group} (n={len(values)})",
                boxmean=True,
                marker_color=PALETTE[i % len(PALETTE)],
                showlegend=False,
            )
        )
    fig.update_layout(title=f"{num_col} by {cat_col}", yaxis_title=num_col, margin=dict(b=140))
    fig.update_xaxes(tickangle=30)
    return apply_report_theme(fig)


def plot_time_series(df, date_col, num_col):
    df_sorted = df.sort_values(by=date_col)
    fig = px.line(df_sorted, x=date_col, y=num_col, title=f"{num_col} over time", markers=True)
    return apply_report_theme(fig)
