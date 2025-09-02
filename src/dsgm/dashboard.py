import panel as pn
import pandas as pd
from bokeh.plotting import figure
from dsgm.model import simulate_dsgm

pn.extension("tabulator")

# Controls
alpha = pn.widgets.FloatSlider(name="alpha (persistence)", start=0.6, end=0.98, step=0.01, value=0.85)
beta  = pn.widgets.FloatSlider(name="beta (support)", start=0.0, end=0.3, step=0.01, value=0.10)
gamma = pn.widgets.FloatSlider(name="gamma (obstacles)", start=0.0, end=0.3, step=0.01, value=0.05)
delta = pn.widgets.FloatSlider(name="delta (policy)", start=0.0, end=0.4, step=0.01, value=0.12)
T     = pn.widgets.IntSlider(name="Horizon T", start=5, end=50, step=1, value=20)
policy_start = pn.widgets.IntSlider(name="Policy start t", start=0, end=20, step=1, value=5)
P0    = pn.widgets.FloatSlider(name="Initial P0", start=0.0, end=0.6, step=0.01, value=0.20)

def _plot(df: pd.DataFrame):
    p = figure(height=350, sizing_mode="stretch_width", x_axis_label="t", y_axis_label="Participation index")
    p.line(df["t"], df["P_baseline"], color="gray", line_dash="dashed", legend_label="baseline")
    p.line(df["t"], df["P_moderate"], color="green", legend_label="moderate")
    p.line(df["t"], df["P_aggressive"], color="red", line_dash="dotted", legend_label="aggressive")
    p.legend.location = "bottom_right"
    return p

@pn.depends(alpha, beta, gamma, delta, T, policy_start, P0)
def view(alpha, beta, gamma, delta, T, policy_start, P0):
    df = simulate_dsgm(T=int(T), alpha=alpha, beta=beta, gamma=gamma, delta=delta,
                       policy_start=int(policy_start), P0=P0)
    plot = _plot(df)
    table = pn.widgets.Tabulator(df, height=220)
    return pn.Column(plot, table)

sidebar = pn.Column("## DSGM Controls", alpha, beta, gamma, delta, T, policy_start, P0)
main    = pn.Column("## DSGM Simulation", view)

template = pn.template.MaterialTemplate(
    title="DSGM Dashboard – Inclusive Internet Governance",
    sidebar=[sidebar],
    main=[main],
)

if __name__ == "__main__":
    template.servable()
    pn.serve(template, show=True)
