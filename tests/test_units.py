"""Einheiten an den Mini-Instanzen (conftest, von Hand gerechnet): jede Regel einzeln, in Brüchen. Jede Einheit mit Wirkung ändert auf mindestens einer Instanz das Ergebnis."""

from fractions import Fraction as F

import numpy as np
import pytest

import gvh_coase as CO
import gvh_double_auction as DA


# --- Doppelte Auktion -------------------------------------------------------------------------------------------------------------------------------
def test_coefficients_of_the_classic_case(klassiker):
    st = DA.cs_coefficients(*klassiker["range"], klassiker["kappa"])
    assert (st.ab, st.bb, st.as_, st.bs) == (klassiker["ab"], klassiker["bb"], klassiker["as"], klassiker["bs"])
    assert DA.bid(F(1), st) == F(3, 4) and DA.bid(F(0), st) == F(1, 12) and DA.ask(F(0), st) == F(1, 4) and DA.ask(F(1), st) == F(11, 12)


def test_coefficients_of_the_shifted_case(grenzfall):
    st = DA.cs_coefficients(*grenzfall["range"], grenzfall["kappa"])
    assert (st.ab, st.bb, st.as_, st.bs) == (F(1, 9), F(2, 3), F(1, 3), F(2, 3))


def test_coefficients_when_the_seller_sets_the_price(verkaeufer_preis):
    st = DA.cs_coefficients(*verkaeufer_preis["range"], verkaeufer_preis["kappa"])
    assert (st.ab, st.bb, st.as_, st.bs) == (verkaeufer_preis["ab"], verkaeufer_preis["bb"], verkaeufer_preis["as"], verkaeufer_preis["bs"])


def test_coefficients_for_kappa_one_quarter():
    """kappa = 1/4: p = (3/4)/(7/4) = 3/7, q = (1/4)/(5/4) = 1/5, bb = 4/5, bs = 4/7; ab = (1/5 * 3/7 * 4/5)/(1 - 3/35) = 3/40, as = 3/7 * (3/40 + 4/5) = 3/8."""
    st = DA.cs_coefficients(F(0), F(1), F(0), F(1), F(1, 4))
    assert (st.ab, st.bb, st.as_, st.bs) == (F(3, 40), F(4, 5), F(3, 8), F(4, 7))


def test_type_pairs_of_the_classic_case(klassiker):
    st = DA.cs_coefficients(*klassiker["range"], klassiker["kappa"])
    assert DA.bid(F(1, 2), st) == DA.ask(F(1, 4), st) == F(5, 12) and DA.trades(F(1, 2), F(1, 4), st)       # Gleichstand: Handel
    assert DA.price(F(1, 2), F(1, 4), st, F(1, 2)) == F(5, 12)
    assert DA.bid(F(1, 2), st) == F(5, 12) and DA.ask(F(1, 2), st) == F(7, 12) and not DA.trades(F(1, 2), F(1, 2), st)
    assert DA.price(F(1), F(0), st, F(1, 2)) == F(1, 2)


def test_validity_margins_and_verdict(klassiker, grenzfall, ungueltig):
    kl = DA.cs_validity(*klassiker["range"], klassiker["kappa"])
    assert kl.valid and kl.margin_low == F(1, 6) and kl.margin_high == F(1, 6)         # 2/3 * (1/4 - 0) = 1/6, ebenso oben
    gf = DA.cs_validity(*grenzfall["range"], grenzfall["kappa"])
    assert gf.valid and gf.margin_low == 0 and gf.margin_high == 0                       # Grenzfall: beide Abstände null, noch gültig (Gleichheit zählt)
    ug = DA.cs_validity(*ungueltig["range"], ungueltig["kappa"])
    assert not ug.valid and ug.margin_low == ungueltig["margin"] == ug.margin_high


def test_validity_needs_each_of_the_two_conditions():
    """Nur eine Seite verletzt: Werte [1/2, 3/2] gegen Kosten [0, 3/2]: L = 3/2, L/4 = 3/8; v0 - c0 = 1/2 > 3/8 (unten verletzt), v1 - c1 = 0 <= 3/8 (oben erfüllt)."""
    v = DA.cs_validity(F(1, 2), F(3, 2), F(0), F(3, 2), F(1, 2))
    assert not v.valid and v.margin_low < 0 <= v.margin_high
    """Gegenstück: Werte [0, 3/2] gegen Kosten [0, 1/2]: L = 3/2; v0 - c0 = 0 erfüllt, v1 - c1 = 1 > 3/8 verletzt (oben)."""
    w = DA.cs_validity(F(0), F(3, 2), F(0), F(1, 2), F(1, 2))
    assert not w.valid and w.margin_high < 0 <= w.margin_low


def test_validity_at_the_price_rule_edges_drops_one_condition():
    """kappa = 0, Werte U[1/2, 3/2], Kosten U[0, 1]: b(v) = v, s(c) = 3/4 + c/2 (Handrechnung: a = (3/2 + c)/2). Unten 3/4 - 1/2 = 1/4 >= 0, oben 5/4 - 3/2 = -1/4 < 0.
    Beim Käufer lohnt Abweichen nicht (der Preis ist die Forderung, das Gebot ändert ihn nicht): gültig. Schon bei kappa = 1/10 ist das Profil ungültig (oben verletzt, und jetzt maßgeblich)."""
    v = DA.cs_validity(F(1, 2), F(3, 2), F(0), F(1), F(0))
    assert (v.margin_low, v.margin_high, v.valid, v.margin) == (F(1, 4), F(-1, 4), True, F(1, 4))
    w = DA.cs_validity(F(1, 2), F(3, 2), F(0), F(1), F(1, 10))
    assert not w.valid and w.margin_high < 0
    """Spiegelbild (v, c) -> (-c, -v), kappa -> 1 - kappa: Werte U[-1, 0], Kosten U[-3/2, -1/2], kappa = 1; hier entfällt die untere Bedingung."""
    m = DA.cs_validity(F(-1), F(0), F(-3, 2), F(-1, 2), F(1))
    assert m.valid and m.margin == m.margin_high == F(1, 4) and m.margin_low == F(-1, 4)


def test_validity_is_false_without_gains_from_trade():
    assert not DA.cs_validity(F(0), F(1), F(1), F(2), F(1, 2)).valid          # v1 <= c0: nichts zu handeln


def test_tolerance_lets_a_rounding_residual_pass():
    v = DA.cs_validity(0.2, 0.8, 0.0, 0.6, 0.5, tol=1e-9)                       # 0.2 + 0.6 und L/4 treffen sich bis auf Rundung
    assert v.valid and abs(v.margin_low) < 1e-12


def test_region_stats_classic(klassiker):
    assert DA.threshold_stats(*klassiker["range"], klassiker["thr"]) == (klassiker["prob"], klassiker["gain"])
    assert DA.first_best_stats(*klassiker["range"]) == (klassiker["fb_prob"], klassiker["fb_gain"])


def test_cs_stats_for_each_hand_instance(klassiker, grenzfall, verkaeufer_preis):
    assert DA.cs_stats(*klassiker["range"], klassiker["kappa"]) == (klassiker["prob"], klassiker["gain"])
    assert DA.cs_stats(*grenzfall["range"], grenzfall["kappa"]) == (grenzfall["prob"], grenzfall["gain"])
    assert DA.cs_stats(*verkaeufer_preis["range"], verkaeufer_preis["kappa"]) == (verkaeufer_preis["prob"], verkaeufer_preis["gain"])


def test_cs_stats_for_kappa_one_quarter():
    """Zwei Rechenwege in Brüchen: die Formel liefert 35/256; Handel bei 4/5 v - 4/7 c >= 3/8 - 3/40 = 3/10 (Handrechnung siehe test_oracle_auction: Quadratur)."""
    assert DA.cs_stats(F(0), F(1), F(0), F(1), F(1, 4)) == (F(35, 128), F(35, 256))


def test_second_best_is_a_quarter_in_the_classic_case(klassiker):
    assert DA.budget_slack(*klassiker["range"], klassiker["theta"]) == 0
    assert DA.budget_slack(*klassiker["range"], F(0)) == F(-1, 6)          # G(0) = 2 * 1/6 - 1 * 1/2 = -1/6
    theta = DA.second_best_theta(*klassiker["range"])
    assert abs(theta - F(1, 4)) < F(1, 10 ** 15)
    prob, gain, _ = DA.second_best_stats(*klassiker["range"])
    assert abs(gain - F(9, 64)) < F(1, 10 ** 15)


def test_second_best_is_first_best_when_it_is_budget_balanced():
    """Werte [60, 120] gegen Kosten [0, 60] (alle Touren lohnen sich): immer Handel, G(0) = E[2(v - c) - L] = 2 * 60 - 120 = 0 >= 0, also theta = 0."""
    assert DA.second_best_theta(F(60), F(120), F(0), F(60)) == 0


def test_one_price_profile(klassiker):
    assert DA.one_price_stats(*klassiker["range"], F(1, 2)) == (F(1, 4), F(1, 8))
    assert DA.one_price_stats(*klassiker["range"], F(1, 10)) == (F(9, 100), F(9, 100) * (F(11, 20) - F(1, 20)))     # 0,9 * 0,1; E[v|v>=0,1] = 0,55; E[c|c<=0,1] = 0,05
    prob, gain = DA.one_price_stats(*klassiker["range"], F(2))        # Einpreis über allen Werten: niemand kauft
    assert prob == 0 and gain == 0


def test_one_price_welfare_formula_p_times_one_minus_p_over_two(klassiker):
    for p in (F(1, 10), F(3, 10), F(1, 2), F(9, 10)):
        assert DA.one_price_stats(*klassiker["range"], p)[1] == p * (1 - p) / 2


def test_polygon_area_equals_trade_probability(klassiker, grenzfall):
    def area(poly):
        return abs(sum(a[0] * b[1] - b[0] * a[1] for a, b in zip(poly, poly[1:] + poly[:1]))) / 2
    for case in (klassiker, grenzfall):
        v0, v1, c0, c1 = case["range"]
        poly = DA.region_polygon(v0, v1, c0, c1, F(2, 3), F(2, 3), F(2, 3) * (v1 - c0) / 4)
        assert area(poly) / ((v1 - v0) * (c1 - c0)) == case["prob"]
    assert DA.region_polygon(F(0), F(1), F(0), F(1), F(1), F(1), F(2)) == []         # v - c >= 2: leer


def test_region_without_trade_and_with_certain_trade():
    assert DA.region_stats(F(0), F(1), F(0), F(1), F(1), F(1), F(2)) == (0, 0)                 # v - c >= 2 ist nie erfüllt
    prob, gain = DA.region_stats(F(1), F(2), F(0), F(1), F(1), F(1), F(0))                     # v >= 1 >= c: immer
    assert prob == 1 and gain == F(1, 1)                                                       # E[v - c] = 3/2 - 1/2


def test_seller_and_buyer_payoff_at_the_equilibrium_response(klassiker):
    """Spediteur mit c = 1/4 fordert 5/12: der Käufer bietet b >= 5/12 ab v* = (5/12 - 1/12)/(2/3) = 1/2; Auszahlung = 1/2 * (1/2 * 5/12 - 1/4 + 1/2 * 1/12) + (1/2 * 2/3) * (1 - 1/4)/2 = 0 + 1/8."""
    st = DA.cs_coefficients(*klassiker["range"], klassiker["kappa"])
    assert DA.seller_payoff(DA.ask(F(1, 4), st), F(1, 4), st, F(0), F(1), F(1, 2)) == F(1, 8)
    # ehrliche Forderung a = c = 1/4: v* = (1/4 - 1/12)/(2/3) = 1/4; Auszahlung 3/4 * (1/8 - 1/4 + 1/24) + 1/3 * (1 - 1/16)/2 = 3/4 * (-1/12) + 15/96 = 3/32
    assert DA.seller_payoff(F(1, 4), F(1, 4), st, F(0), F(1), F(1, 2)) == F(3, 32)


def test_best_response_gap_is_zero_in_the_classic_case_and_positive_outside(klassiker, ungueltig):
    assert DA.best_response_gap(0.0, 1.0, 0.0, 1.0, 0.5, ntypes=11, ngrid=501) == (0.0, 0.0)
    gs, gb = DA.best_response_gap(0.4, 1.4, 0.0, 1.0, 0.5, ntypes=11, ngrid=501)
    assert gs > 0.01 and gb > 0.01                                                            # gegen 0,0167 der Vormessung


def test_one_price_gap_detects_a_wrong_ask():
    assert DA.one_price_gap(0.0, 1.0, 0.0, 1.0, 0.5, ntypes=11, ngrid=501) == (0.0, 0.0)
    gs, gb = DA.one_price_gap(0.0, 1.0, 0.0, 1.0, 0.5, ask_other=0.6, ntypes=11, ngrid=501)
    assert gs > 0.1 or gb > 0.1


# --- Coase -----------------------------------------------------------------------------------------------------------------------------------------
def test_coase_steps_in_fractions(coase_halb):
    par = CO.coase_params(coase_halb["delta"], 3)
    for t in (1, 2, 3):
        assert par.pi[t] == coase_halb["pi"][t] and par.w[t] == coase_halb["w"][t]
    assert par.k[1] == F(1, 4) and par.k[2] == F(9, 40)


def test_coase_cutoff_type_is_indifferent(coase_halb):
    """Grenztyp 3/5: jetzt kaufen 3/5 - 9/20 = 3/20, in Runde 2 (Preis 3/10) 1/2 * (3/5 - 3/10) = 3/20."""
    d, w, p2 = coase_halb["delta"], coase_halb["w"][2], coase_halb["pi"][2]
    assert w - p2 == F(3, 20) == d * (w - coase_halb["pi"][1] * w)


def test_coase_path_matches_the_hand_computation(coase_halb):
    path = CO.equilibrium_path(0.5, 2)
    assert path.price == pytest.approx([9 / 20, 3 / 10], rel=1e-12) and path.mass == pytest.approx([2 / 5, 3 / 10], rel=1e-12)
    assert path.profit == pytest.approx(float(coase_halb["profit2"]), rel=1e-12) and path.surplus == pytest.approx(float(coase_halb["surplus2"]), rel=1e-12)
    assert path.welfare == pytest.approx(float(coase_halb["welfare2"]), rel=1e-12) and path.unsold == pytest.approx(float(coase_halb["unsold2"]), rel=1e-12)
    assert path.mean_wait == pytest.approx(float(coase_halb["wait2"]), rel=1e-12)


def test_one_round_is_the_static_monopoly():
    path = CO.equilibrium_path(0.9, 1)
    assert path.price == [0.5] and path.profit == 0.25 and path.surplus == 0.125 and path.welfare == 0.375 and path.unsold == 0.5
    assert (path.profit, path.surplus, path.welfare, path.unsold) == CO.commitment_outcome()


def test_without_discounting_the_seller_cannot_gain_from_waiting_for_buyers():
    """delta = 0: spätere Verkäufe zählen nicht, der Spediteur nimmt in Runde 1 den Monopolpreis, Gewinn 1/4 für jede Rundenzahl."""
    for t in (1, 2, 5):
        par = CO.coase_params(0.0, t)
        assert par.pi[t] == 0.5 and par.k[t] == 0.25


def test_limit_and_stationary_equation_in_fractions():
    """s = 1/2: delta = 3/4, Grenzpreis 1/3 (Handrechnung: rho = 1 - 3/4 + 3/4 * 1/3 = 1/2, w = 2/3, k = (1/2 - 1/4 * 3/2)/(3/4) = 1/6, F = 1/6 * (1 - 3/4 * 4/9) - 1/3 * 1/3 = 0)."""
    assert CO.stationary_residual(F(3, 4), F(1, 3)) == 0
    assert CO.limit_price(0.75) == pytest.approx(1 / 3, rel=1e-12)
    assert CO.stationary_residual(F(3, 4), F(1, 3) + F(1, 1000)) != 0           # kein Nullzufall


def test_fixed_horizon_helpers():
    assert CO.round_discount(1.0, 0.0) == 1.0 and CO.round_discount(2.0, 0.5) == pytest.approx(np.exp(-1))
    assert CO.rounds_for_horizon(1.0, 0.1) == 10 and CO.rounds_for_horizon(0.25, 1.0) == 1       # nie weniger als eine Runde
    assert CO.fixed_horizon_limit(1.0, 0.0) == 0.5 and CO.fixed_horizon_limit(2.0, 1.0) == pytest.approx(0.5 * np.exp(-2))


def test_horizon_for_tolerance_is_reached_first_at_the_returned_round():
    d = 0.5
    t = CO.horizon_for_tolerance(d, 0.01)
    target = CO.limit_price(d)
    par = CO.coase_params(d, t)
    assert abs(par.pi[t] - target) <= 0.01 * target < abs(par.pi[t - 1] - target)
    assert CO.horizon_for_tolerance(d, 0.01, t_max=3) is None


def test_every_stage_of_the_recursion_changes_the_price():
    """Zweig-Test: jede weitere Runde senkt den ersten Preis bei delta > 0 (keine Stufe ist wirkungslos)."""
    par = CO.coase_params(0.9, 12)
    assert all(par.pi[t] < par.pi[t - 1] for t in range(2, 13))
