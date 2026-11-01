"""Randfälle (DEMO-PLAYBOOK §12): kleinste und größte Breiten, kein Handelsgewinn, κ an den Rändern, δ = 0 und 0,99, T = 1 und T = 3 000, Grenzfall der Gültigkeit."""

import math

import pytest

import gvh_coase as CO
import gvh_constants as C
import gvh_double_auction as DA
import gvh_evaluation as EV
from gvh_rng import SplitMix64
from gvh_scenario import Settings


def test_no_gain_when_the_highest_value_is_not_above_the_lowest_cost():
    s = Settings(v0=0, wv=10, c0=10, wc=10)             # v1 = 10 = c0: kein Handelsgewinn (Gleichstand zählt nicht)
    v = EV.analyse_auction(s)
    assert v.no_gain_possible and v.cs_gain is None and v.fb_gain == 0 and v.sb_gain == 0
    kind, text = EV.verdict_auction(v)
    assert kind == "info" and "keinen Handelsgewinn" in text
    assert EV.verdict_grid_check(v)[0] == "info"
    assert all(not r.valid for r in EV.kappa_rows(s)) and EV.best_one_price_gain(s) is None
    assert EV.verdict_one_price(EV.analyse_one_price(s, None))[0] == "info"


def test_smallest_widths_are_handled():
    for s in (Settings(wv=C.WV_MIN, wc=C.WC_MIN), Settings(v0=0, wv=C.WV_MIN, c0=0, wc=C.WC_MAX), Settings(v0=C.V0_MAX, wv=C.WV_MIN, c0=C.C0_MIN, wc=C.WC_MIN)):
        v = EV.analyse_auction(s)
        assert v.fb_gain >= v.sb_gain >= 0
        if v.cs_gain is not None:
            assert v.cs_gain <= v.sb_gain + 1e-9
        EV.kappa_rows(s)
        EV.shift_rows(s)


def test_values_entirely_above_the_costs_make_the_first_best_feasible():
    """Werte 60 bis 120, Kosten 0 bis 60: immer Handel; erstbest = zweitbest = 60 Euro; das lineare Profil ist hier kein Gleichgewicht (Fixpreis verbessert)."""
    s = Settings(v0=60, wv=60, c0=0, wc=60)
    v = EV.analyse_auction(s)
    assert v.sb_gain == pytest.approx(60.0) and v.fb_gain == pytest.approx(60.0) and v.theta == 0
    assert v.cs_gain is None and not v.validity.valid and v.gap > 1.0


def test_kappa_at_the_edges_has_a_valid_profile_in_the_classic_case():
    for kp in (0, 100):
        v = EV.analyse_auction(Settings(kappa=kp))
        assert v.validity.valid and v.cs_gain == pytest.approx(7.5) and v.grid_agrees          # 1/8 * 60


def test_boundary_case_of_validity_counts_as_valid_in_floats():
    v = EV.analyse_auction(Settings(v0=20))
    assert v.validity.valid and abs(v.validity.margin_low) < 1e-12 and v.grid_agrees
    just = EV.analyse_auction(Settings(v0=21))
    assert not just.validity.valid and just.validity.margin_low < -0.1 and just.gap > 0.1


def test_one_price_at_the_edges_has_no_trade_but_is_still_an_equilibrium():
    s = Settings(p=C.P_MAX)
    ov = EV.analyse_one_price(s, None)
    assert ov.prob == 0 and ov.gain == 0 and ov.gap <= C.GAP_TOL
    assert EV.verdict_one_price(ov)[0] == "info"
    assert EV.analyse_one_price(Settings(p=0), None).prob == pytest.approx(0)


def test_waiting_model_at_the_edges():
    one = EV.analyse_coase(Settings(delta=0, T=1))
    assert one.path.price == [0.5] and EV.verdict_coase(one)[0] == "info" and "einer einzigen Runde" in EV.verdict_coase(one)[1]
    patient = EV.analyse_coase(Settings(delta=C.DELTA_MAX, T=C.T_MAX))
    assert patient.path.price[0] == pytest.approx(CO.limit_price(0.99), rel=1e-9) and patient.path.profit < 0.05
    impatient = EV.analyse_coase(Settings(delta=0, T=C.T_MAX))
    assert impatient.path.price[0] == pytest.approx(0.5) and impatient.path.profit == pytest.approx(0.25)
    assert all(math.isfinite(x) for x in patient.path.price + patient.path.mass)


def test_worst_case_at_the_slider_maximum_finishes():
    """Komplexität am Maximum: T = 3 000 (O(T)) und die elf Rundenlängen des größten Horizonts (je O(H/Δ), zusammen unter 40 000 Schritten)."""
    cv = EV.analyse_coase(Settings(delta=99, T=3000))
    assert len(cv.path.price) == 3000 and cv.t_tol == 384
    rows = EV.fixed_horizon_rows(Settings(H=C.H_MAX))
    assert sum(r.rounds for r in rows) <= C.FIXED_HORIZON_T_MAX and rows[-1].rounds == 20_000
    curves = EV.price_curves(3000)
    assert len(curves[3000]) == 100


def test_fixed_horizon_rows_for_a_round_longer_than_the_horizon():
    rows = EV.fixed_horizon_rows(Settings(H=0.25))
    assert rows[0].dt == 1.0 and rows[0].rounds == 1 and rows[0].horizon == 1.0           # eine Runde, tatsächlicher Horizont 1 statt 0,25
    assert rows[0].price == 0.5


def test_second_best_is_the_first_best_at_the_extreme_overlap():
    prob, gain, theta = DA.second_best_stats(60.0, 120.0, 0.0, 60.0)
    assert theta == 0 and gain == pytest.approx(60.0) and prob == pytest.approx(1.0)


def test_polygon_of_an_empty_region_is_empty():
    assert DA.region_polygon(0.0, 1.0, 0.0, 1.0, 1.0, 1.0, 5.0) == []
    assert len(DA.region_polygon(0.0, 1.0, 0.0, 1.0, 1.0, 1.0, -5.0)) == 4                # alles gehandelt: das ganze Rechteck


def test_every_sampled_setting_gives_finite_numbers():
    rng = SplitMix64(0)

    def pick(lo, hi):
        return lo + int(rng.uniform() * (hi - lo + 1))

    for _ in range(25):
        s = Settings(v0=pick(C.V0_MIN, C.V0_MAX), wv=pick(C.WV_MIN, C.WV_MAX), c0=pick(C.C0_MIN, C.C0_MAX), wc=pick(C.WC_MIN, C.WC_MAX), kappa=pick(0, 20) * 5)
        v = EV.analyse_auction(s)
        for x in (v.fb_gain, v.sb_gain, v.gap, v.theta):
            assert math.isfinite(x)
        if v.cs_gain is not None:
            assert math.isfinite(v.cs_gain)
