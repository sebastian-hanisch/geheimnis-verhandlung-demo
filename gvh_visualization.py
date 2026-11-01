"""Plotly-Figuren der Demo (alle Achsen fest, `fixedrange`, damit Touch-Scrollen auf der Seite nicht am Diagramm hängen bleibt)."""

from __future__ import annotations

import numpy as np
import plotly.graph_objects as go

import gvh_constants as C
import gvh_double_auction as DA
from gvh_evaluation import AuctionView, CoaseView, HorizonRow, KappaRow, OnePriceView, de, delta_curve, visible_rounds


def _style(fig: go.Figure, x_title: str, y_title: str, height: int = 380, **layout) -> go.Figure:
    fig.update_layout(margin=dict(l=60, r=20, t=100, b=50), height=height + 60, legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0), **layout)
    fig.update_xaxes(title_text=x_title, fixedrange=True)
    fig.update_yaxes(title_text=y_title, fixedrange=True)
    return fig


def _polygon(fig: go.Figure, pts, name: str, color: str, line: str | None = None):
    if not pts:
        return
    xs = [p[0] for p in pts] + [pts[0][0]]
    ys = [p[1] for p in pts] + [pts[0][1]]
    fig.add_trace(go.Scatter(x=xs, y=ys, mode="lines", fill="toself", fillcolor=color, line=dict(color=line or color, width=1), name=name, hoverinfo="skip"))


def build_region(v: AuctionView) -> go.Figure:
    """Das Rechteck der Typen (v, c): wo effizient gehandelt würde, und wo im Gleichgewicht gehandelt wird."""
    s = v.s
    fig = go.Figure()
    v0, v1, c0, c1 = float(s.v0), float(s.v1), float(s.c0), float(s.c1)
    fig.add_trace(go.Scatter(x=[v0, v1, v1, v0, v0], y=[c0, c0, c1, c1, c0], mode="lines", line=dict(color=C.COLOR_GREY, width=2), name="alle Typen", hoverinfo="skip"))
    if not v.no_gain_possible:
        _polygon(fig, DA.region_polygon(v0, v1, c0, c1, 1.0, 1.0, 0.0), "Erstbestes: Handel bei v ≥ c", C.COLOR_LOSS)
        if v.cs_prob is not None:
            _polygon(fig, DA.region_polygon(v0, v1, c0, c1, v.st.bb, v.st.bs, v.st.as_ - v.st.ab), "Gleichgewicht: Handel bei Gebot ≥ Forderung", C.COLOR_GAIN, C.COLOR_SECOND)
    return _style(fig, "Wert des Verladers v (Euro je Tour)", "Kosten des Spediteurs c (Euro je Tour)", height=400)


def build_strategies(v: AuctionView) -> go.Figure:
    """Gebot b(v) und Forderung s(c) gegen die ehrliche Meldung (Winkelhalbierende)."""
    s = v.s
    fig = go.Figure()
    lo, hi = float(min(s.v0, s.c0)), float(max(s.v1, s.c1))
    fig.add_trace(go.Scatter(x=[lo, hi], y=[lo, hi], mode="lines", line=dict(color=C.COLOR_GREY, dash="dot"), name="ehrlich (Meldung = Wert bzw. Kosten)", hoverinfo="skip"))
    vv = np.array([s.v0, s.v1], dtype=float)
    cc = np.array([s.c0, s.c1], dtype=float)
    fig.add_trace(go.Scatter(x=vv, y=DA.bid(vv, v.st), mode="lines", line=dict(color=C.COLOR_FIRST, width=3), name="Gebot des Verladers b(v)"))
    fig.add_trace(go.Scatter(x=cc, y=DA.ask(cc, v.st), mode="lines", line=dict(color=C.COLOR_EQ, width=3), name="Forderung des Spediteurs s(c)"))
    return _style(fig, "Wert v bzw. Kosten c (Euro je Tour)", "Gebot bzw. Forderung (Euro je Tour)", height=400)


def build_gain_bars(v: AuctionView, best_one_price: float | None = None) -> go.Figure:
    """Erwarteter Gewinn je Tour: Erstbestes, Zweitbestes, Gleichgewicht (wo die Formel gilt), bester Einpreis."""
    names, values, colors = ["Erstbestes"], [v.fb_gain], [C.COLOR_FIRST]
    names.append("Zweitbestes")
    values.append(v.sb_gain)
    colors.append(C.COLOR_SECOND)
    if v.cs_gain is not None:
        names.append("Gleichgewicht (linear)")
        values.append(v.cs_gain)
        colors.append(C.COLOR_EQ)
    if best_one_price is not None:
        names.append("bester Einpreis")
        values.append(best_one_price)
        colors.append(C.COLOR_ONE)
    fig = go.Figure(go.Bar(x=names, y=values, marker_color=colors, text=[de(x) for x in values], textposition="outside"))
    fig = _style(fig, "", "Erwarteter Gewinn je Tour (Euro)", height=360)
    fig.update_yaxes(range=[0, max(values) * 1.18 if max(values) > 0 else 1])
    return fig


def build_kappa_curve(rows: list[KappaRow], v: AuctionView) -> go.Figure:
    ok = [r for r in rows if r.valid]
    fig = go.Figure()
    if ok:
        fig.add_trace(go.Scatter(x=[r.kappa / 100 for r in ok], y=[r.gain for r in ok], mode="lines+markers", line=dict(color=C.COLOR_EQ, width=3), name="Gleichgewicht (linear)"))
    fig.add_trace(go.Scatter(x=[0, 1], y=[v.sb_gain] * 2, mode="lines", line=dict(color=C.COLOR_SECOND, dash="dash"), name="Zweitbestes"))
    fig.add_trace(go.Scatter(x=[0, 1], y=[v.fb_gain] * 2, mode="lines", line=dict(color=C.COLOR_FIRST, dash="dot"), name="Erstbestes"))
    cur = next((r for r in rows if r.kappa == v.s.kappa and r.valid), None)
    if cur:
        fig.add_trace(go.Scatter(x=[cur.kappa / 100], y=[cur.gain], mode="markers", marker=dict(size=13, color="#c0392b", symbol="diamond"), name="gewählt"))
    fig = _style(fig, "Preisregel κ (0: Preis = Forderung, 1: Preis = Gebot)", "Erwarteter Gewinn je Tour (Euro)", height=360)
    fig.update_xaxes(range=[-0.02, 1.02])
    fig.update_yaxes(range=[0, max(v.fb_gain, 1e-9) * 1.1])
    return fig


def build_one_price(v: OnePriceView, cs_gain: float | None) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=v.curve_p, y=v.curve_gain, mode="lines", line=dict(color=C.COLOR_ONE, width=3), name="Einpreis-Gleichgewicht"))
    fig.add_trace(go.Scatter(x=[float(v.curve_p[0]), float(v.curve_p[-1])], y=[v.sb_gain] * 2, mode="lines", line=dict(color=C.COLOR_SECOND, dash="dash"), name="Zweitbestes"))
    if cs_gain is not None:
        fig.add_trace(go.Scatter(x=[float(v.curve_p[0]), float(v.curve_p[-1])], y=[cs_gain] * 2, mode="lines", line=dict(color=C.COLOR_EQ), name="lineares Gleichgewicht"))
    fig.add_trace(go.Scatter(x=[v.s.p], y=[v.gain], mode="markers", marker=dict(size=13, color="#c0392b", symbol="diamond"), name="gewählter Einpreis"))
    fig = _style(fig, "Einpreis p (Euro je Tour)", "Erwarteter Gewinn je Tour (Euro)", height=380)
    fig.update_yaxes(range=[0, max(v.fb_gain, 1e-9) * 1.1])
    return fig


def build_coase_prices(v: CoaseView) -> go.Figure:
    """Preis je Runde (Euro); gestrichelt die jeweils andere Seite des Schalters „Selbstbindung“ (mit Selbstbindung: ein Angebot zum Preis V/2)."""
    sc = v.scale
    fig = go.Figure()
    n_free = visible_rounds(v.path)
    free_x = np.arange(1, n_free + 1)
    free_y = np.array(v.path.price[:n_free]) * sc
    free_mode = "lines+markers" if n_free <= 60 else "lines"
    if v.s.commit:
        fig.add_trace(go.Scatter(x=[1], y=[sc / 2], mode="markers", marker=dict(size=14, color=C.COLOR_SECOND), name="Einmalangebot mit Selbstbindung (V/2)"))
        fig.add_trace(go.Scatter(x=free_x, y=free_y, mode=free_mode, line=dict(color=C.COLOR_EQ, dash="dot"), name="zum Vergleich: ohne Selbstbindung"))
    else:
        fig.add_trace(go.Scatter(x=free_x, y=free_y, mode=free_mode, line=dict(color=C.COLOR_EQ, width=3), name="Preis ohne Selbstbindung"))
        fig.add_trace(go.Scatter(x=[1, max(n_free, 2)], y=[sc / 2] * 2, mode="lines", line=dict(color=C.COLOR_SECOND, dash="dash"), name="Einmalangebot mit Selbstbindung (V/2)"))
    fig = _style(fig, "Runde", "Preis (Euro je Tour)", height=360)
    fig.update_yaxes(range=[0, sc * 0.55])
    return fig


def build_coase_buyers(v: CoaseView) -> go.Figure:
    """Wer kauft wann: Anteil aller Verlader, der in der Runde kauft (Balken), und der aufgelaufene Anteil (Linie)."""
    path = v.shown
    n = visible_rounds(path)
    rounds = np.arange(1, n + 1)
    mass = np.array(path.mass[:n])
    fig = go.Figure()
    fig.add_trace(go.Bar(x=rounds, y=mass * 100, marker_color=C.COLOR_EQ, name="kauft in dieser Runde (%)"))
    fig.add_trace(go.Scatter(x=rounds, y=np.cumsum(mass) * 100, mode="lines", line=dict(color=C.COLOR_FIRST, width=3), name="insgesamt bisher gekauft (%)"))
    fig = _style(fig, "Runde", "Anteil der Verlader (%)", height=360)
    fig.update_yaxes(range=[0, 100.5])
    return fig


def build_limit_curve(curves: dict[int, list[float]], rounds: int, current_delta: float) -> go.Figure:
    """Erster Preis über dem Diskontfaktor für feste Rundenzahlen und im Grenzfall unendlichen Horizonts."""
    pts = delta_curve()
    fig = go.Figure()
    palette = ["#9db7d5", "#6f9bc9", "#4c78a8", "#2f5a85", "#c0392b"]
    for i, (t, prices) in enumerate(sorted(curves.items())):
        chosen = t == rounds
        fig.add_trace(go.Scatter(x=[p[0] for p in pts], y=prices, mode="lines", line=dict(color="#c0392b" if chosen else palette[i % 4], width=3 if chosen else 2),
                                 name=f"T = {t}" + (" (gewählt)" if chosen else "")))
    fig.add_trace(go.Scatter(x=[p[0] for p in pts], y=[p[1] for p in pts], mode="lines", line=dict(color=C.COLOR_EQ, width=3, dash="dash"), name="unendlicher Horizont: s/(1+s), s = √(1−δ)"))
    fig.add_trace(go.Scatter(x=[0, 1], y=[0.5, 0.5], mode="lines", line=dict(color=C.COLOR_SECOND, dash="dot"), name="Einmalangebot (V/2)"))
    fig.add_trace(go.Scatter(x=[current_delta], y=[curves[rounds][int(round(current_delta * 100))]], mode="markers", marker=dict(size=13, color="#c0392b", symbol="diamond"), name="gewähltes δ"))
    fig = _style(fig, "Diskontfaktor δ je Runde", "Erster Preis als Anteil von V", height=400)
    fig.update_xaxes(range=[0, 1])
    fig.update_yaxes(range=[0, 0.55])
    return fig


def build_fixed_horizon(rows: list[HorizonRow], current_dt: float) -> go.Figure:
    fig = go.Figure()
    dts = [r.dt for r in rows]
    fig.add_trace(go.Scatter(x=dts, y=[r.price for r in rows], mode="lines+markers", line=dict(color=C.COLOR_EQ, width=3), name="erster Preis (gerechnet)"))
    fig.add_trace(go.Scatter(x=dts, y=[r.limit_long for r in rows], mode="lines", line=dict(color=C.COLOR_FIRST, dash="dot"), name="Grenzwert bei unendlichem Horizont (s/(1+s))"))
    fig.add_trace(go.Scatter(x=dts, y=[r.limit_fixed for r in rows], mode="lines", line=dict(color=C.COLOR_SECOND, dash="dash"), name="½·e^(−H) (Messhypothese)"))
    cur = next((r for r in rows if abs(r.dt - current_dt) < 1e-12), None)
    if cur:
        fig.add_trace(go.Scatter(x=[cur.dt], y=[cur.price], mode="markers", marker=dict(size=13, color="#c0392b", symbol="diamond"), name="gewählte Rundenlänge"))
    fig = _style(fig, "Rundenlänge Δ (1/r, logarithmisch)", "Erster Preis als Anteil von V", height=380)
    fig.update_xaxes(type="log")
    fig.update_yaxes(range=[0, 0.55])
    return fig
