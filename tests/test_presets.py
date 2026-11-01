"""Presets: Vollständigkeit, gültige Werte, Standard-Preset = Standardeinstellungen, jedes Preset ein anderer Zustand, und die Verdikte je Preset (DEMO-PLAYBOOK §11a Punkt 7)."""

import pytest

import gvh_constants as C
import gvh_evaluation as EV
import gvh_presets as P
from gvh_scenario import Settings


def test_every_preset_has_help_and_only_known_keys():
    assert set(C.PRESETS) == set(C.PRESET_HELP)
    for name, preset in C.PRESETS.items():
        assert set(preset) <= set(P.PRESET_KEYS), name
        assert C.PRESET_HELP[name]


def test_preset_values_are_inside_the_slider_bounds_or_choices():
    for name, preset in C.PRESETS.items():
        for key, value in preset.items():
            spec = P.SETTING_SPECS[P.PRESET_KEYS[key]]
            if spec.choices is not None:
                assert value in spec.choices, (name, key)
            else:
                assert spec.lo <= value <= spec.hi, (name, key)


def test_default_preset_equals_the_default_settings():
    assert Settings(**C.PRESETS["Klassiker (beide 0 bis 60 Euro)"]) == Settings()


def test_setting_specs_cover_every_preset_key_and_every_settings_field():
    assert set(P.PRESET_KEYS.values()) == set(P.SETTING_SPECS)
    assert set(P.PRESET_KEYS) == {f for f in Settings.__dataclass_fields__}


def test_all_presets_are_different_states():
    states = [Settings(**p) for p in C.PRESETS.values()]
    assert len(set(states)) == len(states)


def test_flag_caster():
    assert P._flag("true") and P._flag("1") and P._flag("an") and not P._flag("false") and not P._flag("")


def _verdicts(name):
    s = Settings(**C.PRESETS[name])
    av = EV.analyse_auction(s)
    return s, av


def test_preset_classic_and_shifted_are_valid_and_reach_the_second_best():
    for name, gain in (("Klassiker (beide 0 bis 60 Euro)", 60 * 9 / 64), ("Verschobene Bereiche (Grenzfall)", 20.0)):
        s, av = _verdicts(name)
        assert EV.verdict_auction(av)[0] == "success" and av.cs_gain == pytest.approx(gain) and av.cs_gain == pytest.approx(av.sb_gain, rel=1e-9) and av.grid_agrees


def test_preset_invalid_reports_no_number_instead_of_a_gain():
    s, av = _verdicts("Ungültig: Bereiche zu weit auseinander")
    kind, text = EV.verdict_auction(av)
    assert kind == "warning" and "Formel gilt hier nicht" in text and av.cs_gain is None and av.grid_agrees
    rows = EV.kappa_rows(s)
    assert [r.kappa for r in rows if r.valid] == [0, 100]            # nur die Ränder: dort entfällt je eine Bedingung (siehe cs_validity)
    assert "2 von 21 Preisregeln" in EV.verdict_kappa(rows, s)[1] and "(1 Paar geprüft)" in EV.verdict_kappa(rows, s)[1]


def test_preset_seller_sets_the_price_is_valid_and_below_the_second_best():
    s, av = _verdicts("Verkäufer setzt den Preis (κ = 0)")
    assert av.validity.valid and av.cs_gain == pytest.approx(7.5) and av.cs_gain < av.sb_gain and av.grid_agrees
    assert EV.verdict_auction(av)[0] == "success" and "unter dem Zweitbesten" in EV.verdict_auction(av)[1]


def test_preset_one_price_has_the_textbook_welfare():
    s, av = _verdicts("Einpreis bei der Mitte (30 Euro)")
    ov = EV.analyse_one_price(s, av.cs_gain)
    assert ov.gain == pytest.approx(7.5) and ov.gain / ov.sb_gain == pytest.approx(8 / 9) and ov.gap <= C.GAP_TOL


def test_preset_patient_cases_state_their_horizon_condition():
    s = Settings(**C.PRESETS["Geduldig (δ = 0,9)"])
    text = EV.verdict_coase(EV.analyse_coase(s))[1]
    assert "Ab 31 Runden" in text and "14,42 Euro" in text
    s = Settings(**C.PRESETS["Sehr geduldig (δ = 0,99, 3 000 Runden)"])
    text = EV.verdict_coase(EV.analyse_coase(s))[1]
    assert "Ab 384 Runden" in text and "5,45 Euro" in text and "nahe" not in text


def test_preset_short_rounds_has_a_thousand_rounds_and_the_fixed_horizon_price():
    s = Settings(**C.PRESETS["Kurze Runden bei festem Horizont"])
    cur = next(r for r in EV.fixed_horizon_rows(s) if r.dt == s.dt)
    assert cur.rounds == 1000 and cur.horizon == pytest.approx(1.0) and cur.price == pytest.approx(0.186, abs=5e-4)
