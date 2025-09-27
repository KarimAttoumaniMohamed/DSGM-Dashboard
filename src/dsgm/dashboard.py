# src/dsgm/dashboard.py

import panel as pn
import pandas as pd

# Bokeh plotting primitives you use in _plot_timeseries()
from bokeh.plotting import figure
from bokeh.models import Span

# Robust import so both run modes work:
#   - panel serve src/dsgm/dashboard.py
#   - python -m src.dsgm.dashboard
try:
    from dsgm.model import simulate_with_metrics, add_metrics_to_timeseries
except ImportError:
    from .model import simulate_with_metrics, add_metrics_to_timeseries


pn.extension("tabulator", "plotly")  # plotly optional; tabulator for tables

# -------------------------
# Controls
# -------------------------
alpha = pn.widgets.FloatSlider(name="α (persistence)", start=0.60, end=0.98, step=0.01, value=0.85)
beta  = pn.widgets.FloatSlider(name="β (support)",     start=0.00, end=0.30, step=0.01, value=0.10)
gamma = pn.widgets.FloatSlider(name="γ (obstacles)",   start=0.00, end=0.30, step=0.01, value=0.05)
delta = pn.widgets.FloatSlider(name="δ (policy)",      start=0.00, end=0.40, step=0.01, value=0.12)

T     = pn.widgets.IntSlider(name="Horizon T", start=5, end=100, step=1, value=20)
policy_start = pn.widgets.IntSlider(name="Policy start t", start=0, end=50, step=1, value=5)
P0    = pn.widgets.FloatSlider(name="Initial P0", start=0.00, end=0.60, step=0.01, value=0.20)

# Choose which columns to compute metrics on.
# NOTE: Using scenarios (baseline/moderate/aggressive) treats them as "groups" for H/I.
# If you later have true stakeholder columns (e.g., gov/private/cso/tech/academia),
# simply replace this list with those column names.
metric_cols = pn.widgets.MultiSelect(
    name="Columns for H/I",
    options=["P_baseline", "P_moderate", "P_aggressive"],
    value=["P_baseline", "P_moderate", "P_aggressive"],
    size=3
)

# Optional target threshold to draw a horizontal reference line
target_threshold = pn.widgets.FloatSlider(
    name="Target participation threshold",
    start=0.0, end=1.0, step=0.01, value=0.60
)

# -------------------------
# Core compute + visuals
# -------------------------
def _plot_timeseries(df: pd.DataFrame):
    p = figure(
        height=360, sizing_mode="stretch_width",
        x_axis_label="t", y_axis_label="Participation index"
    )
    p.line(df["t"], df["P_baseline"],  color="gray",  line_dash="dashed", legend_label="baseline")
    p.line(df["t"], df["P_moderate"],  color="green", legend_label="moderate")
    p.line(df["t"], df["P_aggressive"], color="red",   line_dash="dotted", legend_label="aggressive")
    p.legend.location = "bottom_right"

    # Add horizontal target threshold line
    thresh = Span(location=target_threshold.value, dimension='width', line_color='black', line_dash='dashed')
    p.add_layout(thresh)
    return p

@pn.depends(alpha, beta, gamma, delta, T, policy_start, P0, metric_cols, target_threshold)
def view(alpha, beta, gamma, delta, T, policy_start, P0, metric_cols, _):
    # 1) Run simulation and compute metrics on selected columns
    df = simulate_with_metrics(
        T=int(T),
        cols_for_metrics=list(metric_cols),
        alpha=alpha, beta=beta, gamma=gamma, delta=delta,
        policy_start=int(policy_start), P0=P0
    )

    # 2) Build line plot
    plot = _plot_timeseries(df)

    # 3) Current (last-time-step) metrics
    last = df.iloc[-1]
    H_now = float(last["H_shannon"])
    I_now = float(last["I_inclusivity"])

    # 4) Indicators
    H_ind = pn.indicators.Number(
        name="Shannon Diversity H(t)",
        value=H_now,
        format="{value:.3f}",
        colors=[(0.33, "red"), (0.66, "orange"), (1, "green")],
        sizing_mode="stretch_width"
    )
    I_ind = pn.indicators.Number(
        name="Inclusivity Index I(t)",
        value=I_now,
        format="{value:.3f}",
        colors=[(0.33, "red"), (0.66, "orange"), (1, "green")],
        sizing_mode="stretch_width"
    )

    # 5) Data table
    table = pn.widgets.Tabulator(
        df.round(4),
        height=240,
        pagination=None,
        selectable=False,
        sizing_mode="stretch_width",
    )

    # 6) Help text (brief interpretation)
    help_text = pn.pane.Markdown(
        "**Interpretation**  \n"
        "- **H(t)** close to 1 indicates balanced diversity across the selected columns.  \n"
        "- **I(t)** close to 1 indicates high inclusivity relative to the maximum participation observed.  \n"
        "Use the sliders to explore policy effects on both diversity and inclusivity.",
        sizing_mode="stretch_width",
    )

    return pn.Column(
        pn.Row(H_ind, I_ind),
        plot,
        table,
        help_text,
        sizing_mode="stretch_width"
    )

# -------------------------
# App layout
# -------------------------
sidebar = pn.Column(
    "## DSGM Controls",
    alpha, beta, gamma, delta,
    T, policy_start, P0,
    "## Metrics",
    metric_cols,
    target_threshold,
    sizing_mode="stretch_width"
)

main = pn.Column(
    "## DSGM Simulation — Participation, Diversity H(t), Inclusivity I(t)",
    view,
    sizing_mode="stretch_both"
)

template = pn.template.MaterialTemplate(
    title="DSGM Dashboard — Inclusive Internet Governance",
    sidebar=[sidebar],
    main=[main],
)

# -------------------------
# Entrypoint
# -------------------------
if __name__ == "__main__":
    # Option A: run with Python directly
    #   python -m src.dsgm.dashboard
    template.servable()
    pn.serve(template, show=True)  # opens a local server

# ... your template definition above ...
template = pn.template.MaterialTemplate(
    title="DSGM Dashboard — Inclusive Internet Governance",
    sidebar=[sidebar],
    main=[main],
)

# ✅ This line must be at module level for `panel serve`:
template.servable()

if __name__ == "__main__":
    # For `python -m src.dsgm.dashboard`
    pn.serve(template, show=True)
