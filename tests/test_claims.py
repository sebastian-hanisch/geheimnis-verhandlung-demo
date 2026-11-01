"""Jede Zahl aus der README, nachgerechnet (DEMO-PLAYBOOK §4).

Drei Quellen, alle plattformsicher:
* die gespeicherten Messreihen (`data/tables.json`; Erzeuger-Hash geprüft in `test_measurements.py`): die README-Zahl ist der gespeicherte Wert, gerundet;
* exakte Rechnung (Brüche, Formeln, Identitäten): Gleitkommagleichheit nur mit `approx`;
* die Zeilenbauer der App (`gvh_evaluation.*_rows`, `*_table`): jede Zeile der README-Tabellen steht als Text in der README.
Keine Zeit-Assertion, keine exakten Zufallswerte einzelner Läufe. Zählungen über das Raster („in k von m Zellen“) stehen als Zählungen im Test, nicht als Urteilswort."""

import math
import re
from fractions import Fraction as F
from pathlib import Path

import pytest

import gvh_coase as CO
import gvh_double_auction as DA
import gvh_evaluation as EV
import gvh_experiments as XP
import gvh_texts as T
from gvh_scenario import Settings

ROOT = Path(__file__).resolve().parent.parent
README = (ROOT / "README.md").read_text(encoding="utf-8")
UNIT = (0.0, 1.0, 0.0, 1.0)


def german(x, nd):
    """Eigene Fassung des deutschen Zahlenformats (unabhängig von EV.de): Dezimalkomma, Tausenderpunkt."""
    s = f"{x:,.{nd}f}"
    return s.replace(",", "T").replace(".", ",").replace("T", ".")


def row_of(label):
    """Die Tabellenzeile der Hypothese (eine Zeile der README, beginnt mit `| Hn |`)."""
    return next(line for line in README.splitlines() if line.startswith(f"| {label} |"))


def has(row, *needles):
    missing = [n for n in needles if n not in row]
    assert not missing, missing


def md_row(d):
    return "| " + " | ".join(str(v) for v in d.values()) + " |"


@pytest.fixture(scope="module")
def tables():
    t = XP.load_tables()
    assert t is not None
    return t


# --- README und App: dieselben Texte, dieselben Tabellenzeilen ---------------------------------------------------------------------------------
def test_assumption_and_not_implemented_texts_are_the_same_in_app_and_readme():
    assert T.ASSUMPTIONS_MARKDOWN.strip() in README
    assert T.NOT_IMPLEMENTED_MARKDOWN.strip() in README


def test_readme_tables_are_built_by_the_same_row_builders(tables):
    s = Settings()
    commit_rows = []
    for delta, horizon in ((50, 200), (90, 200), (99, 3000)):
        for row in EV.commitment_rows(EV.analyse_coase(Settings(delta=delta, T=horizon))):
            commit_rows.append({"δ": EV.de(delta / 100, 2), **row})
    builders = (EV.shift_table(EV.shift_rows(s)), EV.rows_validity(tables), EV.kappa_table(EV.kappa_rows(s)), EV.one_price_rows(s), commit_rows,
                EV.fixed_table(EV.fixed_horizon_rows(s)), EV.horizon_table(), EV.rows_deviation(tables))
    for rows in builders:
        assert rows
        for row in rows:
            assert md_row(row) in README, row


def test_hypothesis_rows_are_present_with_the_expected_status():
    rows = re.findall(r"^\| (H\d+) \|(?:\\\||[^|])*\|\s*\*\*([^*]+)\*\*", README, flags=re.M)
    assert dict(rows) == {"H1": "Ja", "H2": "Ja", "H3": "Ja", "H4": "Ja", "H5": "Ja", "H6": "Ja", "H7": "Nein", "H8": "Ja", "H9": "Ja", "H10": "Ja", "H11": "Ja",
                          "H12": "Offen", "H13": "Nein"}


# --- Kernfrage -----------------------------------------------------------------------------------------------------------------------------------
def test_core_question_numbers():
    unit_gain = DA.cs_stats(*UNIT, 0.5)
    fb = DA.first_best_stats(*UNIT)
    assert 60 * unit_gain[1] == pytest.approx(8.4375) and 60 * fb[1] == pytest.approx(10.0)
    assert unit_gain[1] / fb[1] == pytest.approx(27 / 32) and 1 - unit_gain[0] / fb[0] == pytest.approx(7 / 16)
    one = lambda p: DA.one_price_stats(*UNIT, p)[1] * 60      # noqa: E731
    assert one(0.5) == pytest.approx(7.5) and one(0.5) / (60 * 9 / 64) == pytest.approx(8 / 9) and one(0.1) == pytest.approx(2.7) and one(0.1) / (60 * 9 / 64) == pytest.approx(0.32)
    path = CO.equilibrium_path(0.9, 200)
    assert 60 * path.price[0] == pytest.approx(14.42, abs=5e-3) and path.profit / 0.25 == pytest.approx(0.481, abs=5e-4)
    assert 60 * path.welfare == pytest.approx(26.40, abs=5e-3) and 60 * path.surplus == pytest.approx(19.19, abs=5e-3)
    has(README, "8,44 Euro statt 10,00 Euro im Erstbesten (84,4 %)", "7/16 (43,8 %)", "Einpreis bei 30 Euro", "7,50 Euro (88,9 % des Zweitbesten)", "Einpreis bei 6 Euro mit 2,70 Euro (32,0 %)", "gemessen bis *rH* = 2",
        "14,42 Euro statt 30,00 Euro", "48,1 %", "(26,40 statt 22,50 Euro)", "19,19 statt 7,50 Euro")


# --- H1 bis H6: doppelte Auktion -----------------------------------------------------------------------------------------------------------------
def test_h1_classic_equilibrium():
    st = DA.cs_coefficients(F(0), F(1), F(0), F(1), F(1, 2))
    assert (st.ab, st.bb, st.as_, st.bs) == (F(1, 12), F(2, 3), F(1, 4), F(2, 3))
    assert DA.cs_stats(F(0), F(1), F(0), F(1), F(1, 2)) == (F(9, 32), F(9, 64))
    assert DA.best_response_gap(*UNIT, 0.5, ntypes=41, ngrid=4001, corners=False) == (0.0, 0.0)
    assert DA.seller_payoff(F(1, 4), F(1, 4), st, F(0), F(1), F(1, 2)) == F(3, 32) and DA.seller_payoff(DA.ask(F(1, 4), st), F(1, 4), st, F(0), F(1), F(1, 2)) == F(1, 8)
    has(row_of("H1"), "2*v*/3 + 1/12", "2*c*/3 + 1/4", "9/64", "9/32", "Lücke exakt 0 auf dem Gitter 1/120", "Gitter 4 001", "3/32 statt 1/8")


def test_h2_second_best():
    assert DA.budget_slack(F(0), F(1), F(0), F(1), F(1, 4)) == 0
    assert DA.second_best_stats(*UNIT)[1] == pytest.approx(9 / 64, abs=1e-15)
    pytest.importorskip("scipy")
    import test_oracle_auction as TA
    lp_a, _ = TA._lp_richardson(*UNIT, ks=(24, 32))
    lp_b, _ = TA._lp_richardson(*UNIT, ks=(32, 40))
    assert german(lp_a, 5) == "0,14106" and german(lp_b, 5) == "0,14089" and german(9 / 64, 6) == "0,140625"
    assert german((lp_a - 9 / 64) * 1e4, 1) == "4,3"
    has(row_of("H2"), "*G*(¼) = 0 in Brüchen", "0,14106 gegen 9/64 = 0,140625", "aus 32 und 40: 0,14089")
    has(README, "Abweichung 4,3·10⁻⁴ bei 24 und 32 Typen")


def test_h3_equilibrium_equals_second_best_when_valid(tables):
    sm = tables["validity"]["half"]["summary"]
    assert sm["valid_with_second_best"] == sm["both_valid"] == 59 and sm["rel_dev_max"] < 1e-9
    assert f"{sm['rel_dev_max']:.1e}" == "5.3e-13"
    # Anteil am Zweitbesten: in jeder gültigen Zeile der Verschiebungstabelle 100 %
    rows = [r for r in EV.shift_rows(Settings()) if r.valid]
    assert len(rows) == 5 and all(r.equals_second for r in rows)
    has(row_of("H3"), "59 von 59 gültigen Zufallsinstanzen", "5,3·10⁻¹³", "Anteil am Zweitbesten in allen 59 gültigen Instanzen 100 %")


def test_h4_validity_criterion(tables):
    for mode in ("half", "random"):
        sm = tables["validity"][mode]["summary"]
        assert sm["total"] == 189 and sm["both_valid"] + sm["both_invalid"] == 189 and sm["criterion_only"] == sm["numeric_only"] == 0
    assert tables["validity"]["half"]["summary"]["both_valid"] == 59 and tables["validity"]["half"]["summary"]["both_invalid"] == 130
    assert tables["validity"]["random"]["summary"]["both_valid"] == 70 and tables["validity"]["random"]["summary"]["both_invalid"] == 119
    import test_oracle_auction as TA
    counts = {mode: TA.validity_agreement(mode) for mode in (False, True, "edge")}
    assert [counts[m][0] for m in (False, True, "edge")] == [52, 57, 53] and counts["edge"][1] < counts["edge"][0]
    has(row_of("H4"), "189 von 189 bei κ = ½, 189 von 189 bei zufälligem κ", "52, 57 und 53 Zufallsinstanzen")
    has(README, "59 gültig / 130 ungültig", "70 gültig / 119 ungültig")


def test_h4_hand_edge_case_for_kappa_zero():
    v = DA.cs_validity(F(1, 2), F(3, 2), F(0), F(1), F(0))
    assert v.valid and v.margin_high == F(-1, 4)
    has(README, "bei κ = 0 die obere, bei κ = 1 die untere")


def test_h5_price_rule():
    ks = [k / 100 for k in range(0, 101, 5)]
    gains = [DA.cs_stats(*UNIT, k)[1] for k in ks]
    assert len(ks) == 21 and max(gains) == pytest.approx(9 / 64) and ks[gains.index(max(gains))] == 0.5
    assert sum(1 for k in range(0, 50, 5) if gains[k // 5] == pytest.approx(gains[(100 - k) // 5])) == 10
    assert all(DA.cs_validity(*UNIT, k, tol=1e-12).valid for k in ks) and DA.cs_stats(*UNIT, 0.0)[1] == pytest.approx(1 / 8)
    shares = {k: DA.cs_stats(*UNIT, k)[1] * 6 for k in (0.0, 0.1, 0.25, 0.4, 0.5)}
    assert [german(100 * shares[k], 1) for k in (0.0, 0.1, 0.25, 0.4, 0.5)] == ["75,0", "78,4", "82,0", "84,0", "84,4"]
    has(row_of("H5"), "21 Preisregeln", "10 Paare", "1/8")


def test_h6_one_price_equilibria():
    for p in (0.1, 0.3, 0.5, 0.7, 0.9):
        gs, gb = DA.one_price_gap(*UNIT, p, ntypes=41, ngrid=4001)
        assert max(gs, gb) <= 1e-12
        assert DA.one_price_stats(*UNIT, p)[1] == pytest.approx(p * (1 - p) / 2, rel=1e-12)
    gs, gb = DA.one_price_gap(*UNIT, 0.5, ask_other=0.6, ntypes=41, ngrid=4001)
    assert german(max(gs, gb), 2) == "0,25"
    has(row_of("H6"), "5 Preise", "10⁻¹²", "Lücke 0,25")


# --- H8 bis H13: Warten --------------------------------------------------------------------------------------------------------------------------
def test_h8_equilibrium_checks(tables):
    assert all(r["horizon"] == 200 and r["violations"] == 0 and r["worst"] <= 1e-9 for r in tables["deviation"]) and len(tables["deviation"]) == 3
    import test_oracle_coase as TC
    errs = {}
    for d in (0.5, 0.9, 0.99):
        out = TC.grid_maximum_solver(d, 30)
        par = CO.coase_params(d, 30)
        e = [abs(out[t - 1][0] - par.pi[t]) for t in range(1, 31)]
        errs[d] = (next(t for t, x in enumerate(e, 1) if x > 0.01), max(e))
    assert [errs[d][0] for d in (0.5, 0.9, 0.99)] == [6, 6, 9]
    assert [german(errs[d][1], 3) for d in (0.5, 0.9, 0.99)] == ["0,081", "0,221", "0,055"]
    has(row_of("H8"), "bis *T* = 200", "nur bis *T* = 3", "*T* = 6 (δ = 0,5 und 0,9) bzw. *T* = 9 (δ = 0,99)", "0,081 / 0,221 / 0,055")


def test_h9_limit_form_and_its_consequences():
    worst = 0.0
    for d in (0.1, 0.3, 0.5, 0.7, 0.8, 0.9, 0.95, 0.97, 0.99):
        horizon = 60_000 if d > 0.97 else 20_000
        pi, k = CO.first_price_and_profit(d, horizon)
        worst = max(worst, abs(pi - CO.limit_price(d)), abs(k - pi / 2))
        path = CO.equilibrium_path(d, horizon)
        assert path.mass[0] == pytest.approx(CO.limit_price(d), abs=1e-9)
        assert path.mean_wait == pytest.approx(1 / math.sqrt(1 - d), rel=1e-9)
    assert worst < 1e-12
    for s in (F(1, 2), F(1, 3), F(2, 3), F(1, 5), F(3, 4), F(1, 10)):
        d, p = 1 - s * s, s / (1 + s)
        assert CO.stationary_residual(d, p) == 0
        rho = 1 - d + d * p
        assert (rho - rho * rho / (2 * p)) / d == p / 2
    has(row_of("H9"), "9 Diskontfaktoren", "6 Punkten", "Wartezeit 1/s")
    has(README, "Messhypothesen ohne Beweis")


def test_h10_fixed_horizon_limit():
    import test_oracle_coase as TC
    devs = {}
    for horizon in (0.25, 0.5, 1.0, 2.0, 3.0, 4.0):
        value, _ = TC._fixed_horizon_richardson(horizon)
        devs[horizon] = abs(value - CO.fixed_horizon_limit(1.0, horizon))
    assert max(devs[h] for h in (0.25, 0.5, 1.0, 2.0)) < 2e-5 and german(devs[1.0] * 1e7, 1) == "7,3"
    assert german(devs[3.0] * 1e4, 1) == "1,4" and german(devs[4.0] * 1e3, 1) == "1,1"
    has(row_of("H10"), "höchstens 2·10⁻⁵", "7,3·10⁻⁷ bei *rH* = 1", "1,4·10⁻⁴ bei *rH* = 3", "1,1·10⁻³ bei *rH* = 4")


def test_h11_commitment_value():
    shares = []
    count = 0
    for d in (0.5, 0.6, 0.7, 0.8, 0.85, 0.9, 0.95, 0.99):
        path = CO.equilibrium_path(d, 3000 if d >= 0.99 else 200)
        count += int(path.welfare > 0.375 and path.surplus > 0.125 and path.profit < 0.25)
        if d in (0.5, 0.9, 0.99):
            shares.append(german(100 * path.profit / 0.25, 1))
    assert count == 8 and shares == ["82,8", "48,1", "18,2"]
    has(row_of("H11"), "8 von 8")
    has(README, "82,8 % (δ = 0,5), 48,1 % (δ = 0,9) und 18,2 % (δ = 0,99)", "0,5; 0,6; 0,7; 0,8; 0,85; 0,9; 0,95 und 0,99 höher (8 von 8)")


def test_h13_first_price_is_not_monotone_in_delta_for_short_horizons():
    grid = [d / 100 for d in range(100)]
    for horizon in (200, 3000):
        prices = [CO.first_price(d, horizon) for d in grid]
        assert all(b <= a + 1e-12 for a, b in zip(prices, prices[1:]))
    minima = []
    for horizon in (2, 3, 5, 10, 30):
        prices = [CO.first_price(d, horizon) for d in grid]
        assert any(b > a + 1e-12 for a, b in zip(prices, prices[1:]))
        minima.append(german(grid[prices.index(min(prices))], 2))
    assert minima == ["0,67", "0,73", "0,80", "0,87", "0,94"]
    has(row_of("H13"), "*T* = 2 bis 30", "*T* = 200 und 3 000")
    has(README, "Minimum bei δ = 0,67 / 0,73 / 0,80 / 0,87 / 0,94 für *T* = 2 / 3 / 5 / 10 / 30")


def test_horizon_needed_and_ratio_range():
    rows = EV.horizon_needed_rows()
    assert [r["T"] for r in rows] == [5, 9, 31, 66, 384, 823]
    ratios = [r["ratio"] for r in rows]
    assert german(min(ratios), 1) == "2,5" and german(max(ratios), 1) == "4,1"
    has(README, "das 2,5- bis 4,1-fache von 1/(1 − δ)")


def test_gain_scales_linearly_with_the_euro_scale():
    assert DA.cs_stats(0.0, 60.0, 0.0, 60.0, 0.5)[1] == pytest.approx(60 * 9 / 64) and DA.cs_stats(0.0, 60.0, 0.0, 60.0, 0.5)[0] == pytest.approx(9 / 32)
    has(README, "Gewinne skalieren linear, Wahrscheinlichkeiten nicht")


def test_shift_boundary_is_one_third_of_the_width():
    rows = EV.shift_rows(Settings())
    assert [r.valid for r in rows] == [True] * 5 + [False] * 4 and rows[4].shift == pytest.approx(20.0) and abs(rows[4].margin) < 1e-12
    has(README, "Der Grenzfall liegt bei der Verschiebung 20 Euro (ein Drittel der Breite)")


def test_method_numbers_stated_in_the_readme_come_from_the_code():
    import gvh_constants as C
    assert (C.GRID_TYPES, C.GRID_POINTS) == (21, 2001) and C.T_MAX == 3000 and (XP.GRID_TYPES, XP.GRID_POINTS) == (41, 8001)
    assert XP.TABLE_SEEDS == (11, 22, 33, 44) and XP.N_RANDOM == 50 and XP.DEV_HORIZON == 200
    has(README, "Gitter von 2 001 Geboten für 21 Typen je Seite", "vier Zufalls-Seeds, 50 je Seed und Modus", "Der Regler *T* geht bis 3 000")
