"""Orakel der Coase-Rekursion: andere Rechenwege als die Skalierungsrekursion der Demo.

(1) Brüche (T <= 8) und 100-stellige Dezimalrechnung (T <= 200) gegen float; (2) verschachtelte stetige Optimierung ohne Skalierungsansatz (T <= 3, scipy);
(3) Abweichungsprüfer: bester Preis eines abweichenden Spediteurs, die Antwort der Verlader durch Aufzählung ALLER späteren Kaufrunden (Skimming nicht vorausgesetzt), T bis 60 im Repo
(bis 200 im Scratch-Lauf); (4) Pfadsumme und Kauf je Typ durch Aufzählung von 200 001 Typen; (5) Fixpunktgleichung des Grenzfalls (brentq) gegen die Grenzform und die Rekursion bei T = 20 000;
(6) Richardson für den festen Horizont. Das unabhängige LÖSEN (ohne die Rekursionsformel) gelingt nur bis T = 3; das Gitter-Maximum der nächsten Grenze versagt ab T = 5 (letzter Test).
Der Abweichungsprüfer ist ein Gleichgewichts-Nachweis (Ein-Abweichungs-Prinzip), kein unabhängiges Lösen."""

from decimal import Decimal, getcontext
from fractions import Fraction as F
from functools import lru_cache

import numpy as np
import pytest

import gvh_coase as CO

optimize = pytest.importorskip("scipy.optimize")


# --- (1) Brüche und hohe Genauigkeit ----------------------------------------------------------------------------------------------------------------
@pytest.mark.parametrize("delta", [F(1, 2), F(9, 10), F(99, 100)])
def test_float_recursion_matches_fractions_up_to_eight_rounds(delta):
    exact = CO.coase_params(delta, 8)
    flt = CO.coase_params(float(delta), 8)
    for t in range(1, 9):
        assert float(exact.pi[t]) == pytest.approx(flt.pi[t], abs=1e-15) and float(exact.k[t]) == pytest.approx(flt.k[t], abs=1e-15)


@pytest.mark.parametrize("delta", ["0.5", "0.9", "0.99"])
def test_float_recursion_matches_100_digit_decimals_up_to_200_rounds(delta):
    getcontext().prec = 100
    d = Decimal(delta)
    pi, k = Decimal(1) / 2, Decimal(1) / 4
    flt = CO.coase_params(float(delta), 200)
    worst = 0.0
    for t in range(2, 201):
        rho = 1 - d * (1 - pi)
        pi = rho * rho / (2 * (rho - d * k))
        w = pi / rho
        k = pi * (1 - w) + d * k * w * w
        worst = max(worst, abs(float(pi) - flt.pi[t]), abs(float(k) - flt.k[t]))
    assert worst < 1e-13


# --- (2) Verschachtelte stetige Optimierung ----------------------------------------------------------------------------------------------------------
def _nested(delta, rounds):
    """Preis und Gewinn der ersten Runde bei Träger [0, 1]: für jede Grenze w die Indifferenz des Grenztyps (w - p = delta (w - p'(w)), p' = Preis der Folgerunde bei Träger [0, w])
    per Wurzelsuche, der Spediteur maximiert p (x - w) + delta V(w) per beschränkter Optimierung. Kein Skalierungsansatz: die Folgerunde wird für jeden Träger neu gelöst."""
    @lru_cache(maxsize=None)
    def solve(left, x):
        if left == 1:
            p = x / 2
            return p, p * (x - p)

        def cutoff(p):
            def f(w):
                return (w - p) - delta * (w - solve(left - 1, round(w, 12))[0])
            if f(x) <= 0:
                return x
            lo = x * 1e-6
            if f(lo) >= 0:
                return lo
            return optimize.brentq(f, lo, x, xtol=x * 1e-13)

        def neg(p):
            w = cutoff(p)
            return -(p * (x - w) + delta * solve(left - 1, round(w, 12))[1])
        r = optimize.minimize_scalar(neg, bounds=(x * 1e-6, x), method="bounded", options={"xatol": x * 1e-11})
        return r.x, -r.fun
    return solve(rounds, 1.0)


@pytest.mark.parametrize("delta", [0.5, 0.9])
@pytest.mark.parametrize("rounds", [2, 3])
def test_nested_optimisation_reproduces_the_recursion(delta, rounds):
    price, profit = _nested(delta, rounds)
    par = CO.coase_params(delta, rounds)
    assert price == pytest.approx(par.pi[rounds], abs=2e-5) and profit == pytest.approx(par.k[rounds], abs=2e-5)


# --- (3) Abweichungsprüfer ---------------------------------------------------------------------------------------------------------------------------
def deviation_check(delta, horizon, n_prices=20_001, k_scale=1.0):
    """Für t = 1..horizon verbleibende Runden (Träger [0, 1], Skalierung): der Spediteur weicht mit beliebigem Preis p ab; ab der nächsten Runde wird das Gleichgewicht gespielt.
    Der Verlader mit Wert v kauft jetzt, wenn v - p >= max über alle späteren Kaufrunden s von delta^s (v - q_s) ist (q_s = Gleichgewichtspreis der s-ten späteren Runde auf dem Pfad ab Träger 1,
    alle s aufgezählt); die Grenze ist w = p / (1 - kappa_t), kappa_t = max_s delta^s (1 - q_s). Rückgabe: größte Gewinnsteigerung der Abweichung gegen den Gleichgewichtsgewinn
    und die Zahl der t, in denen die nächste Runde NICHT die beste spätere Kaufrunde des Grenztyps ist (Skimming verletzt). `k_scale` verfälscht die Fortsetzung (Negativkontrolle)."""
    par = CO.coase_params(delta, horizon)
    prices = np.linspace(1e-5, 1.0, n_prices)
    worst = -np.inf
    skimming_violations = 0
    for t in range(1, horizon + 1):
        if t == 1:
            worst = max(worst, float((prices * (1 - prices)).max() - par.k[1]))
            continue
        kappa, x, kappa_next = 0.0, 1.0, None
        for s in range(1, t):
            left = t - s
            q = par.pi[left] * x
            kappa = max(kappa, delta ** s * (1 - q))
            if s == 1:
                kappa_next = delta * (1 - q)
            x = par.w[left] * x
        if abs(kappa - kappa_next) > 1e-12:
            skimming_violations += 1
        w = np.minimum(prices / (1 - kappa), 1.0)
        profit = prices * (1 - w) + delta * k_scale * par.k[t - 1] * w * w
        worst = max(worst, float(profit.max() - par.k[t]))
    return worst, skimming_violations


@pytest.mark.parametrize("delta", [0.5, 0.9, 0.99])
def test_no_profitable_one_round_deviation_for_sixty_rounds(delta):
    worst, violations = deviation_check(delta, 60)
    assert worst < 1e-9 and violations == 0


def test_deviation_check_catches_a_wrong_continuation():
    """Negativkontrolle: mit verdoppelter Fortsetzung lohnt das Abweichen."""
    worst, _ = deviation_check(0.9, 10, k_scale=2.0)
    assert worst > 0.05


# --- (4) Pfadsumme und Kauf je Typ -----------------------------------------------------------------------------------------------------------------
@pytest.mark.parametrize("delta,horizon", [(0.5, 5), (0.9, 30), (0.99, 100)])
def test_path_sums_match_type_by_type_enumeration(delta, horizon):
    path = CO.equilibrium_path(delta, horizon)
    n = 200_001
    v = (np.arange(n) + 0.5) / n
    upper = np.array(path.upper)
    price = np.array(path.price)
    # Kaufrunde (0-basiert) = erste Runde, deren obere Grenze nach der Runde unter dem Wert liegt; wer nie kauft, hat Wert <= upper[-1]
    idx = np.searchsorted(-upper, -v, side="left")           # upper fällt: erster Index mit upper[idx] < v
    buys = idx < horizon
    disc = delta ** idx[buys]
    profit = float(np.sum(disc * price[idx[buys]]) / n)
    surplus = float(np.sum(disc * (v[buys] - price[idx[buys]])) / n)
    assert profit == pytest.approx(path.profit, abs=2e-5) and surplus == pytest.approx(path.surplus, abs=2e-5)
    assert float(np.mean(~buys)) == pytest.approx(path.unsold, abs=2e-5)
    assert profit + surplus == pytest.approx(path.welfare, abs=3e-5)


@pytest.mark.parametrize("delta,horizon", [(0.5, 5), (0.9, 40), (0.99, 200)])
def test_profit_by_path_equals_the_recursion(delta, horizon):
    path = CO.equilibrium_path(delta, horizon)
    par = CO.coase_params(delta, horizon)
    assert path.profit == pytest.approx(par.k[horizon], abs=1e-13)
    assert path.profit + path.surplus == pytest.approx(path.welfare, abs=1e-13)


# --- (5) Grenzfall ------------------------------------------------------------------------------------------------------------------------------------
def _stationary_roots(delta):
    xs = np.linspace(1e-6, 0.5, 4001)
    fs = np.array([CO.stationary_residual(delta, float(x)) for x in xs])
    return [optimize.brentq(lambda p: CO.stationary_residual(delta, p), xs[i], xs[i + 1], xtol=1e-15) for i in range(len(xs) - 1) if fs[i] * fs[i + 1] < 0]


@pytest.mark.parametrize("delta", [0.1, 0.3, 0.5, 0.7, 0.9, 0.95])
def test_limit_form_matches_the_stationary_root_and_the_long_recursion(delta):
    form = CO.limit_price(delta)
    roots = _stationary_roots(delta)
    assert roots and min(abs(r - form) for r in roots) < 1e-9
    assert CO.first_price(delta, 20_000) == pytest.approx(form, abs=1e-9)


@pytest.mark.parametrize("s", [F(1, 2), F(1, 3), F(2, 3), F(1, 5), F(3, 4), F(1, 10)])
def test_limit_form_solves_the_stationary_equation_exactly_in_fractions(s):
    assert CO.stationary_residual(1 - s * s, s / (1 + s)) == 0


# --- (6) fester Horizont: Richardson ------------------------------------------------------------------------------------------------------------------
def _fixed_horizon_richardson(horizon, rate=1.0, steps=(4e-4, 2e-4, 1e-4)):
    prices = [CO.first_price(CO.round_discount(rate, dt), round(horizon / dt)) for dt in steps]
    return 2 * prices[2] - prices[1], (prices[0] - prices[1]) / (prices[1] - prices[2])


@pytest.mark.parametrize("horizon", [0.25, 0.5, 1.0, 2.0])
def test_fixed_horizon_limit_is_one_half_e_to_minus_h(horizon):
    value, ratio = _fixed_horizon_richardson(horizon)
    assert value == pytest.approx(CO.fixed_horizon_limit(1.0, horizon), abs=2e-5)
    assert 1.9 < ratio < 2.1                    # Fehler proportional zur Rundenlänge


def test_fixed_horizon_limit_is_not_yet_reached_at_horizon_four():
    value, _ = _fixed_horizon_richardson(4.0)
    assert abs(value - CO.fixed_horizon_limit(1.0, 4.0)) > 5e-4


# --- Gitter-Löser: dokumentierter Negativbefund --------------------------------------------------------------------------------------------------
def grid_maximum_solver(delta, rounds, points=801):
    """Rückwärtsrechnen über den Zustand x (obere Grenze der Typen) mit Wahl der nächsten Grenze y als Gitter-Maximum (parabolisch verfeinert); kein Skalierungsansatz.
    Preis, der y indifferent macht: (1 - delta) y + delta P(y). Rückgabe: Liste (Preis, Gewinn) bei x = 1 für 1..rounds Runden."""
    xs = np.linspace(0, 1, points)
    value, price = xs ** 2 / 4, xs / 2
    out = [(price[-1], value[-1])]
    x_col, y_row = xs[:, None], xs[None, :]
    below = y_row <= x_col
    h = xs[1] - xs[0]
    for _ in range(2, rounds + 1):
        obj = np.where(below, ((1 - delta) * y_row + delta * price[None, :]) * (x_col - y_row) + delta * value[None, :], -np.inf)
        j = obj.argmax(1)
        jm = np.clip(j, 1, points - 2)
        fm, f0, fp = obj[np.arange(points), jm - 1], obj[np.arange(points), jm], obj[np.arange(points), jm + 1]
        with np.errstate(all="ignore"):
            den = fm - 2 * f0 + fp
            off = np.where((den < 0) & np.isfinite(fm) & np.isfinite(fp), 0.5 * (fm - fp) / den, 0.0)
        y = np.minimum(xs[jm] + np.clip(off, -1, 1) * h, xs)
        new_price = (1 - delta) * y + delta * np.interp(y, xs, price)
        value, price = new_price * (xs - y) + delta * np.interp(y, xs, value), new_price
        out.append((price[-1], value[-1]))
    return out


def test_grid_maximum_solver_is_fine_for_three_rounds_and_fails_later():
    """Befund (Ursache nicht geklärt, Verdacht: das Maximum über die nächste Grenze ist flach, der Preis hängt linear an seiner Lage): bei delta = 0,9 und 801 Punkten
    stimmt der Löser für T <= 3 auf 0,01, weicht aber für T <= 30 um mehr als 0,05 ab."""
    out = grid_maximum_solver(0.9, 30)
    par = CO.coase_params(0.9, 30)
    early = max(abs(out[t - 1][0] - par.pi[t]) for t in range(1, 4))
    late = max(abs(out[t - 1][0] - par.pi[t]) for t in range(1, 31))
    assert early < 0.01 and late > 0.05
