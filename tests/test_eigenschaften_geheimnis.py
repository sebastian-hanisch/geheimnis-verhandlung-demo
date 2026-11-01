"""Eigenschaftstests (ORACLE-PLAYBOOK §5.2): Beziehungen, die gelten müssen, ohne dass man das richtige Ergebnis kennt. Zufallsinstanzen mit festem Zufalls-Seed (SplitMix64).

Verschiebung und Skalierung der Beträge, Rollentausch, Rangfolge Erstbestes >= Zweitbestes >= jedes Gleichgewicht, Einpreis-Symmetrie, Monotonie der Coase-Größen (nur dort, wo sie gemessen ist)."""

import pytest

import gvh_coase as CO
import gvh_double_auction as DA
from gvh_rng import SplitMix64


def _instances(seed, count, kappa=0.5, valid_only=True):
    rng = SplitMix64(seed)
    out = []
    while len(out) < count:
        v0 = 3 * rng.uniform()
        v1 = v0 + 0.3 + 2 * rng.uniform()
        c0 = -0.5 + 2.5 * rng.uniform()
        c1 = c0 + 0.3 + 2 * rng.uniform()
        k = kappa if kappa is not None else 0.1 + 0.8 * rng.uniform()
        if v1 - c0 < 0.2:
            continue
        if valid_only and not DA.cs_validity(v0, v1, c0, c1, k, tol=1e-12).valid:
            continue
        out.append((v0, v1, c0, c1, k))
    return out


def test_shifting_all_values_and_costs_shifts_strategies_and_keeps_the_trade_set():
    for v0, v1, c0, c1, k in _instances(1, 25, kappa=None):
        base = DA.cs_coefficients(v0, v1, c0, c1, k)
        shifted = DA.cs_coefficients(v0 + 7, v1 + 7, c0 + 7, c1 + 7, k)
        assert shifted.bb == pytest.approx(base.bb) and shifted.bs == pytest.approx(base.bs)
        assert DA.bid(5.0 + 7, shifted) == pytest.approx(DA.bid(5.0, base) + 7, abs=1e-9)
        assert DA.ask(5.0 + 7, shifted) == pytest.approx(DA.ask(5.0, base) + 7, abs=1e-9)
        assert DA.cs_stats(v0 + 7, v1 + 7, c0 + 7, c1 + 7, k) == pytest.approx(DA.cs_stats(v0, v1, c0, c1, k), abs=1e-9)
        assert DA.second_best_stats(v0 + 7, v1 + 7, c0 + 7, c1 + 7)[0] == pytest.approx(DA.second_best_stats(v0, v1, c0, c1)[0], abs=1e-9)
        assert DA.cs_validity(v0 + 7, v1 + 7, c0 + 7, c1 + 7, k, tol=1e-12).valid == DA.cs_validity(v0, v1, c0, c1, k, tol=1e-12).valid


def test_scaling_all_amounts_scales_gains_and_keeps_probabilities():
    lam = 2.5
    for v0, v1, c0, c1, k in _instances(2, 25, kappa=None):
        p1, g1 = DA.cs_stats(v0, v1, c0, c1, k)
        p2, g2 = DA.cs_stats(lam * v0, lam * v1, lam * c0, lam * c1, k)
        assert p2 == pytest.approx(p1, rel=1e-9) and g2 == pytest.approx(lam * g1, rel=1e-9)
        sp1, sg1, th1 = DA.second_best_stats(v0, v1, c0, c1)
        sp2, sg2, th2 = DA.second_best_stats(lam * v0, lam * v1, lam * c0, lam * c1)
        assert sp2 == pytest.approx(sp1, abs=1e-9) and sg2 == pytest.approx(lam * sg1, rel=1e-9) and th2 == pytest.approx(th1, abs=1e-9)


def test_role_swap_mirrors_the_game():
    """(v, c) -> (-c, -v) tauscht Käufer und Verkäufer, der Preis spiegelt sich mit kappa -> 1 - kappa: Wahrscheinlichkeit, Gewinn und Gültigkeit bleiben."""
    for v0, v1, c0, c1, k in _instances(3, 25, kappa=None, valid_only=False):
        mirror = (-c1, -c0, -v1, -v0, 1 - k)
        a = DA.cs_validity(v0, v1, c0, c1, k, tol=1e-12)
        b = DA.cs_validity(*mirror[:4], mirror[4], tol=1e-12)
        assert a.valid == b.valid
        if a.valid:
            assert DA.cs_stats(v0, v1, c0, c1, k) == pytest.approx(DA.cs_stats(*mirror[:4], mirror[4]), abs=1e-9)
        assert DA.first_best_stats(v0, v1, c0, c1) == pytest.approx(DA.first_best_stats(*mirror[:4]), abs=1e-9)
        assert DA.second_best_stats(v0, v1, c0, c1) == pytest.approx(DA.second_best_stats(*mirror[:4]), abs=1e-9)


def test_symmetric_ranges_give_a_symmetric_price_rule_curve():
    for kp in range(0, 51, 5):
        k = kp / 100
        assert DA.cs_stats(0.0, 1.0, 0.0, 1.0, k)[1] == pytest.approx(DA.cs_stats(0.0, 1.0, 0.0, 1.0, 1 - k)[1], abs=1e-12)


def test_ranking_first_best_second_best_equilibrium_and_one_price():
    """Erstbestes >= Zweitbestes >= jedes Gleichgewicht eines Verfahrens, bei dem beide freiwillig mitmachen und niemand Geld zuschießt (hier: lineares Gleichgewicht
    und Einpreis-Gleichgewichte, jeweils als Doppelte Auktion)."""
    for v0, v1, c0, c1, k in _instances(4, 40, kappa=None):
        _fp, fg = DA.first_best_stats(v0, v1, c0, c1)
        _sp, sg, _th = DA.second_best_stats(v0, v1, c0, c1)
        _cp, cg = DA.cs_stats(v0, v1, c0, c1, k)
        assert fg + 1e-12 >= sg >= cg - 1e-12
        for frac in (0.1, 0.4, 0.5, 0.8):
            p = min(v0, c0) + frac * (max(v1, c1) - min(v0, c0))
            assert sg + 1e-12 >= DA.one_price_stats(v0, v1, c0, c1, p)[1]


def test_equilibrium_equals_second_best_exactly_when_kappa_is_one_half_and_valid():
    for v0, v1, c0, c1, k in _instances(5, 40):
        assert DA.cs_stats(v0, v1, c0, c1, 0.5)[1] == pytest.approx(DA.second_best_stats(v0, v1, c0, c1)[1], rel=1e-9)


def test_equilibrium_is_below_second_best_for_other_price_rules():
    """Zweig: bei kappa != 1/2 liegt das Gleichgewicht unter dem Zweitbesten (nicht gleich) -- in jeder gültigen Zufallsinstanz mit kappa außerhalb von [0,45; 0,55]."""
    count = 0
    for v0, v1, c0, c1, k in _instances(6, 60, kappa=None):
        if abs(k - 0.5) < 0.05:
            continue
        count += 1
        assert DA.cs_stats(v0, v1, c0, c1, k)[1] < DA.second_best_stats(v0, v1, c0, c1)[1] - 1e-9
    assert count >= 20


def test_one_price_gain_is_symmetric_about_the_middle_for_equal_ranges():
    for p in (0.05, 0.2, 0.35, 0.45):
        assert DA.one_price_stats(0.0, 1.0, 0.0, 1.0, p)[1] == pytest.approx(DA.one_price_stats(0.0, 1.0, 0.0, 1.0, 1 - p)[1], abs=1e-12)


# --- Coase -------------------------------------------------------------------------------------------------------------------------------------------
def test_profit_and_first_price_do_not_rise_with_more_rounds():
    for d in (0.3, 0.6, 0.9, 0.99):
        par = CO.coase_params(d, 300)
        assert all(par.k[t] <= par.k[t - 1] + 1e-15 for t in range(2, 301))
        assert all(par.pi[t] <= par.pi[t - 1] + 1e-15 for t in range(2, 301))


def test_first_price_falls_with_the_discount_factor_only_for_long_horizons():
    """Gemessen auf dem Raster delta = 0, 0,01, ..., 0,99: bei T = 200 und T = 3000 fällt der erste Preis monoton in delta; bei kurzem Horizont (T = 2, 3, 5, 10, 30) steigt er
    für große delta wieder (Minimum bei delta = 0,67 / 0,73 / 0,80 / 0,87 / 0,94). Die Erwartung „mehr Geduld, niedrigerer erster Preis“ gilt also nur mit langem Horizont."""
    grid = [d / 100 for d in range(100)]
    for T in (200, 3000):
        prices = [CO.first_price(d, T) for d in grid]
        assert all(b <= a + 1e-12 for a, b in zip(prices, prices[1:])), T
    minima = {}
    for T in (2, 3, 5, 10, 30):
        prices = [CO.first_price(d, T) for d in grid]
        assert any(b > a + 1e-12 for a, b in zip(prices, prices[1:])), T
        minima[T] = grid[prices.index(min(prices))]
    assert minima == {2: 0.67, 3: 0.73, 5: 0.8, 10: 0.87, 30: 0.94}


def test_euro_amounts_of_the_waiting_model_scale_linearly_with_the_value_limit():
    """Die Euro-Größen der App sind V mal die normierten (Wert gleichverteilt auf [0, V], Gewinn je Verlader): halbes V gibt halben Gewinn, Überschuss, Gesamtwert und ersten Preis."""
    import gvh_evaluation as EV
    from gvh_scenario import Settings
    big = EV.coase_totals(EV.analyse_coase(Settings(delta=90, T=50, vmax=60)))
    small = EV.coase_totals(EV.analyse_coase(Settings(delta=90, T=50, vmax=30)))
    for scenario in ("free", "bound"):
        for key in ("profit", "surplus", "welfare"):
            assert small[scenario][key] == pytest.approx(big[scenario][key] / 2, rel=1e-12)
        assert small[scenario]["unsold"] == pytest.approx(big[scenario]["unsold"], rel=1e-12)
    assert EV.analyse_coase(Settings(delta=90, T=50, vmax=30)).first_price == pytest.approx(EV.analyse_coase(Settings(delta=90, T=50, vmax=60)).first_price / 2, rel=1e-12)


def test_every_discount_factor_below_one_gives_a_strictly_lower_profit_than_commitment_for_two_or_more_rounds():
    for d in (0.1, 0.5, 0.9, 0.99):
        assert CO.equilibrium_path(d, 2).profit < CO.commitment_outcome()[0]
