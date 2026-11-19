"""All Plotly charts. Every function returns a Figure; pages just call st.plotly_chart."""
from __future__ import annotations

import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

TEAL, INK, MUTED, GRID = "#0f766e", "#1f2937", "#6b7280", "#e5e7eb"
GOOD, WARN, BAD = "#2f9e44", "#f59f00", "#e03131"
HEALTHY_C, SICK_C = "#2f9e44", "#e03131"
FONT = dict(family="Inter, system-ui, sans-serif", color=INK, size=13)


def _base(fig: go.Figure, height: int, **kw) -> go.Figure:
    fig.update_layout(height=height, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                      font=FONT, margin=dict(l=10, r=10, t=kw.pop("t", 30), b=10), **kw)
    return fig


def risk_color(p: float) -> str:
    return GOOD if p < 0.33 else WARN if p < 0.66 else BAD


def gauge(prob: float) -> go.Figure:
    fig = go.Figure(go.Indicator(
        mode="gauge+number", value=round(prob * 100, 1), number=dict(suffix="%", font=dict(size=46, color=risk_color(prob))),
        gauge=dict(axis=dict(range=[0, 100], tickwidth=1, tickcolor=MUTED, tickvals=[0, 33, 66, 100]),
                   bar=dict(color=INK, thickness=0.22), bgcolor="white", borderwidth=0,
                   steps=[dict(range=[0, 33], color="#d3f2dc"), dict(range=[33, 66], color="#ffe8a3"),
                          dict(range=[66, 100], color="#ffc9c9")])))
    return _base(fig, 250, t=20)


def _display(v, decimals):
    return f"{v:.{decimals}f}" if decimals else f"{v:.0f}"


def range_chart(bundle: dict, cfg: dict, values: dict) -> go.Figure:
    """One row per numeric input: normal band, typical healthy person, typical patient, and YOU."""
    feats = [f for f in cfg["features"] if f["kind"] == "num"]
    # most influential first, keep it readable
    feats = sorted(feats, key=lambda f: -bundle["importance"].get(f["name"], 0))[:8]
    n = len(feats)
    fig = make_subplots(rows=n, cols=1, vertical_spacing=0.11 if n > 4 else 0.14,
                        subplot_titles=[f"{f['label']}" + (f" ({f['unit']})" if f["unit"] else "") for f in feats])
    for i, f in enumerate(feats, start=1):
        s = bundle["stats"][f["name"]]
        lo, hi = s["min"], s["max"]
        pad = (hi - lo) * 0.04
        if f["normal"]:
            band, label = f["normal"], "Normal range"
        else:
            band, label = (s["healthy_p10"], s["healthy_p90"]), "Typical healthy range"
        fig.add_shape(type="rect", x0=band[0], x1=band[1], y0=-0.35, y1=0.35, fillcolor="#d3f2dc",
                      line=dict(width=0), row=i, col=1, layer="below")
        fig.add_trace(go.Scatter(x=[lo, hi], y=[0, 0], mode="lines", line=dict(color=GRID, width=3),
                                 hoverinfo="skip", showlegend=False), row=i, col=1)
        fig.add_trace(go.Scatter(x=[s["healthy_median"]], y=[0], mode="markers", name="Typical healthy person",
                                 marker=dict(symbol="diamond", size=12, color=HEALTHY_C, line=dict(color="white", width=1)),
                                 legendgroup="h", showlegend=(i == 1),
                                 hovertemplate=f"Typical healthy: {_display(s['healthy_median'], f['decimals'])}<extra></extra>"), row=i, col=1)
        fig.add_trace(go.Scatter(x=[s["disease_median"]], y=[0], mode="markers", name="Typical patient",
                                 marker=dict(symbol="diamond", size=12, color=SICK_C, line=dict(color="white", width=1)),
                                 legendgroup="d", showlegend=(i == 1),
                                 hovertemplate=f"Typical patient: {_display(s['disease_median'], f['decimals'])}<extra></extra>"), row=i, col=1)
        v = values[f["name"]]
        outside = (v < band[0]) or (v > band[1])
        fig.add_trace(go.Scatter(x=[v], y=[0], mode="markers", name="You",
                                 marker=dict(symbol="circle", size=17, color=BAD if outside else TEAL, line=dict(color="white", width=2)),
                                 legendgroup="y", showlegend=(i == 1),
                                 hovertemplate=f"You: {_display(v, f['decimals'])}  ({label.lower()} {_display(band[0], f['decimals'])}-{_display(band[1], f['decimals'])})<extra></extra>"), row=i, col=1)
        fig.update_xaxes(range=[min(lo, v) - pad, max(hi, v) + pad], showgrid=False, zeroline=False,
                         tickfont=dict(size=11, color=MUTED), row=i, col=1)
        fig.update_yaxes(visible=False, range=[-0.8, 0.8], row=i, col=1)
    for a in fig.layout.annotations:  # subplot titles -> left aligned, small
        a.update(x=0, xanchor="left", font=dict(size=12, color=INK))
    fig.add_trace(go.Scatter(x=[None], y=[None], mode="markers", name="Normal / typical healthy range",
                             marker=dict(symbol="square", size=12, color="#d3f2dc")), row=1, col=1)
    return _base(fig, 96 * n + 80, t=50, legend=dict(orientation="h", y=1.0 + 0.5 / n, x=0, yanchor="bottom"))


def radar(bundle: dict, cfg: dict, values: dict) -> go.Figure:
    feats = [f for f in cfg["features"] if f["kind"] == "num"]
    feats = sorted(feats, key=lambda f: -bundle["importance"].get(f["name"], 0))[:7]
    if len(feats) < 3:
        return go.Figure()

    def scale(name, v):
        s = bundle["stats"][name]
        return float(np.clip((v - s["min"]) / (s["max"] - s["min"] + 1e-9), 0, 1)) * 100

    labels = [f["label"].split("(")[0].strip() for f in feats]
    def trace(name, vals, color, fill):
        return go.Scatterpolar(r=vals + vals[:1], theta=labels + labels[:1], name=name, fill=fill,
                               line=dict(color=color, width=2.5), fillcolor=color.replace("#", "#") + "22" if fill else None)
    fig = go.Figure()
    fig.add_trace(trace("Typical healthy person", [scale(f["name"], bundle["stats"][f["name"]]["healthy_median"]) for f in feats], HEALTHY_C, "toself"))
    fig.add_trace(trace("Typical patient", [scale(f["name"], bundle["stats"][f["name"]]["disease_median"]) for f in feats], SICK_C, "toself"))
    fig.add_trace(trace("You", [scale(f["name"], values[f["name"]]) for f in feats], TEAL, None))
    fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100], showticklabels=False, gridcolor=GRID),
                                 angularaxis=dict(gridcolor=GRID), bgcolor="rgba(0,0,0,0)"),
                      legend=dict(orientation="h", y=-0.08, x=0.5, xanchor="center"))
    return _base(fig, 400, t=20)


def contributions(df, cfg, top=8) -> go.Figure:
    names = {f["name"]: f["label"].split("(")[0].strip() for f in cfg["features"]}
    d = df.head(top).iloc[::-1]
    fig = go.Figure(go.Bar(
        x=d["effect"] * 100, y=[names[f] for f in d["feature"]], orientation="h",
        marker_color=[BAD if e > 0 else GOOD for e in d["effect"]],
        text=[f"{e * 100:+.1f}" for e in d["effect"]], textposition="outside", cliponaxis=False,
        hovertemplate="%{y}: %{x:+.1f} percentage points<extra></extra>"))
    fig.update_xaxes(title="Change in risk (percentage points)", zeroline=True, zerolinecolor=MUTED, gridcolor=GRID)
    return _base(fig, 60 + 38 * len(d), t=10)


def importance_bar(bundle, cfg, top=10) -> go.Figure:
    names = {f["name"]: f["label"].split("(")[0].strip() for f in cfg["features"]}
    items = sorted(bundle["importance"].items(), key=lambda kv: kv[1])[-top:]
    fig = go.Figure(go.Bar(x=[v for _, v in items], y=[names[k] for k, _ in items], orientation="h", marker_color=TEAL,
                           hovertemplate="%{y}: %{x:.3f}<extra></extra>"))
    fig.update_xaxes(title="Drop in AUC when this input is scrambled", gridcolor=GRID)
    return _base(fig, 60 + 34 * len(items), t=10)


def roc_curve_fig(m: dict) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=m["roc"]["fpr"], y=m["roc"]["tpr"], mode="lines", name=f"Model (AUC {m['auc']:.2f})",
                             line=dict(color=TEAL, width=3), fill="tozeroy", fillcolor="rgba(15,118,110,0.10)"))
    fig.add_trace(go.Scatter(x=[0, 1], y=[0, 1], mode="lines", name="Random guessing", line=dict(color=MUTED, dash="dash")))
    fig.update_xaxes(title="False-alarm rate", gridcolor=GRID, range=[0, 1])
    fig.update_yaxes(title="Cases caught (recall)", gridcolor=GRID, range=[0, 1.02])
    return _base(fig, 340, t=10, legend=dict(orientation="h", y=-0.28))


def confusion_fig(m: dict) -> go.Figure:
    (tn, fp), (fn, tp) = m["confusion"]
    z = [[tn, fp], [fn, tp]]
    fig = go.Figure(go.Heatmap(z=z, x=["Predicted healthy", "Predicted disease"], y=["Actually healthy", "Actually disease"],
                               colorscale=[[0, "#f1f5f4"], [1, TEAL]], showscale=False, text=z, texttemplate="<b>%{text}</b>",
                               textfont=dict(size=22), hoverinfo="skip"))
    fig.update_yaxes(autorange="reversed")
    return _base(fig, 300, t=10)


def distribution(bundle: dict, f: dict, value: float | None = None) -> go.Figure:
    s = bundle["sample"]
    name = f["name"]
    fig = go.Figure()
    kind = f["kind"]
    for flag, label, color in [(0, "Healthy", HEALTHY_C), (1, "Disease", SICK_C)]:
        col = s.loc[s["_disease"] == flag, name].dropna()
        fig.add_trace(go.Histogram(x=col, name=label, marker_color=color, opacity=0.6, histnorm="percent",
                                   nbinsx=min(25, max(4, col.nunique())), hovertemplate="%{x}: %{y:.1f}%<extra>" + label + "</extra>"))
    fig.update_layout(barmode="overlay")
    if value is not None:
        fig.add_vline(x=value, line_width=3, line_color=TEAL, annotation_text="You", annotation_position="top")
    fig.update_xaxes(title=f"{f['label']}" + (f" ({f['unit']})" if f["unit"] else ""), gridcolor=GRID)
    if kind == "cat":
        fig.update_xaxes(tickmode="array", tickvals=list(f["options"].keys()), ticktext=list(f["options"].values()))
    fig.update_yaxes(title="% of group", gridcolor=GRID)
    return _base(fig, 330, t=20, legend=dict(orientation="h", y=1.1, x=0))


def compare_models(rows: list[dict]) -> go.Figure:
    names = [r["name"] for r in rows]
    fig = go.Figure()
    for key, label, color in [("accuracy", "Accuracy", TEAL), ("recall", "Recall (cases caught)", "#e4572e"), ("auc", "AUC", "#6c4ab6")]:
        fig.add_trace(go.Bar(x=names, y=[r[key] * 100 for r in rows], name=label, marker_color=color,
                             hovertemplate="%{x}: %{y:.1f}%<extra>" + label + "</extra>"))
    fig.update_layout(barmode="group")
    fig.update_yaxes(range=[0, 105], title="%", gridcolor=GRID)
    return _base(fig, 360, t=10, legend=dict(orientation="h", y=1.12))
