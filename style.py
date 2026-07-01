import plotly.graph_objects as go
import plotly.io as pio

# A clean, muted, colorblind-friendly palette (avoids Plotly's default
# saturated rainbow, which reads as "app demo" rather than "report figure").
PALETTE = ["#2C5F8A", "#C7622A", "#3E8560", "#8A5A9E", "#B0A030", "#6B6B6B"]

_TEMPLATE = go.layout.Template(
    layout=go.Layout(
        font=dict(family="Georgia, 'Times New Roman', serif", size=14, color="#222"),
        title=dict(font=dict(size=18, family="Georgia, 'Times New Roman', serif"), x=0.02, xanchor="left"),
        paper_bgcolor="white",
        plot_bgcolor="white",
        colorway=PALETTE,
        xaxis=dict(showgrid=True, gridcolor="#E5E5E5", zeroline=False, showline=True, linecolor="#888", ticks="outside"),
        yaxis=dict(showgrid=True, gridcolor="#E5E5E5", zeroline=False, showline=True, linecolor="#888", ticks="outside"),
        margin=dict(t=60, l=60, r=30, b=60),
        legend=dict(bordercolor="#DDD", borderwidth=1),
    )
)

pio.templates["report"] = _TEMPLATE


def apply_report_theme(fig):
    """Apply the shared presentation-ready theme to a figure in place."""
    fig.update_layout(template="report")
    return fig


def summary_stats(series):
    """Return a dict of the summary stats JMP shows in its Distribution report."""
    clean = series.dropna()
    return {
        "N": int(clean.shape[0]),
        "Mean": round(clean.mean(), 3) if len(clean) else None,
        "Std Dev": round(clean.std(), 3) if len(clean) else None,
        "Min": round(clean.min(), 3) if len(clean) else None,
        "Median": round(clean.median(), 3) if len(clean) else None,
        "Max": round(clean.max(), 3) if len(clean) else None,
    }


def to_png_bytes(fig, scale=3):
    """Render a figure to high-resolution PNG bytes, suitable for a poster."""
    return fig.to_image(format="png", scale=scale)
