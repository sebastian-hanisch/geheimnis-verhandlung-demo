"""End-to-end Smoke-Test via Streamlits offiziellem AppTest-Framework: lädt app.py mit den Standardeinstellungen, klickt jeden Button, fährt jeden Regler an seine Grenzen
(einzeln und alle zusammen), jede Rundenlänge, den Schalter Selbstbindung und prüft, dass kein Python-Fehler auftritt (insbesondere StreamlitDuplicateElementId bei
Diagrammen ohne eindeutiges key= und StreamlitAPIException bei Reglern mit berechneten Grenzen)."""

import os

from streamlit.testing.v1 import AppTest

import gvh_constants as C

APP_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "app.py")
TIMEOUT = int(os.environ.get("APPTEST_TIMEOUT", "300"))  # unter Last (parallele Läufe) reichen 180 s nicht immer; Umgebungsvariable zum Anpassen
AUTOPLAY_MARKER = "\u25b6"  # Auto-Play-Buttons (Animation mit sleep) im Smoke-Test auslassen


def _fresh_app() -> AppTest:
    at = AppTest.from_file(APP_PATH)
    at.run(timeout=TIMEOUT)
    assert not at.exception, [str(e) for e in at.exception]
    return at


def test_app_loads_without_exception():
    _fresh_app()


def test_every_button_click_does_not_raise():
    labels = [b.label for b in _fresh_app().button]
    assert labels, "keine Buttons gefunden"
    for index, label in enumerate(labels):
        if AUTOPLAY_MARKER in label:
            continue
        at = _fresh_app()
        at.button[index].click().run(timeout=TIMEOUT)
        assert not at.exception, (label, [str(e) for e in at.exception])


def test_every_slider_at_its_min_and_max_does_not_raise():
    labels = [s.label for s in _fresh_app().slider]
    assert len(labels) == 10, labels
    for index, label in enumerate(labels):
        for edge in ("min", "max"):
            at = _fresh_app()
            slider = at.slider[index]
            value = slider.min if edge == "min" else slider.max
            if isinstance(slider.value, int):
                value = int(value)
            slider.set_value(value).run(timeout=TIMEOUT)
            assert not at.exception, (label, edge, [str(e) for e in at.exception])


def test_every_round_length_and_the_toggle_do_not_raise():
    for dt in C.DT_CHOICES:
        at = _fresh_app()
        at.select_slider(key="dt_select").set_value(dt).run(timeout=TIMEOUT)
        assert not at.exception, (dt, [str(e) for e in at.exception])
    for flag in (True, False):
        at = _fresh_app()
        at.toggle(key="commit_toggle").set_value(flag).run(timeout=TIMEOUT)
        assert not at.exception, (flag, [str(e) for e in at.exception])


def test_all_minima_and_all_maxima_together_do_not_raise():
    for edge in ("min", "max"):
        at = _fresh_app()
        for index in range(len(at.slider)):
            slider = at.slider[index]
            value = slider.min if edge == "min" else slider.max
            at.slider[index].set_value(int(value) if isinstance(slider.value, int) else value)
        at.select_slider(key="dt_select").set_value(C.DT_CHOICES[-1] if edge == "max" else C.DT_CHOICES[0])
        at.toggle(key="commit_toggle").set_value(edge == "max")
        at.run(timeout=TIMEOUT)
        assert not at.exception, (edge, [str(e) for e in at.exception])


def test_pdf_button_produces_a_download():
    at = _fresh_app()
    at.button(key="pdf_button").click().run(timeout=TIMEOUT)
    assert not at.exception and at.session_state["pdf_bytes"][:5] == b"%PDF-"


def test_pdf_with_the_invalid_preset_and_the_toggle_on():
    at = _fresh_app()
    at.button(key="preset_Ungültig: Bereiche zu weit auseinander").click().run(timeout=TIMEOUT)
    at.toggle(key="commit_toggle").set_value(True).run(timeout=TIMEOUT)
    at.button(key="pdf_button").click().run(timeout=TIMEOUT)
    assert not at.exception and at.session_state["pdf_bytes"][:5] == b"%PDF-"


def test_headline_numbers_of_the_default_scenario():
    """Skala 60 Euro: Erstbestes 60/6 = 10, Zweitbestes = Gleichgewicht 60 * 9/64 = 8,4375 (8,44), Anteil 84,4 %, ausbleibend 7/16 = 43,8 %; Warten δ = 1/2, T = 200: Gewinn 0,2071 * 60 = 12,43."""
    at = _fresh_app()
    values = {m.label: m.value for m in at.metric}
    assert values["Erstbestes"] == "10,00" and values["Zweitbestes"] == "8,44" and values["Gleichgewicht"] == "8,44"
    assert values["Anteil am Erstbesten"] == "84,4 %" and values["Ausbleibender Handel"] == "43,8 %"
    assert values["Gewinn Spediteur"] == "12,43"
    delta = next(m for m in at.metric if m.label == "Gleichgewicht").delta
    assert delta == "-1,56"           # ASCII-Minus: sonst färbt Streamlit den Rückgang grün


def test_invalid_preset_shows_the_verdict_instead_of_a_number():
    at = _fresh_app()
    at.button(key="preset_Ungültig: Bereiche zu weit auseinander").click().run(timeout=TIMEOUT)
    assert not at.exception
    values = {m.label: m.value for m in at.metric}
    assert values["Gleichgewicht"] == "Formel gilt nicht" and "Anteil am Erstbesten" not in values
    assert any("Formel gilt hier nicht" in w.value for w in at.warning)


def test_toggle_switches_the_shown_scenario_and_flips_the_metric_deltas():
    at = _fresh_app()
    free = {m.label: (m.value, m.delta) for m in at.metric}
    at.toggle(key="commit_toggle").set_value(True).run(timeout=TIMEOUT)
    bound = {m.label: (m.value, m.delta) for m in at.metric}
    assert free["Gewinn Spediteur"] == ("12,43", "-2,57") and bound["Gewinn Spediteur"] == ("15,00", "2,57")
    assert bound["Nie gekauft"][0] == "50,0 %" and free["Nie gekauft"][0] == "0,0 %"


def test_permalink_values_are_clamped_and_bad_values_ignored():
    at = AppTest.from_file(APP_PATH)
    at.query_params["v0"] = "9999"           # über dem Maximum: auf die Reglergrenze begrenzt
    at.query_params["kappa"] = "abc"         # kein Zahlenwert: ignoriert (Standard bleibt)
    at.query_params["dt"] = "0.123"          # kein erlaubter Wert des Auswahlreglers: ignoriert
    at.query_params["commit"] = "true"
    at.run(timeout=TIMEOUT)
    assert not at.exception, [str(e) for e in at.exception]
    assert at.slider(key="v0_slider").value == C.V0_MAX and at.slider(key="kappa_slider").value == C.DEFAULT_KAPPA
    assert at.select_slider(key="dt_select").value == C.DEFAULT_DT and at.toggle(key="commit_toggle").value is True
