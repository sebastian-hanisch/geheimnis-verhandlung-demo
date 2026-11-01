"""Permalink (Begrenzen), Presets und Reglerliste (Standardmuster aus dem Demo-Portfolio)."""

import math
from collections.abc import Callable
from dataclasses import dataclass

import streamlit as st

import gvh_constants as C
from gvh_scenario import Settings


def _flag(text: str) -> bool:
    return str(text).strip().lower() in ("1", "true", "ja", "an")


@dataclass(frozen=True)
class SettingSpec:
    url_param: str
    caster: Callable
    default: object
    lo: float | None = None
    hi: float | None = None
    choices: tuple | None = None      # bei Auswahlreglern: die erlaubten Werte


SETTING_SPECS = {
    "v0_slider": SettingSpec("v0", int, C.DEFAULT_V0, C.V0_MIN, C.V0_MAX),
    "wv_slider": SettingSpec("wv", int, C.DEFAULT_WV, C.WV_MIN, C.WV_MAX),
    "c0_slider": SettingSpec("c0", int, C.DEFAULT_C0, C.C0_MIN, C.C0_MAX),
    "wc_slider": SettingSpec("wc", int, C.DEFAULT_WC, C.WC_MIN, C.WC_MAX),
    "kappa_slider": SettingSpec("kappa", int, C.DEFAULT_KAPPA, C.KAPPA_MIN, C.KAPPA_MAX),
    "p_slider": SettingSpec("p", int, C.DEFAULT_P, C.P_MIN, C.P_MAX),
    "delta_slider": SettingSpec("delta", int, C.DEFAULT_DELTA, C.DELTA_MIN, C.DELTA_MAX),
    "t_slider": SettingSpec("t", int, C.DEFAULT_T, C.T_MIN, C.T_MAX),
    "vmax_slider": SettingSpec("vmax", int, C.DEFAULT_VMAX, C.VMAX_MIN, C.VMAX_MAX),
    "commit_toggle": SettingSpec("commit", _flag, C.DEFAULT_COMMIT, choices=(True, False)),
    "dt_select": SettingSpec("dt", float, C.DEFAULT_DT, choices=C.DT_CHOICES),
    "h_slider": SettingSpec("h", float, C.DEFAULT_H, C.H_MIN, C.H_MAX),
}
PRESET_KEYS = {"v0": "v0_slider", "wv": "wv_slider", "c0": "c0_slider", "wc": "wc_slider", "kappa": "kappa_slider", "p": "p_slider", "delta": "delta_slider",
               "T": "t_slider", "vmax": "vmax_slider", "commit": "commit_toggle", "dt": "dt_select", "H": "h_slider"}


def init_session_state_defaults():
    for state_key, spec in SETTING_SPECS.items():
        if state_key not in st.session_state:
            st.session_state[state_key] = spec.default


def bounds(state_key):
    spec = SETTING_SPECS[state_key]
    return spec.lo, spec.hi


def load_permalink_settings():
    """Einmal je Sitzung: Werte aus der Adresszeile übernehmen, auf die Reglergrenzen begrenzt bzw. auf erlaubte Werte geprüft."""
    if "permalink_loaded" in st.session_state:
        return
    qp = st.query_params
    for state_key, spec in SETTING_SPECS.items():
        if spec.url_param in qp:
            try:
                value = spec.caster(qp[spec.url_param])
            except (ValueError, TypeError):
                continue
            if spec.choices is not None:
                if value not in spec.choices:
                    continue
            else:
                if isinstance(value, float) and not math.isfinite(value):
                    continue
                if spec.lo is not None:
                    value = max(spec.lo, value)
                if spec.hi is not None:
                    value = min(spec.hi, value)
            st.session_state[state_key] = value
    st.session_state["permalink_loaded"] = True


def sync_query_params(values):
    """`values`: {state_key: aktueller Wert}; die Adresszeile spiegelt die Konfiguration."""
    try:
        for state_key, value in values.items():
            st.query_params[SETTING_SPECS[state_key].url_param] = str(value)
    except Exception:
        pass


def apply_preset(name):
    """Alle Regler setzen: was das Preset nicht nennt, bekommt den Standardwert (so ist das Preset danach genau das aktive)."""
    for key, state_key in PRESET_KEYS.items():
        st.session_state[state_key] = C.PRESETS[name].get(key, SETTING_SPECS[state_key].default)


def settings_from_state() -> Settings:
    """Die Einstellungen aus dem Session State (vor dem Zeichnen der Regler gesetzt durch Voreinstellung, Permalink oder Standard)."""
    g = st.session_state.get
    d = {k: g(k, SETTING_SPECS[k].default) for k in SETTING_SPECS}
    return Settings(v0=int(d["v0_slider"]), wv=int(d["wv_slider"]), c0=int(d["c0_slider"]), wc=int(d["wc_slider"]), kappa=int(d["kappa_slider"]), p=int(d["p_slider"]),
                    delta=int(d["delta_slider"]), T=int(d["t_slider"]), vmax=int(d["vmax_slider"]), commit=bool(d["commit_toggle"]), dt=float(d["dt_select"]), H=float(d["h_slider"]))


def aktives_preset():
    """Name des Presets, dessen Werte GENAU den aktuellen Einstellungen entsprechen, sonst None.

    Zustandslos: verglichen wird jeder Regler aus SETTING_SPECS (ein Preset ohne Eintrag für einen Regler meint dessen
    Standardwert) mit dem Session State. Ein später ergänzter Regler braucht nur seinen Eintrag in SETTING_SPECS,
    dann hebt auch seine Änderung die Markierung auf (tests/test_layout.py prüft das für jeden Regler)."""
    preset_key_of = {state_key: key for key, state_key in PRESET_KEYS.items()}
    for name, preset in C.PRESETS.items():
        if all(
            st.session_state.get(state_key, spec.default) == preset.get(preset_key_of.get(state_key), spec.default)
            for state_key, spec in SETTING_SPECS.items()
        ):
            return name
    return None


def sidebar_presets():
    """Schnellstart oben in der Seitenleiste; das aktive Preset ist hervorgehoben (`type="primary"`)."""
    if not C.PRESETS:
        return
    st.header("🎯 Schnellstart")
    st.caption("Ein Beispielszenario laden:")
    aktiv = aktives_preset()
    for name in C.PRESETS:
        st.button(
            name, width="stretch", on_click=apply_preset, args=(name,), help=C.PRESET_HELP.get(name, ""), key=f"preset_{name}",
            type="primary" if aktiv == name else "secondary",
        )
