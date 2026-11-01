"""Verdikte an von Hand gesetzten Werten (DEMO-PLAYBOOK §12): jede Schwelle der Art und jede Zahl im Text. Die Rechnungen im Kommentar sind Handrechnungen (Skala 60 Euro)."""

import dataclasses

import pytest

import gvh_coase as CO
import gvh_constants as C
import gvh_evaluation as EV
from gvh_scenario import Settings


def _av(**kw):
    return EV.analyse_auction(Settings(**kw))


# --- Hauptverdikt ------------------------------------------------------------------------------------------------------------------------------------
def test_main_verdict_of_the_classic_case():
    """Gewinn 9/64 * 60 = 8,4375; Erstbestes 10; L/4 = 15; ausbleibend 7/16 = 43,75 %; Anteil 84,375 %."""
    kind, text = EV.verdict_auction(_av())
    assert kind == "success"
    assert "L/4 = 15,00 Euro" in text and "8,44 Euro" in text and "84,4 %" in text and "(10,00 Euro)" in text and "43,8 %" in text and "Das ist das Zweitbeste" in text


def test_main_verdict_for_another_price_rule_names_the_distance_to_the_second_best():
    """kappa = 0: Gewinn 1/8 * 60 = 7,5; Zweitbestes 8,4375; 1 - 7,5/8,4375 = 1/9 = 11,1 %; Anteil am Erstbesten 75 %; die Hälfte der Touren bleibt aus."""
    kind, text = EV.verdict_auction(_av(kappa=0))
    assert kind == "success" and "7,50 Euro" in text and "75,0 %" in text and "50,0 %" in text and "11,1 % unter dem Zweitbesten (8,44 Euro)" in text
    assert "Gehandelt wird genau, wenn das Gebot die Forderung erreicht" in text and "L/4" not in text


def test_main_verdict_of_the_invalid_case_gives_no_equilibrium_number():
    """Werte 36 bis 96, Kosten 0 bis 60, kappa = 1/2: L = 96, L/4 = 24; v0 - c0 = 36 > 24; Abstand 2/3 * (24 - 36) = -8 (unten wie oben)."""
    kind, text = EV.verdict_auction(_av(v0=36))
    assert kind == "warning" and text.startswith("Formel gilt hier nicht")
    assert text.count("8,00 Euro unter") == 2 and "v₀ − c₀ = 36" in text and "L/4 = 24,00 Euro" in text and "Zweitbeste: 34,16 Euro" in text and "Erstbestes 36,64" in text
    assert "Gewinn je Tour" not in text


def test_main_verdict_names_only_the_relevant_condition_at_the_edges():
    """kappa = 0 (Preis = Forderung): nur die untere Bedingung zählt; bei Werten 90 bis 150 ist sie verletzt (s(0) = 75 < b(90) = 90: -15), die obere nicht genannt."""
    kind, text = EV.verdict_auction(_av(v0=90, kappa=0))
    assert kind == "warning" and text.count("Euro unter dem") == 1 and "niedrigste Forderung liegt 15,00 Euro unter dem niedrigsten Gebot" in text
    kind, text = EV.verdict_auction(_av(v0=90, kappa=100))
    assert kind == "warning" and text.count("Euro unter dem") == 1 and "höchste Forderung" in text


def test_main_verdict_without_any_gain():
    kind, text = EV.verdict_auction(_av(v0=0, wv=10, c0=10, wc=10))
    assert kind == "info" and text.count("(10 Euro)") == 2 and "keinen Handelsgewinn" in text


def test_grid_check_verdict_has_three_branches():
    valid = _av()
    assert EV.verdict_grid_check(valid)[0] == "success" and "größte Lücke 0,000000 Euro" in EV.verdict_grid_check(valid)[1]
    invalid = _av(v0=36)
    kind, text = EV.verdict_grid_check(invalid)
    assert kind == "info" and "größte Lücke 4,00 Euro" in text                                   # Vormessung: Lücke 0,0667 bei Verschiebung 0,6 (normiert), mal 60 Euro = 4
    broken = dataclasses.replace(valid, gap_seller=1.0)                                            # Kriterium gültig, Gitter widerspricht
    kind, text = EV.verdict_grid_check(broken)
    assert kind == "error" and "widerspricht" in text and "Kriterium gültig" in text


# --- Preisregel -------------------------------------------------------------------------------------------------------------------------------------
def test_kappa_verdict_names_maximum_symmetry_and_edges():
    s = Settings()
    rows = EV.kappa_rows(s)
    kind, text = EV.verdict_kappa(rows, s)
    assert kind == "info" and "κ = 0,50" in text and "84,4 %" in text and "75,0 % und 75,0 %" in text and "symmetrisch (10 Paare geprüft)" in text and "21 von 21" in text


def test_kappa_verdict_without_any_valid_rule():
    s = Settings(v0=120, wv=10, c0=0, wc=10)
    kind, text = EV.verdict_kappa(EV.kappa_rows(s), s)
    assert kind == "warning" and "keine Kurve" in text


def test_kappa_verdict_marks_an_asymmetric_curve():
    s = Settings()
    rows = [dataclasses.replace(r, gain=r.gain * (1.1 if r.kappa == 40 else 1.0)) for r in EV.kappa_rows(s)]
    assert "nicht symmetrisch" in EV.verdict_kappa(rows, s)[1]


# --- Einpreis -----------------------------------------------------------------------------------------------------------------------------------------
def test_one_price_verdict_at_the_middle_price():
    """p = 30: Gewinn p(1-p)/2 in Skala: 60 * 1/8 = 7,5; Anteil am Zweitbesten 8/9 = 88,9 %; bester Einpreis 30."""
    s = Settings(p=30)
    kind, text = EV.verdict_one_price(EV.analyse_one_price(s, EV.analyse_auction(s).cs_gain))
    assert kind == "info" and "Einpreis 30 Euro: Gewinn 7,50 Euro" in text and "88,9 % des Zweitbesten" in text and "(30,0 Euro)" in text and "Das lineare Gleichgewicht aus Reiter 1 schafft 8,44 Euro" in text


def test_one_price_verdict_without_the_linear_equilibrium_omits_the_comparison():
    s = Settings(v0=36, p=30)
    assert "Reiter 1" not in EV.verdict_one_price(EV.analyse_one_price(s, None))[1]


def test_one_price_verdict_when_nobody_trades():
    s = Settings(p=C.P_MAX)
    kind, text = EV.verdict_one_price(EV.analyse_one_price(s, 8.4375))
    assert kind == "info" and "handelt niemand" in text and "Gewinn 0" in text and "Das lineare Gleichgewicht" in text


# --- Warten ----------------------------------------------------------------------------------------------------------------------------------------
def test_coase_verdict_for_the_default_case():
    """delta = 1/2, T = 200: erster Preis (sqrt 2 - 1) * 60 = 24,85; Gewinn 0,2071 * 60 = 12,43 gegen 15 (82,8 %); Gesamtwert 0,3964 * 60 = 23,79 gegen 22,5; Wartezeit sqrt 2 = 1,41; 5 Runden für 1 %."""
    kind, text = EV.verdict_coase(EV.analyse_coase(Settings(delta=50, T=200)))
    assert kind == "info"
    for needle in ("24,85 Euro (41,4 % von V = 60 Euro", "Gewinn 12,43 Euro statt 15,00 Euro mit Selbstbindung (82,8 %)", "23,79 statt 22,50 Euro (höher ohne Selbstbindung; Erstbestes 30,00)",
                   "im Mittel 1,41 Runden", "Ab 5 Runden", "dieser Horizont ist erreicht"):
        assert needle in text, needle


def test_coase_verdict_with_one_round_has_nothing_to_wait_for():
    kind, text = EV.verdict_coase(EV.analyse_coase(Settings(delta=90, T=1)))
    assert kind == "info" and "einer einzigen Runde" in text and "30,00 Euro" in text and "Gewinn" not in text


def test_coase_verdict_states_the_missing_horizon():
    """delta = 0,9, T = 10 < 31: der Horizont reicht nicht für das Prozent; ohne Horizontbedingung wäre „Preis nahe Kosten“ nicht gedeckt."""
    text = EV.verdict_coase(EV.analyse_coase(Settings(delta=90, T=10)))[1]
    assert "fehlt Horizont: erst ab 31 Runden" in text and "dieser Horizont ist erreicht" not in text


def test_coase_verdict_for_the_very_patient_preset_names_the_horizon_condition():
    """delta = 0,99, T = 3000: erster Preis 0,0909 * 60 = 5,45; 384 Runden reichen für ein Prozent; Wartezeit im Mittel 10."""
    text = EV.verdict_coase(EV.analyse_coase(Settings(delta=99, T=3000)))[1]
    assert "5,45 Euro (9,1 %" in text and "Ab 384 Runden" in text and "im Mittel 10,00 Runden" in text
    short = EV.verdict_coase(EV.analyse_coase(Settings(delta=99, T=50)))[1]
    assert "fehlt Horizont: erst ab 384 Runden" in short


def test_coase_verdict_welfare_wording_has_three_branches():
    cv = EV.analyse_coase(Settings(delta=50, T=5))
    same = dataclasses.replace(cv, path=cv.path._replace(welfare=0.375))
    lower = dataclasses.replace(cv, path=cv.path._replace(welfare=0.3))
    assert "(höher ohne Selbstbindung" in EV.verdict_coase(cv)[1]
    assert "(gleich ohne Selbstbindung" in EV.verdict_coase(same)[1]
    assert "(niedriger ohne Selbstbindung" in EV.verdict_coase(lower)[1]


def test_commitment_rows_show_both_paths():
    rows = EV.commitment_rows(EV.analyse_coase(Settings(delta=90, T=200)))
    assert [r["Pfad"] for r in rows] == ["ohne Selbstbindung", "mit Selbstbindung"]
    assert rows[1]["Gewinn Spediteur"] == "15,00" and rows[1]["Überschuss Verlader"] == "7,50" and rows[1]["Gesamtwert"] == "22,50" and rows[1]["nie gekauft"] == "50,0 %"
    assert rows[0]["Gewinn Spediteur"] == "7,21" and rows[0]["mittlere Wartezeit der Käufer (Runden)"] == "3,16"


# --- Rundenlänge -------------------------------------------------------------------------------------------------------------------------------------
def test_fixed_horizon_verdict_notes_that_the_formula_is_measured_only_up_to_two():
    s = Settings(H=1.0, dt=0.1)
    rows = EV.fixed_horizon_rows(s)
    text = EV.verdict_fixed(rows, s)[1]
    assert "50,0 % von V" in text and "(der Preis sinkt über alle elf Rundenlängen)" in text and "18,4 %" in text and "gemessen" not in text
    long = EV.verdict_fixed(EV.fixed_horizon_rows(Settings(H=4.0)), Settings(H=4.0))[1]
    assert "nur für H bis 2 gemessen" in long


def test_fixed_horizon_verdict_reports_a_non_monotone_price():
    s = Settings()
    rows = EV.fixed_horizon_rows(s)
    rows[3] = dataclasses.replace(rows[3], price=0.9)
    assert "nicht über alle elf Rundenlängen monoton" in EV.verdict_fixed(rows, s)[1]


def test_delta_curve_verdict_for_short_and_long_horizons():
    kind, text = EV.verdict_delta_curves(EV.price_curves(200), 200)
    assert kind == "info" and "T = 2: Minimum 44,4 % bei δ = 0,67" in text and "T = 10: Minimum 30,4 % bei δ = 0,87" in text and "T = 200: fällt über das ganze Raster bis δ = 0,99" in text
    text = EV.verdict_delta_curves(EV.price_curves(3000), 3000)[1]
    assert "T = 3000: fällt über das ganze Raster" in text


# --- Verschiebung, Tabellen --------------------------------------------------------------------------------------------------------------------------
def test_shift_verdict_counts_valid_rows():
    """Skala 60, kappa = 1/2: Verschiebungen 0, 6, 12, 18, 20, 24, 36, 48, 60 (Brüche 0 ... 1 der Kostenbreite); gültig bis v0 - c0 <= (v0 + 60)/4, also v0 <= 20: fünf Zeilen."""
    s = Settings()
    rows = EV.shift_rows(s)
    assert [r.shift for r in rows] == pytest.approx([0, 6, 12, 18, 20, 24, 36, 48, 60]) and [r.valid for r in rows] == [True] * 5 + [False] * 4
    kind, text = EV.verdict_shift(rows, s)
    assert kind == "info" and "bei 5 von 9 Verschiebungen, bis zur Verschiebung 20,00 Euro" in text and "(24,00 Euro)" in text and "in 5 von 5 Zeilen" in text and "in 9 von 9 Zeilen" in text
    assert rows[4].cs_gain == pytest.approx(20.0)                                                  # Grenzfall: 1/3 * 60


def test_shift_verdict_without_a_valid_row():
    s = Settings(v0=120, wv=10, c0=0, wc=10)
    assert EV.verdict_shift(EV.shift_rows(s), s)[0] == "warning"


def test_table_verdicts_report_mismatches():
    tables = {"validity": {m: {"summary": {"total": 10, "both_valid": 4, "both_invalid": 6, "criterion_only": 0, "numeric_only": 0, "valid_with_second_best": 4, "rel_dev_max": 1e-13}} for m in ("half", "random")},
              "deviation": [{"delta": 0.5, "horizon": 200, "worst": -1e-13, "violations": 0}]}
    kind, text = EV.verdict_table_validity(tables)
    assert kind == "success" and "10 von 10" in text and "Abweichungen: 0" in text
    tables["validity"]["random"]["summary"]["numeric_only"] = 1
    kind, text = EV.verdict_table_validity(tables)
    assert kind == "warning" and "Abweichungen: 1" in text
    assert EV.verdict_table_deviation(tables)[0] == "success"
    tables["deviation"][0]["violations"] = 2
    assert EV.verdict_table_deviation(tables)[0] == "warning"


def test_number_formatting():
    assert EV.de(1234.5) == "1.234,50" and EV.de(-0.001) == "0,00" and EV.de(-1.5) == "−1,50" and EV.pct(0.84375) == "84,4" and EV.de(0.1, 4) == "0,1000"
    assert CO.limit_price(0.75) == pytest.approx(1 / 3)
