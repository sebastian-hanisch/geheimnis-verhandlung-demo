"""Orakel der doppelten Auktion: andere Rechenwege als die Formeln der Demo.

(1) Beste Antwort durch numerische Integration über die Gegenseite (nicht die geschlossene Auszahlung der Demo) und durch ein Gitter in Brüchen;
(2) Handelswahrscheinlichkeit und Gewinn durch Integration über v mit exakter innerer Integration über c (nicht die Streifenformel);
(3) Zweitbestes durch ein lineares Programm (interim anreizverträglich, im Erwartungswert ausgeglichen, Typenmitten, Richardson aus zwei Feinheiten);
(4) das Gültigkeitskriterium gegen die numerische Lücke an Zufallsinstanzen (SplitMix64, feste Zufalls-Seeds);
(5) Einpreis-Gleichgewichte gegen ein Gitter, mit Negativkontrolle.
scipy nur hier (Orakel), nie in der Demo."""

from fractions import Fraction as F

import numpy as np
import pytest

import gvh_double_auction as DA
from gvh_rng import SplitMix64

linprog = pytest.importorskip("scipy.optimize").linprog


# --- (1) Beste Antwort ------------------------------------------------------------------------------------------------------------------------------
def _seller_payoff_by_integration(a, c, st, v0, v1, kappa, n=40_001):
    """Mittelwert über Käufer-Werte v (Mittelpunktregel): Handel, wenn b(v) >= a, zum Preis (1 - kappa) a + kappa b(v); die Kosten c fallen bei Handel an."""
    v = v0 + (v1 - v0) * (np.arange(n) + 0.5) / n
    b = st.ab + st.bb * v
    return float(np.mean(np.where(b >= a, (1 - kappa) * a + kappa * b - c, 0.0)))


def _buyer_payoff_by_integration(x, v, st, c0, c1, kappa, n=40_001):
    c = c0 + (c1 - c0) * (np.arange(n) + 0.5) / n
    s = st.as_ + st.bs * c
    return float(np.mean(np.where(x >= s, v - kappa * x - (1 - kappa) * s, 0.0)))


CASES = [
    ((0.0, 1.0, 0.0, 1.0), 0.5), ((0.0, 1.0, 0.0, 1.0), 0.25), ((0.0, 1.0, 0.0, 1.0), 0.8), ((0.0, 1.0, 0.0, 1.0), 0.0),
    ((1 / 3, 4 / 3, 0.0, 1.0), 0.5), ((0.0, 1.5, 0.5, 1.5), 0.5), ((0.2, 1.2, 0.0, 1.0), 0.5),
]


@pytest.mark.parametrize("rng,kappa", CASES)
def test_formula_strategies_are_best_responses_by_numerical_integration(rng, kappa):
    v0, v1, c0, c1 = rng
    st = DA.cs_coefficients(v0, v1, c0, c1, kappa)
    L = v1 - c0
    assert DA.cs_validity(v0, v1, c0, c1, kappa, tol=1e-9).valid
    grid = np.linspace(c0 - 0.2 * L, v1 + 0.2 * L, 401)
    for c in np.linspace(c0, c1, 4):
        pay = np.array([_seller_payoff_by_integration(a, c, st, v0, v1, kappa) for a in grid])
        ref = _seller_payoff_by_integration(DA.ask(c, st), c, st, v0, v1, kappa)
        assert max(pay.max(), 0.0) - ref < 2e-4 * L
        assert abs(grid[pay.argmax()] - DA.ask(c, st)) < 0.02 * L if pay.max() > 0 else True
    for v in np.linspace(v0, v1, 4):
        pay = np.array([_buyer_payoff_by_integration(x, v, st, c0, c1, kappa) for x in grid])
        ref = _buyer_payoff_by_integration(DA.bid(v, st), v, st, c0, c1, kappa)
        assert max(pay.max(), 0.0) - ref < 2e-4 * L


def test_negative_control_an_honest_ask_is_not_a_best_response():
    st = DA.cs_coefficients(0.0, 1.0, 0.0, 1.0, 0.5)
    honest = _seller_payoff_by_integration(0.25, 0.25, st, 0.0, 1.0, 0.5)
    eq = _seller_payoff_by_integration(DA.ask(0.25, st), 0.25, st, 0.0, 1.0, 0.5)
    assert eq == pytest.approx(1 / 8, abs=1e-4) and honest == pytest.approx(3 / 32, abs=1e-4) and eq - honest > 0.03


def test_best_responses_on_a_grid_in_fractions_have_gap_zero():
    """Gitter 1/120 in Brüchen (die Gleichgewichtsantworten (2k + 15)/60 und (2k + 5)/60 liegen darauf), 11 Typen je Seite: kein Typ gewinnt durch Abweichen, exakt."""
    st = DA.cs_coefficients(F(0), F(1), F(0), F(1), F(1, 2))
    grid = np.array([F(k, 120) for k in range(-30, 151)], dtype=object)
    for k in range(0, 21, 2):
        c = F(k, 20)
        ref = DA.seller_payoff(DA.ask(c, st), c, st, F(0), F(1), F(1, 2))
        best = max(max(DA.seller_payoff(a, c, st, F(0), F(1), F(1, 2)) for a in grid), 0)
        assert best == ref
        v = F(k, 20)
        refb = DA.buyer_payoff(DA.bid(v, st), v, st, F(0), F(1), F(1, 2))
        bestb = max(max(DA.buyer_payoff(x, v, st, F(0), F(1), F(1, 2)) for x in grid), 0)
        assert bestb == refb


@pytest.mark.parametrize("v0,expect_gap", [(0.0, False), (1 / 3, False), (0.4, True), (0.6, True)])
def test_grid_gap_separates_valid_from_invalid_in_the_shift_experiment(v0, expect_gap):
    """Käufer U[s, 1 + s] gegen Verkäufer U[0, 1] (Verschiebung s = v0): gültig bis s = 1/3, ungültig ab 0,4. Reines Gitter ohne Eckpunkte."""
    gs, gb = DA.best_response_gap(v0, 1 + v0, 0.0, 1.0, 0.5, ntypes=21, ngrid=2001, corners=False)
    assert (max(gs, gb) > 1e-6) == expect_gap


# --- (2) Wahrscheinlichkeit und Gewinn ---------------------------------------------------------------------------------------------------------------
def _stats_by_inner_integration(v0, v1, c0, c1, bb, bs, d, n=200_001):
    """Über v mit Mittelpunktregel, für jedes v die Kosten c in [c0, min(c1, (bb v - d)/bs)] exakt integriert."""
    v = v0 + (v1 - v0) * (np.arange(n) + 0.5) / n
    cs = np.clip((bb * v - d) / bs, c0, c1)
    wc = c1 - c0
    prob = np.mean((cs - c0) / wc)
    gain = np.mean((v * (cs - c0) - (cs ** 2 - c0 ** 2) / 2) / wc)
    return float(prob), float(gain)


@pytest.mark.parametrize("rng,kappa", CASES)
def test_cs_stats_match_inner_integration(rng, kappa):
    v0, v1, c0, c1 = rng
    st = DA.cs_coefficients(v0, v1, c0, c1, kappa)
    prob, gain = DA.cs_stats(v0, v1, c0, c1, kappa)
    p2, g2 = _stats_by_inner_integration(v0, v1, c0, c1, st.bb, st.bs, st.as_ - st.ab)
    assert prob == pytest.approx(p2, abs=1e-9) and gain == pytest.approx(g2, abs=1e-9)


def test_region_stats_match_integration_also_when_the_line_is_clipped():
    """Zufällige Halbebenen, darunter solche, die das Rechteck an einer Ecke, an zwei Seiten oder gar nicht treffen."""
    rng = SplitMix64(7)
    for _ in range(60):
        v0, c0 = 2 * rng.uniform() - 1, 2 * rng.uniform() - 1
        v1, c1 = v0 + 0.2 + rng.uniform(), c0 + 0.2 + rng.uniform()
        bb, bs, d = 0.3 + rng.uniform(), 0.3 + rng.uniform(), 2 * rng.uniform() - 0.8
        a = DA.region_stats(v0, v1, c0, c1, bb, bs, d)
        b = _stats_by_inner_integration(v0, v1, c0, c1, bb, bs, d)
        assert a[0] == pytest.approx(b[0], abs=1e-8) and a[1] == pytest.approx(b[1], abs=1e-8)
        poly = DA.region_polygon(v0, v1, c0, c1, bb, bs, d)
        area = abs(sum(p[0] * q[1] - q[0] * p[1] for p, q in zip(poly, poly[1:] + poly[:1]))) / 2 if poly else 0.0
        assert area / ((v1 - v0) * (c1 - c0)) == pytest.approx(a[0], abs=1e-9)


def test_closed_form_for_the_valid_triangle():
    """Im Gültigkeitsbereich (kappa = 1/2) ist die Handelsmenge ein Dreieck mit Katheten 3L/4 im Rechteck: Wahrscheinlichkeit 9 L^2/(32 Wv Wc), Gewinn 9 L^3/(64 Wv Wc)."""
    rng = SplitMix64(11)
    done = 0
    while done < 40:
        v0, c0 = rng.uniform(), 2 * rng.uniform() - 0.5
        v1, c1 = v0 + 0.2 + 2 * rng.uniform(), c0 + 0.2 + 2 * rng.uniform()
        L = v1 - c0
        if L <= 0.05 or not DA.cs_validity(v0, v1, c0, c1, 0.5, tol=1e-12).valid:
            continue
        done += 1
        prob, gain = DA.cs_stats(v0, v1, c0, c1, 0.5)
        area = (v1 - v0) * (c1 - c0)
        assert prob == pytest.approx(9 * L ** 2 / (32 * area), rel=1e-9) and gain == pytest.approx(9 * L ** 3 / (64 * area), rel=1e-9)


# --- (3) Zweitbestes durch ein lineares Programm ---------------------------------------------------------------------------------------------------
def _second_best_lp(v0, v1, c0, c1, k):
    """Interim anreizverträglicher, interim individuell rationaler, im Erwartungswert ausgeglichener Handel auf Typenmitten (k je Seite); maximiert den erwarteten Gewinn.

    Variablen x[i, j] (Handelswahrscheinlichkeit), Nutzen des Käufers u_b[i] = v_i * X_i - P_i, des Verkäufers u_s[j]. Rückgabe (Zweitbestes, Erstbestes) dieses Gitters."""
    v = v0 + (v1 - v0) * (np.arange(k) + 0.5) / k
    c = c0 + (c1 - c0) * (np.arange(k) + 0.5) / k
    nx = k * k
    nv = nx + 2 * k
    obj = np.zeros(nv)
    for i in range(k):
        for j in range(k):
            obj[i * k + j] = -(v[i] - c[j]) / (k * k)
    rows, rhs = [], []
    for i in range(k):                          # Käufer: wahre Meldung i gegen Meldung i2
        for i2 in range(k):
            if i2 == i:
                continue
            row = np.zeros(nv)
            for j in range(k):
                row[i * k + j] += -v[i] / k
                row[i2 * k + j] += v[i] / k
            row[nx + i] += 1
            row[nx + i2] += -1
            rows.append(row)
            rhs.append(0)
        row = np.zeros(nv)
        for j in range(k):
            row[i * k + j] += -v[i] / k
        row[nx + i] += 1
        rows.append(row)
        rhs.append(0)
    for j in range(k):                          # Verkäufer
        for j2 in range(k):
            if j2 == j:
                continue
            row = np.zeros(nv)
            row[nx + k + j] += -1
            row[nx + k + j2] += 1
            for i in range(k):
                row[i * k + j] += c[j] / k
                row[i * k + j2] += -c[j] / k
            rows.append(row)
            rhs.append(0)
        row = np.zeros(nv)
        row[nx + k + j] += -1
        for i in range(k):
            row[i * k + j] += c[j] / k
        rows.append(row)
        rhs.append(0)
    row = np.zeros(nv)                          # Ausgleich im Erwartungswert: Zahlungen des Käufers >= Zahlungen an den Verkäufer
    for i in range(k):
        row[nx + i] += -1 / k
    for j in range(k):
        row[nx + k + j] += 1 / k
    rows.append(row)
    rhs.append(0)
    res = linprog(obj, A_ub=np.array(rows), b_ub=np.array(rhs), bounds=[(0, 1)] * nx + [(None, None)] * (2 * k), method="highs")
    assert res.status == 0
    first = sum(max(v[i] - c[j], 0) for i in range(k) for j in range(k)) / (k * k)
    return -res.fun, first


def _lp_richardson(v0, v1, c0, c1, ks=(24, 32)):
    a, b = ks
    ra, rb = _second_best_lp(v0, v1, c0, c1, a), _second_best_lp(v0, v1, c0, c1, b)
    return (b * rb[0] - a * ra[0]) / (b - a), (b * rb[1] - a * ra[1]) / (b - a)


@pytest.mark.parametrize("rng", [(0.0, 1.0, 0.0, 1.0), (0.2, 1.2, 0.0, 1.0), (0.0, 0.5, 0.0, 1.0), (0.6, 1.6, 0.0, 1.0)])
def test_second_best_matches_the_linear_program(rng):
    sb_lp, fb_lp = _lp_richardson(*rng)
    _p, sb, _theta = DA.second_best_stats(*rng)
    _fp, fb = DA.first_best_stats(*rng)
    assert sb == pytest.approx(sb_lp, abs=2e-3 * (rng[1] - rng[2]) ** 1)
    assert fb == pytest.approx(fb_lp, abs=2e-3 * (rng[1] - rng[2]))


def test_the_linear_program_itself_on_a_hand_case():
    """Werte U[1, 2], Kosten U[0, 1]: jede Tour lohnt sich, der Festpreis 1 macht alle IR-Bedingungen wahr und gleicht das Budget aus; Erst- und Zweitbestes sind E[v - c] = 3/2 - 1/2 = 1."""
    sb, fb = _second_best_lp(1.0, 2.0, 0.0, 1.0, 8)
    assert sb == pytest.approx(1.0, abs=1e-6) and fb == pytest.approx(1.0, abs=1e-6)


# --- (4) Gültigkeitskriterium gegen die numerische Lücke --------------------------------------------------------------------------------------------
def _random_instances(seed, count, random_kappa):
    """random_kappa: False (kappa = 1/2), True (kappa in [0,1; 0,9]) oder "edge" (kappa abwechselnd 0 und 1)."""
    rng = SplitMix64(seed)
    out = []
    for _ in range(count):
        v0 = rng.uniform()
        v1 = v0 + 0.2 + 1.8 * rng.uniform()
        c0 = -0.5 + 1.5 * rng.uniform()
        c1 = c0 + 0.2 + 1.8 * rng.uniform()
        kappa = (len(out) % 2) * 1.0 if random_kappa == "edge" else (0.1 + 0.8 * rng.uniform() if random_kappa else 0.5)
        if v1 - c0 > 0.05:
            out.append((v0, v1, c0, c1, kappa))
    return out


def validity_agreement(random_kappa):
    """(übereinstimmend, davon gültig, ausgelassen) für die Zufalls-Seeds 11 und 22 mit je 30 Instanzen, Gitter ohne Eckpunkte. Instanzen, deren maßgeblicher Abstand dem Betrag nach unter 2 % von L liegt,
    werden ausgelassen: dort ist die Lücke zu klein für das Gitter (die vorgerechnete Reihe in data/tables.json zählt alle)."""
    agree = valid = skipped = 0
    for seed in (11, 22):
        for v0, v1, c0, c1, kappa in _random_instances(seed, 30, random_kappa):
            val = DA.cs_validity(v0, v1, c0, c1, kappa, tol=1e-12)
            if abs(val.margin) < 0.02 * (v1 - c0):
                skipped += 1
                continue
            gs, gb = DA.best_response_gap(v0, v1, c0, c1, kappa, ntypes=21, ngrid=4001, corners=False)
            assert (max(gs, gb) < 1e-7) == val.valid, (v0, v1, c0, c1, kappa, gs, gb, val)
            agree += 1
            valid += val.valid
    return agree, valid, skipped


@pytest.mark.parametrize("random_kappa", [False, True, "edge"])
def test_validity_criterion_agrees_with_the_grid_gap(random_kappa):
    agree, valid, skipped = validity_agreement(random_kappa)
    assert agree >= 40 and 0 < valid < agree          # beide Zweige (gültig und ungültig) kommen vor


def test_validity_zero_and_nonzero_branches_both_occur():
    flags = [DA.cs_validity(*inst[:4], inst[4], tol=1e-12).valid for seed in (11, 22) for inst in _random_instances(seed, 30, False)]
    assert any(flags) and not all(flags)


# --- (5) Einpreis-Gleichgewichte ---------------------------------------------------------------------------------------------------------------------
@pytest.mark.parametrize("p", [0.1, 0.3, 0.5, 0.7, 0.9])
def test_one_price_profile_is_an_equilibrium_on_the_grid(p):
    gs, gb = DA.one_price_gap(0.0, 1.0, 0.0, 1.0, p, ntypes=41, ngrid=4001)
    assert max(gs, gb) < 1e-12
    assert DA.one_price_stats(0.0, 1.0, 0.0, 1.0, p)[1] == pytest.approx(p * (1 - p) / 2, rel=1e-12)


def test_one_price_with_a_wrong_ask_is_not_an_equilibrium():
    gs, gb = DA.one_price_gap(0.0, 1.0, 0.0, 1.0, 0.5, ask_other=0.6, ntypes=41, ngrid=4001)
    assert max(gs, gb) > 0.1


def test_one_price_equilibria_also_hold_for_other_ranges():
    for rng, p in (((0.2, 1.2, 0.0, 1.0), 0.6), ((0.0, 2.0, 0.5, 1.5), 1.0), ((0.0, 1.0, -0.5, 0.5), 0.2)):
        gs, gb = DA.one_price_gap(*rng, p, ntypes=21, ngrid=2001)
        assert max(gs, gb) < 1e-12
