"""Doppelte Auktion mit privaten Werten (Chatterjee-Samuelson): Verlader (Käufer, Wert v) und Spediteur (Verkäufer, Kosten c).

Der Verlader nennt ein Gebot b, der Spediteur eine Forderung a. Ist b >= a, wird gehandelt (Gleichstand: Handel), zum Preis
(1 - kappa) * a + kappa * b; kappa = 1/2 ist der Mittelpunkt. Werte v ~ U[v0, v1] und Kosten c ~ U[c0, c1] sind unabhängig und gleichverteilt,
jeder kennt nur den eigenen Wert und die Verteilung des anderen.

Jede Funktion ist eine Einheit mit expliziten Eingaben und ohne versteckten Zustand. Die Formelfunktionen rechnen nur mit +, -, *, / und Vergleichen:
sie laufen mit float genauso wie mit fractions.Fraction (die Mini-Instanzen der Tests rechnen exakt). Nur die Gitterprüfung (best_response_gap) braucht numpy."""

from __future__ import annotations

from typing import NamedTuple

import numpy as np


class Strategies(NamedTuple):
    """Lineare Strategien: Gebot b(v) = ab + bb * v, Forderung s(c) = as_ + bs * c."""

    ab: float
    bb: float
    as_: float
    bs: float


class Validity(NamedTuple):
    """Gültigkeit des linearen Gleichgewichts: zwei Abstände (Euro), der kleinste maßgebliche Abstand und das Urteil.

    margin_low: niedrigste Forderung s(c0) minus niedrigstes Gebot b(v0); margin_high: höchste Forderung s(c1) minus höchstes Gebot b(v1).
    Maßgeblich sind beide, bei kappa = 0 nur der untere, bei kappa = 1 nur der obere (siehe cs_validity); `margin` ist der kleinste maßgebliche Abstand."""

    margin_low: float
    margin_high: float
    valid: bool
    margin: float


def cs_coefficients(v0, v1, c0, c1, kappa) -> Strategies:
    """Koeffizienten des linearen Gleichgewichts aus den Bedingungen erster Ordnung (Preis = (1 - kappa) * Forderung + kappa * Gebot).

    Der Verkäufer mit Kosten c fordert a = (c + (1 - kappa) * (ab + bb * v1)) / (2 - kappa): bs = 1 / (2 - kappa).
    Der Käufer mit Wert v bietet b = (v + kappa * (as + bs * c0)) / (1 + kappa): bb = 1 / (1 + kappa).
    Die beiden Achsenabschnitte lösen ein lineares 2x2-System. c1 und v0 gehen nicht ein: im Inneren hängt die Beste Antwort nur an v1 und c0."""
    bs = 1 / (2 - kappa)
    bb = 1 / (1 + kappa)
    p = (1 - kappa) / (2 - kappa)
    q = kappa / (1 + kappa)
    ab = (q * p * bb * v1 + q * bs * c0) / (1 - q * p)
    as_ = p * (ab + bb * v1)
    return Strategies(ab, bb, as_, bs)


def bid(v, st: Strategies):
    """Gebot des Verladers mit Wert v."""
    return st.ab + st.bb * v


def ask(c, st: Strategies):
    """Forderung des Spediteurs mit Kosten c."""
    return st.as_ + st.bs * c


def trades(v, c, st: Strategies) -> bool:
    """Handel kommt zustande, wenn das Gebot die Forderung erreicht (Gleichstand: Handel)."""
    return bid(v, st) >= ask(c, st)


def price(v, c, st: Strategies, kappa):
    """Preis bei Handel: (1 - kappa) * Forderung + kappa * Gebot."""
    return (1 - kappa) * ask(c, st) + kappa * bid(v, st)


def cs_validity(v0, v1, c0, c1, kappa, tol=0.0) -> Validity:
    """Wann ist das lineare Profil ein Gleichgewicht? Genau dann, wenn (i) s(c0) >= b(v0) und (ii) s(c1) >= b(v1), wobei (i) bei kappa = 1 und (ii) bei kappa = 0 entfallen.

    Herleitung: Die Auszahlung des Verkäufers ist in der Forderung a zwischen b(v0) und b(v1) konkav, davor wächst sie bei kappa < 1 (sicherer Handel, der Preis steigt mit a),
    danach ist sie null. Seine Formelforderung s(c) ist dort der Gipfel, wenn sie nicht unter b(v0) liegt; liegt sie über b(v1), ist die Auszahlung null und
    keine Abweichung lohnt. Das kleinste s(c) gehört zu c0: Bedingung (i). Beim Käufer liegt das Gipfelgebot b(v) im Bereich [s(c0), s(c1)] oder darunter (kein Handel,
    nichts zu gewinnen); darüber wäre bei kappa > 0 ein niedrigeres Gebot besser (sicherer Handel, der Preis steigt mit dem Gebot), das größte b(v) gehört zu v1: Bedingung (ii).
    Bei kappa = 0 hängt der Preis nicht vom Gebot ab (Abweichen bringt nichts), bei kappa = 1 nicht von der Forderung.
    Für kappa = 1/2 sind (i) und (ii) v0 - c0 <= L/4 und v1 - c1 <= L/4 mit L = v1 - c0. `tol` erlaubt bei float einen Rundungsspielraum (Euro)."""
    st = cs_coefficients(v0, v1, c0, c1, kappa)
    low = ask(c0, st) - bid(v0, st)
    high = ask(c1, st) - bid(v1, st)
    relevant = ([low] if kappa < 1 else []) + ([high] if kappa > 0 else [])
    margin = min(relevant)
    return Validity(low, high, bool(margin >= -tol and v1 > v0 and c1 > c0 and v1 > c0), margin)


def _clamp(x, lo, hi):
    return lo if x < lo else hi if x > hi else x


def region_stats(v0, v1, c0, c1, bb, bs, d):
    """Wahrscheinlichkeit und erwarteter Gewinn (v - c) der Handelsmenge {bb * v - bs * c >= d} im Rechteck [v0, v1] x [c0, c1].

    Für jedes v handeln die Kosten c <= (bb * v - d) / bs =: m * v - e. Das Rechteck zerfällt in drei Streifen: dort, wo diese Grenze unter c0 liegt, kein Handel;
    dazwischen eine quadratische Auszahlung in v; dort, wo sie über c1 liegt, Handel mit jedem Spediteur. Rückgabe (Wahrscheinlichkeit, Gewinn),
    beide bezogen auf die Gleichverteilung im Rechteck (Erwartung über beide Typen)."""
    wv = v1 - v0
    wc = c1 - c0
    m = bb / bs
    e = d / bs
    ua = _clamp((d + bs * c0) / bb, v0, v1)     # ab hier ist c0 handelbar
    ub = _clamp((d + bs * c1) / bb, v0, v1)     # ab hier handelt jeder Spediteur
    prob = (m * (ub * ub - ua * ua) / 2 - (e + c0) * (ub - ua)) / wc + (v1 - ub)
    gain = (
        (m - m * m / 2) * (ub ** 3 - ua ** 3) / 3 + (m * e - e - c0) * (ub * ub - ua * ua) / 2 - (e * e - c0 * c0) / 2 * (ub - ua)
    ) / wc + ((c1 - c0) * (v1 * v1 - ub * ub) / 2 - (c1 * c1 - c0 * c0) / 2 * (v1 - ub)) / wc
    return prob / wv, gain / wv


def region_polygon(v0, v1, c0, c1, bb, bs, d):
    """Eckpunkte (v, c) der Handelsmenge {bb * v - bs * c >= d} im Rechteck (Sutherland-Hodgman gegen eine Halbebene); leer, wenn nichts gehandelt wird.

    Wird für die Zeichnung gebraucht; die Fläche geteilt durch die Rechteckfläche ist die Handelswahrscheinlichkeit (Gegenprobe zu region_stats)."""
    def f(pt):
        return bb * pt[0] - bs * pt[1] - d

    rect = [(v0, c0), (v1, c0), (v1, c1), (v0, c1)]
    out = []
    for i, a in enumerate(rect):
        b = rect[(i + 1) % 4]
        fa, fb = f(a), f(b)
        if fa >= 0:
            out.append(a)
        if (fa >= 0) != (fb >= 0):
            t = fa / (fa - fb)
            out.append((a[0] + t * (b[0] - a[0]), a[1] + t * (b[1] - a[1])))
    return out if len(out) >= 3 else []


def threshold_stats(v0, v1, c0, c1, thr):
    """Handel genau dann, wenn v - c >= thr: (Wahrscheinlichkeit, erwarteter Gewinn)."""
    one = (v1 - v0) / (v1 - v0)         # 1 im Zahlentyp der Bereiche: Fraction bleibt exakt
    return region_stats(v0, v1, c0, c1, one, one, thr)


def cs_stats(v0, v1, c0, c1, kappa):
    """Handelswahrscheinlichkeit und erwarteter Gewinn des linearen Profils (Handel genau bei b(v) >= s(c)); gilt nur im Gültigkeitsbereich."""
    st = cs_coefficients(v0, v1, c0, c1, kappa)
    return region_stats(v0, v1, c0, c1, st.bb, st.bs, st.as_ - st.ab)


def first_best_stats(v0, v1, c0, c1):
    """Erstbestes: Handel genau dann, wenn v >= c."""
    return threshold_stats(v0, v1, c0, c1, 0)


def budget_slack(v0, v1, c0, c1, theta):
    """G(theta) = E[(2 (v - c) - L) * 1{v - c >= theta * L}], L = v1 - c0: Überschuss der Ausgleichsbedingung (Myerson-Satterthwaite, Gleichverteilung).

    2 v - v1 und 2 c - c0 sind die virtuellen Werte; ist G < 0, ist der Handel mit Schwelle theta nicht ausgeglichen finanzierbar."""
    big_l = v1 - c0
    prob, gain = threshold_stats(v0, v1, c0, c1, theta * big_l)
    return 2 * gain - big_l * prob


def second_best_theta(v0, v1, c0, c1, steps=70):
    """Schwelle theta des zweitbesten Mechanismus (Handel genau bei v - c >= theta * L): 0, wenn schon das Erstbeste ausgeglichen finanzierbar ist,
    sonst die Wurzel von G in [0, 1/2) (Bisektion; G wächst dort)."""
    if budget_slack(v0, v1, c0, c1, 0) >= 0:
        return 0
    lo, hi = 0, 0.5
    for _ in range(steps):
        mid = (lo + hi) / 2
        if budget_slack(v0, v1, c0, c1, mid) < 0:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def second_best_stats(v0, v1, c0, c1):
    """Zweitbestes (Handelswahrscheinlichkeit, Gewinn, theta)."""
    theta = second_best_theta(v0, v1, c0, c1)
    prob, gain = threshold_stats(v0, v1, c0, c1, theta * (v1 - c0))
    return prob, gain, theta


def one_price_stats(v0, v1, c0, c1, p):
    """Einpreis-Profil: Verlader mit v >= p bieten p (sonst 0), Spediteure mit c <= p fordern p (sonst die Obergrenze).
    Handel genau bei v >= p >= c, Preis p. Rückgabe (Wahrscheinlichkeit, Gewinn)."""
    pb = _clamp((v1 - p) / (v1 - v0), 0, 1)
    ps = _clamp((p - c0) / (c1 - c0), 0, 1)
    if pb == 0 or ps == 0:
        return 0 * pb, 0 * pb
    mean_v = (_clamp(p, v0, v1) + v1) / 2
    mean_c = (c0 + _clamp(p, c0, c1)) / 2
    return pb * ps, pb * ps * (mean_v - mean_c)


def seller_payoff(a, c, st: Strategies, v0, v1, kappa):
    """Erwartete Auszahlung des Spediteurs mit Kosten c bei Forderung a gegen das lineare Gebot des Verladers (numpy; a darf ein Feld sein)."""
    vstar = np.clip((a - st.ab) / st.bb, v0, v1)
    return ((v1 - vstar) * ((1 - kappa) * a - c + kappa * st.ab) + kappa * st.bb * (v1 ** 2 - vstar ** 2) / 2) / (v1 - v0)


def buyer_payoff(x, v, st: Strategies, c0, c1, kappa):
    """Erwartete Auszahlung des Verladers mit Wert v bei Gebot x gegen die lineare Forderung des Spediteurs (numpy; x darf ein Feld sein)."""
    cstar = np.clip((x - st.as_) / st.bs, c0, c1)
    return ((cstar - c0) * (v - kappa * x - (1 - kappa) * st.as_) - (1 - kappa) * st.bs * (cstar ** 2 - c0 ** 2) / 2) / (c1 - c0)


def best_response_gap(v0, v1, c0, c1, kappa, ntypes=41, ngrid=4001, corners=True) -> tuple[float, float]:
    """Größte Auszahlungslücke zwischen der Formelstrategie und dem besten Gebot bzw. der besten Forderung aus einem Gitter, getrennt für Spediteur und Verlader.

    Über `ntypes` Typen je Seite; das Gitter reicht über die Spanne beider Bereiche mit einem Rand von einem Viertel. Null (bis auf Rundung) heißt:
    am Gitter lohnt keine Abweichung. Auszahlung ohne Handel: 0 (Gebot weit unter, Forderung weit über allen). `corners=True` nimmt die Eckpunkte der Beantwortung
    (niedrigstes und höchstes Gebot bzw. Forderung der anderen Seite) und die Formelstrategie selbst ins Gitter auf; ohne sie ist die Prüfung ein reines Gitter (Orakel der Tests)."""
    st = cs_coefficients(v0, v1, c0, c1, kappa)
    lo = min(v0, c0)
    hi = max(v1, c1)
    grid = np.linspace(lo - 0.25 * (hi - lo), hi + 0.25 * (hi - lo), ngrid)
    gap_seller = 0.0
    gap_buyer = 0.0
    for c in np.linspace(c0, c1, ntypes):
        ref = float(seller_payoff(ask(c, st), c, st, v0, v1, kappa))
        cand = np.concatenate([grid, [bid(v0, st), bid(v1, st), ask(c, st)]]) if corners else grid
        best = max(float(np.max(seller_payoff(cand, c, st, v0, v1, kappa))), 0.0)
        gap_seller = max(gap_seller, best - ref)
    for v in np.linspace(v0, v1, ntypes):
        ref = float(buyer_payoff(bid(v, st), v, st, c0, c1, kappa))
        cand = np.concatenate([grid, [ask(c0, st), ask(c1, st), bid(v, st)]]) if corners else grid
        best = max(float(np.max(buyer_payoff(cand, v, st, c0, c1, kappa))), 0.0)
        gap_buyer = max(gap_buyer, best - ref)
    return gap_seller, gap_buyer


def one_price_gap(v0, v1, c0, c1, p, ask_other=None, ntypes=41, ngrid=4001) -> tuple[float, float]:
    """Beste-Antwort-Lücke des Einpreis-Profils (gleiche Gitterlogik wie best_response_gap), getrennt für Spediteur und Verlader.

    Profil: Verlader mit v >= p bieten p, die anderen weit unter jeder Forderung (kein Handel); Spediteure mit c <= p fordern `ask_other` (Standard p; ein anderer Wert
    ist die Negativkontrolle), die anderen fordern über jedem Gebot. Auszahlung eines Gebots x des Verladers mit Wert v: Handel mit allen Spediteuren c <= p, wenn x >= ask_other
    (Preis (x + ask_other) / 2); Auszahlung einer Forderung a des Spediteurs: Handel mit allen Verladern v >= p, wenn a <= p (Preis (a + p) / 2)."""
    a_eq = p if ask_other is None else ask_other
    ps = float(_clamp((p - c0) / (c1 - c0), 0, 1))      # Anteil der Spediteure, die a_eq fordern
    pb = float(_clamp((v1 - p) / (v1 - v0), 0, 1))      # Anteil der Verlader, die p bieten
    span = max(v1, c1) - min(v0, c0)
    grid = np.linspace(min(v0, c0) - 0.25 * span, max(v1, c1) + 0.25 * span, ngrid)
    never_bid = min(v0, c0) - 0.25 * span - 1.0         # unter jeder Forderung
    never_ask = max(v1, c1) + 0.25 * span + 1.0         # über jedem Gebot

    def buyer_pay(x, v):
        return np.where(x >= a_eq, ps * (v - (x + a_eq) / 2), 0.0)

    def seller_pay(a, c):
        return np.where(a <= p, pb * ((a + p) / 2 - c), 0.0)

    gap_buyer = 0.0
    for v in np.linspace(v0, v1, ntypes):
        ref = float(buyer_pay(np.asarray(p if v >= p else never_bid), v))
        gap_buyer = max(gap_buyer, max(float(np.max(buyer_pay(grid, v))), 0.0) - ref)
    gap_seller = 0.0
    for c in np.linspace(c0, c1, ntypes):
        ref = float(seller_pay(np.asarray(a_eq if c <= p else never_ask), c))
        gap_seller = max(gap_seller, max(float(np.max(seller_pay(grid, c))), 0.0) - ref)
    return gap_seller, gap_buyer
