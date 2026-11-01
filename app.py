"""Verhandeln mit privaten Werten: Was kostet das Geheimnis? - interaktive Konzept-Demo
Sebastian Hanisch - Operations Research und Machine Learning

Stück der Linie „Regeln setzen, verhandeln, kontrollieren“. Ein Verlader und ein Spediteur kennen jeder nur den eigenen Wert bzw. die eigenen Kosten. Die Demo rechnet das Gleichgewicht der doppelten Auktion (Chatterjee und
Samuelson) mit seinem Gültigkeitsbereich, das Zweitbeste als Maßstab, die Vielfalt der Gleichgewichte (Einpreis) und, bei einseitiger Information, das Warten statt Handeln (Coase) mit Selbstbindung gegen keine.

Lauffähig mit: streamlit run app.py
"""

import streamlit as st

import gvh_constants as C
import gvh_evaluation as EV
import gvh_experiments as XP
import gvh_texts as T
import gvh_visualization as Z
from gvh_evaluation import de, pct
from gvh_layout import dunkles_design, kopf_css
from gvh_presets import (
    SETTING_SPECS,
    bounds,
    init_session_state_defaults,
    load_permalink_settings,
    settings_from_state,
    sidebar_presets,
    sync_query_params,
)
from gvh_scenario import Settings

st.set_page_config(page_title="Verhandeln mit privaten Werten – Sebastian Hanisch", layout="wide")


# --- Zwischenspeicher (Schlüssel = genau die Eingaben, von denen die Rechnung abhängt) -----------------------------------------------------------------
@st.cache_data(show_spinner=False)
def _tables():
    return XP.load_tables()


@st.cache_data(show_spinner=False)
def _auction(v0, wv, c0, wc, kappa):
    return EV.analyse_auction(Settings(v0=v0, wv=wv, c0=c0, wc=wc, kappa=kappa))


@st.cache_data(show_spinner=False)
def _kappa(v0, wv, c0, wc):
    return EV.kappa_rows(Settings(v0=v0, wv=wv, c0=c0, wc=wc))


@st.cache_data(show_spinner=False)
def _shift(v0, wv, c0, wc, kappa):
    return EV.shift_rows(Settings(v0=v0, wv=wv, c0=c0, wc=wc, kappa=kappa))


@st.cache_data(show_spinner=False)
def _one_price(v0, wv, c0, wc, kappa, p):
    s = Settings(v0=v0, wv=wv, c0=c0, wc=wc, kappa=kappa, p=p)
    return EV.analyse_one_price(s, _auction(v0, wv, c0, wc, kappa).cs_gain), EV.one_price_rows(s)


@st.cache_data(show_spinner=False)
def _coase(delta, horizon, vmax, commit):
    return EV.analyse_coase(Settings(delta=delta, T=horizon, vmax=vmax, commit=commit))


@st.cache_data(show_spinner=False)
def _curves(rounds):
    return EV.price_curves(rounds)


@st.cache_data(show_spinner=False)
def _fixed(dt, horizon):
    return EV.fixed_horizon_rows(Settings(dt=dt, H=horizon))


def show(verdict):
    kind, text = verdict
    getattr(st, kind)(text)


def table(rows):
    st.dataframe(rows, hide_index=True, width="stretch")


# Fester Kopf: nur der Titel bleibt beim Scrollen oben (Stylesheet in gvh_layout.py).
st.html(kopf_css(dunkles_design()))
with st.container(key="kopf"):
    st.title("🔒 Verhandeln mit privaten Werten: Was kostet das Geheimnis?")
st.markdown(T.INTRO)

with st.expander("So funktioniert eine doppelte Auktion", expanded=True):
    st.markdown(T.EXPLAINER)

with st.expander("Erklärtabelle: Begriffe und Regler"):
    st.markdown(T.CONTROLS_TABLE)

st.caption("🔗 Die Adresszeile oben spiegelt Ihre aktuelle Konfiguration wider – einfach kopieren, um ein Szenario zu teilen.")

load_permalink_settings()
init_session_state_defaults()

with st.sidebar:
    sidebar_presets()  # Schnellstart oben, das aktive Preset ist hervorgehoben
    st.header("🏛️ Doppelte Auktion (Hauptansicht, Reiter 1 und 2)")
    st.slider("Werte des Verladers: untere Grenze (Euro je Tour)", *bounds("v0_slider"), key="v0_slider", step=1,
              help="Der Wert v der Tour für den Verlader liegt gleichverteilt zwischen dieser und der oberen Grenze (untere Grenze + Breite).")
    st.slider("Werte des Verladers: Breite (Euro)", *bounds("wv_slider"), key="wv_slider", step=1, help="Obere Grenze minus untere Grenze des Wertebereichs.")
    st.slider("Kosten des Spediteurs: untere Grenze (Euro je Tour)", *bounds("c0_slider"), key="c0_slider", step=1,
              help="Die Kosten c der Tour für den Spediteur liegen gleichverteilt zwischen dieser und der oberen Grenze (untere Grenze + Breite).")
    st.slider("Kosten des Spediteurs: Breite (Euro)", *bounds("wc_slider"), key="wc_slider", step=1, help="Obere Grenze minus untere Grenze des Kostenbereichs.")
    st.slider("Preisregel κ (Prozent)", *bounds("kappa_slider"), key="kappa_slider", step=5,
              help="Preis = (1 − κ)·Forderung + κ·Gebot. 50: die Mitte. 0: der Spediteur setzt den Preis (Forderung). 100: der Verlader setzt den Preis (Gebot).")
    st.slider("Einpreis p (Euro je Tour), Reiter 2", *bounds("p_slider"), key="p_slider", step=1, help="Alle Verlader mit Wert ab p bieten p, alle Spediteure mit Kosten bis p fordern p.")
    st.header("⏳ Warten statt Handeln (Reiter 3)")
    st.slider("Diskontfaktor δ je Runde (Prozent)", *bounds("delta_slider"), key="delta_slider", step=1,
              help="So viel ist ein Euro eine Runde später noch wert, in Prozent. 50: Warten halbiert den Wert. 99: Warten kostet ein Prozent.")
    st.slider("Zahl der Runden T", *bounds("t_slider"), key="t_slider", step=1, help="Wie viele Runden der Spediteur bieten kann; in der letzten Runde bietet er den Monopolpreis des Rests.")
    st.slider("Obergrenze des Werts V (Euro je Tour)", *bounds("vmax_slider"), key="vmax_slider", step=1,
              help="Der Wert des Verladers ist gleichverteilt zwischen 0 und V; die Kosten des Spediteurs sind 0 (nur der Aufschlag zählt).")
    st.toggle("Selbstbindung des Spediteurs", key="commit_toggle",
              help="An: der Spediteur bietet nur einmal, zum Preis V/2, und kann in späteren Runden nicht nachbessern. Aus: er bietet in jeder Runde neu. Die Diagramme zeigen die gewählte Seite, die Tabelle beide.")
    st.header("🕰️ Rundenlänge und Horizont (Reiter 4)")
    st.select_slider("Rundenlänge Δ (Einheiten von 1/r)", options=list(C.DT_CHOICES), key="dt_select",
                     help="Zeit in Einheiten von 1/r (r: Rate, mit der Warten Wert kostet). Der Diskontfaktor je Runde ist e^(−Δ).")
    st.slider("Horizont H (Einheiten von 1/r)", *bounds("h_slider"), key="h_slider", step=C.H_STEP, format="%.2f",
              help="Gesamtdauer: T = H/Δ Runden. Bei kurzer Rundenlänge sind das sehr viele Runden, aber nur eine begrenzte Zeit.")

settings = settings_from_state()
sync_query_params({k: st.session_state[k] for k in SETTING_SPECS})

verdicts = []      # Verdikte für den PDF-Export
tables = _tables()
if tables is None:
    st.warning("Die vorgerechneten Messreihen (data/tables.json) fehlen oder gehören zu einem anderen Rechencode: `python tools/make_grid.py` ausführen. Die Reiter zeigen dann keine Reihen.")

# --- Hauptansicht: doppelte Auktion ---------------------------------------------------------------------------------------------------------------
av = _auction(settings.v0, settings.wv, settings.c0, settings.wc, settings.kappa)
st.markdown("## 🎯 Ergebnis: Was kostet das Geheimnis bei gleichzeitigen Geboten?")
m1, m2, m3 = st.columns(3)
m1.metric("Erstbestes", de(av.fb_gain), help="Erwarteter Gewinn je Tour in Euro, wenn genau dann gehandelt wird, wenn der Wert die Kosten erreicht: nur erreichbar, wenn alles offen läge.")
m2.metric("Zweitbestes", de(av.sb_gain), help="Erwarteter Gewinn je Tour in Euro des besten Verfahrens, bei dem beide freiwillig mitmachen und niemand Geld zuschießt (Myerson und Satterthwaite).")
if av.cs_gain is not None:
    m3.metric("Gleichgewicht", de(av.cs_gain), delta=de(av.cs_gain - av.fb_gain).replace("−", "-"), help="Erwarteter Gewinn je Tour in Euro des linearen Gleichgewichts; die Differenz ist gegen das Erstbeste.")
    m4, m5, _m6 = st.columns(3)
    m4.metric("Anteil am Erstbesten", f"{pct(av.cs_gain / av.fb_gain)} %" if av.fb_gain > 0 else "–", help="Gleichgewichtsgewinn geteilt durch Erstbestes.")
    m5.metric("Ausbleibender Handel", f"{pct(1 - av.cs_prob / av.fb_prob)} %" if av.fb_prob > 0 else "–", help="Anteil der Touren, die sich gemeinsam lohnen würden, aber nicht zustande kommen.")
else:
    m3.metric("Gleichgewicht", "Formel gilt nicht", help="Das lineare Profil ist hier kein Gleichgewicht; die App rechnet keinen Gleichgewichtsgewinn.")
st.caption("Erwarteter Gewinn je Tour in Euro, im Mittel über alle Paare aus Wert und Kosten.")
col_a, col_b = st.columns(2)
with col_a:
    st.plotly_chart(Z.build_region(av), width="stretch", key="region_chart")
    st.caption("Alle Typen (v, c) im Rechteck. Rot: hier würde effizient gehandelt (v ≥ c). Grün: hier wird im Gleichgewicht gehandelt. Der rote Rest ist der ausbleibende Handel.")
with col_b:
    st.plotly_chart(Z.build_strategies(av), width="stretch", key="strategies_chart")
    st.caption("Gebot b(v) und Forderung s(c) im Gleichgewicht, gegen die ehrliche Meldung (gepunktet). Der Verlader bietet weniger, der Spediteur fordert mehr, als es ehrlich wäre.")
st.markdown("#### ❓ Kernfrage: Wie viel Handel kostet das Geheimnis?")
v_main = EV.verdict_auction(av)
show(v_main)
verdicts.append(v_main)
show(EV.verdict_grid_check(av))
with st.expander("Zahlen im Einzelnen"):
    table(EV.auction_rows(av))
st.plotly_chart(Z.build_gain_bars(av, EV.best_one_price_gain(settings)), width="stretch", key="gain_chart")
st.caption("Erwarteter Gewinn je Tour. Der beste Einpreis ist das Maximum der Kurve in Reiter 2.")

# --- Reiter --------------------------------------------------------------------------------------------------------------------------------------
tab1, tab2, tab3, tab4 = st.tabs(["1 Gültigkeit und Preisregel", "2 Viele Gleichgewichte", "3 Warten statt Handeln", "4 Rundenlänge und Horizont"])

# --- Reiter 1 ------------------------------------------------------------------------------------------------------------------------------------
with tab1:
    st.subheader("🔬 Experiment E1: Wo gilt die Formel, und was ist dort das Zweitbeste?")
    st.caption("**Erwartung:** Rücken die Wertebereiche über den Kostenbereich hinaus nach oben (oder weichen die Breiten stark ab), hört das lineare Profil auf, ein Gleichgewicht zu sein; "
               "innerhalb des Gültigkeitsbereichs sollte sein Gewinn das Zweitbeste treffen, nicht nur im symmetrischen Fall. Live bei den Breiten, den Kosten und dem κ der Seitenleiste.")
    shift = _shift(settings.v0, settings.wv, settings.c0, settings.wc, settings.kappa)
    table(EV.shift_table(shift))
    v_shift = EV.verdict_shift(shift, settings)
    show(v_shift)
    verdicts.append(v_shift)
    if tables:
        st.markdown("**Vorgerechnet: Zufallsinstanzen** (Kriterium gegen die numerische Lücke am Gitter; vier Zufalls-Seeds)")
        table(EV.rows_validity(tables))
        v_t1 = EV.verdict_table_validity(tables)
        show(v_t1)
        verdicts.append(v_t1)
    st.markdown("---")
    st.subheader("🔬 Experiment E2: Welche Preisregel hebt am meisten Handelsgewinn?")
    st.caption("**Erwartung:** Die Mitte (κ = ½) liefert den größten Gewinn, und die Kurve ist in κ ↔ 1 − κ symmetrisch; setzt eine Seite den Preis allein (κ = 0 oder 1), bleibt weniger übrig. Live bei den Bereichen der Seitenleiste, nur wo die Formel gilt.")
    krows = _kappa(settings.v0, settings.wv, settings.c0, settings.wc)
    st.plotly_chart(Z.build_kappa_curve(krows, av), width="stretch", key="kappa_chart")
    st.caption("Erwarteter Gewinn je Tour über der Preisregel; fehlen Punkte, gilt die Formel dort nicht.")
    v_kappa = EV.verdict_kappa(krows, settings)
    show(v_kappa)
    verdicts.append(v_kappa)
    table(EV.kappa_table(krows))

# --- Reiter 2 ------------------------------------------------------------------------------------------------------------------------------------
with tab2:
    st.subheader("🔬 Experiment E3: Ist das lineare Gleichgewicht das einzige?")
    st.caption("**Erwartung:** Nein. Wenn alle Verlader mit Wert ab p bieten und alle Spediteure mit Kosten bis p fordern, lohnt es keinem, allein abzuweichen: auch jeder Einpreis ist ein Gleichgewicht, "
               "mit weniger Handelsgewinn. Welches Gleichgewicht gespielt wird, sagt die Rechnung nicht: das ist das Auswahlproblem. Live bei den Bereichen und dem Einpreis der Seitenleiste.")
    ov, orows = _one_price(settings.v0, settings.wv, settings.c0, settings.wc, settings.kappa, settings.p)
    st.plotly_chart(Z.build_one_price(ov, av.cs_gain), width="stretch", key="one_price_chart")
    st.caption("Erwarteter Gewinn je Tour des Einpreis-Gleichgewichts über dem Einpreis. Gestrichelt: Zweitbestes; Linie: lineares Gleichgewicht (wo die Formel gilt).")
    v_one = EV.verdict_one_price(ov)
    show(v_one)
    verdicts.append(v_one)
    st.markdown("**Einpreis-Gleichgewichte im Durchlauf** (Euro je Tour; Lücke: Gegenprobe am Gitter)")
    table(orows)

# --- Reiter 3 ------------------------------------------------------------------------------------------------------------------------------------
with tab3:
    st.subheader("🔬 Experiment E4: Wenn der Spediteur sich nicht binden kann, wartet der Verlader")
    st.caption("**Erwartung:** Ohne Selbstbindung sinkt der Preis von Runde zu Runde, weil der Spediteur nach den Hochpreis-Käufern die Übrigen erreichen will; wer den höchsten Wert hat, kauft zuerst, aber alle warten ein wenig. "
               "Der Gewinn des Spediteurs fällt unter den der Selbstbindung; ob der Gesamtwert dabei fällt oder steigt, sagt das Verdikt. Live bei δ, T und V der Seitenleiste.")
    cv = _coase(settings.delta, settings.T, settings.vmax, settings.commit)
    tot = EV.coase_totals(cv)
    cur, other = (tot["bound"], tot["free"]) if settings.commit else (tot["free"], tot["bound"])
    ref = "ohne Selbstbindung" if settings.commit else "mit Selbstbindung"
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Gewinn Spediteur", de(cur["profit"]), delta=de(cur["profit"] - other["profit"]).replace("−", "-"), help=f"Euro je Tour, diskontiert; die Differenz ist gegen den Pfad {ref}.")
    k2.metric("Überschuss Verlader", de(cur["surplus"]), delta=de(cur["surplus"] - other["surplus"]).replace("−", "-"), help=f"Euro je Tour, diskontiert; die Differenz ist gegen den Pfad {ref}.")
    k3.metric("Gesamtwert", de(cur["welfare"]), delta=de(cur["welfare"] - other["welfare"]).replace("−", "-"), help=f"Diskontierter Wert der gehandelten Touren; die Differenz ist gegen den Pfad {ref}. Das Erstbeste wäre {de(tot['first_best'])}.")
    k4.metric("Nie gekauft", f"{pct(cur['unsold'])} %", help="Anteil der Verlader, die bis zum Ende nicht kaufen.")
    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(Z.build_coase_prices(cv), width="stretch", key="coase_price_chart")
        n_vis = EV.visible_rounds(cv.path)
        tail = f" Gezeigt: Runde 1 bis {n_vis} von {settings.T} (bis dahin haben mindestens 99,99 % der Verlader gekauft)." if n_vis < settings.T else ""
        st.caption("Preis je Runde in Euro je Tour. Gestrichelt das Einmalangebot mit Selbstbindung." + tail)
    with c2:
        st.plotly_chart(Z.build_coase_buyers(cv), width="stretch", key="coase_buyer_chart")
        n_vis_b = EV.visible_rounds(cv.shown)
        tail_b = f" Gezeigt: Runde 1 bis {n_vis_b} von {len(cv.shown.mass)} (bis dahin haben mindestens 99,99 % der Verlader gekauft)." if n_vis_b < len(cv.shown.mass) else ""
        st.caption("Wer kauft wann: Anteil aller Verlader je Runde und aufgelaufen." + tail_b)
    v_coase = EV.verdict_coase(cv)
    show(v_coase)
    verdicts.append(v_coase)
    st.markdown("**Ohne und mit Selbstbindung** (Euro je Tour)")
    table(EV.commitment_rows(cv))

# --- Reiter 4 ------------------------------------------------------------------------------------------------------------------------------------
with tab4:
    st.subheader("🔬 Experiment E5: Fällt der Preis auf die Kosten, wenn die Runden kurz werden?")
    st.caption("**Erwartung:** Je größer der Diskontfaktor (je kürzer die Runde), desto niedriger der erste Preis, solange der Horizont lang ist; bei kurzem Horizont soll das kippen. Bei unendlichem Horizont folgt der Preis einer Grenzform; "
               "bei festem Zeithorizont fällt er nicht auf null. Beide Formeln sind aus Messungen erkannt, nicht bewiesen. Live bei Δ und H der Seitenleiste und bei T aus Reiter 3.")
    c3, c4 = st.columns(2)
    with c3:
        curves = _curves(settings.T)
        st.plotly_chart(Z.build_limit_curve(curves, settings.T, settings.delta_f), width="stretch", key="limit_chart")
        st.caption("Erster Preis über dem Diskontfaktor für feste Rundenzahlen; gestrichelt der Grenzfall unendlichen Horizonts (Grenzform s/(1+s), s = √(1−δ)). Das gewählte δ und T aus Reiter 3 sind markiert.")
    frows = _fixed(settings.dt, settings.H)
    with c4:
        st.plotly_chart(Z.build_fixed_horizon(frows, settings.dt), width="stretch", key="fixed_chart")
        st.caption("Erster Preis über der Rundenlänge bei festem Horizont H; die Rundenlänge der Seitenleiste ist markiert.")
    v_curves = EV.verdict_delta_curves(curves, settings.T)
    show(v_curves)
    verdicts.append(v_curves)
    v_fixed = EV.verdict_fixed(frows, settings)
    show(v_fixed)
    verdicts.append(v_fixed)
    table(EV.fixed_table(frows))
    st.markdown("**Wie lang muss der Horizont sein?** Kleinste Rundenzahl T, bei der der erste Preis höchstens 1 % vom Grenzwert bei unendlichem Horizont abweicht")
    table(EV.horizon_table())
    if tables:
        st.markdown("**Vorgerechnet: Abweichungsprüfer** (kein Spediteur gewinnt durch Abweichen, bis T = 200)")
        table(EV.rows_deviation(tables))
        v_dev = EV.verdict_table_deviation(tables)
        show(v_dev)
        verdicts.append(v_dev)

# --- Verwandte Demos, Grenzen, Formeln -----------------------------------------------------------------------------------------------------------
st.markdown("---")
st.subheader("🔗 Verwandte Demos")
st.markdown(
    "- [`verhandlung-demo`](https://github.com/sebastian-hanisch/verhandlung-demo): Verhandlung bei **vollständiger** Information (abwechselnde Angebote, Nash-Lösung); hier ist die Information privat.\n"
    "- `myerson-satterthwaite-demo`: Mechanismen auf einem Typengitter; das Zweitbeste dieser Demo ist dort als lineares Programm gerechnet, das Gleichgewicht der doppelten Auktion dort ausdrücklich nicht.\n"
    "- `einzelgut-auktion-demo`: der Verkäufer legt die Regeln fest (Auktion eines Guts); die Selbstbindung ist dort vorausgesetzt, hier wird gemessen, was sie wert ist.\n"
    "- `vertragsdesign-demo`: private Information über das **Handeln** statt über Werte.\n"
    "- `vorabsignale-demo`: Absprachen vor dem Spiel ohne private Information und ohne teure Signale."
)

st.subheader("🚧 Wo die Annahmen enden")
st.markdown(T.ASSUMPTIONS_MARKDOWN)

st.subheader("Nicht umgesetzt")
st.markdown(T.NOT_IMPLEMENTED_MARKDOWN)

with st.expander("📐 Mathematische Formulierung"):
    st.markdown(T.MATH_MARKDOWN)

st.subheader("📄 Ergebnisse als PDF")
if st.button("PDF erstellen", key="pdf_button"):
    from gvh_pdf_export import build_pdf
    st.session_state["pdf_bytes"] = build_pdf(settings, av, EV.analyse_coase(settings), verdicts)
if st.session_state.get("pdf_bytes"):
    st.download_button("⬇️ PDF herunterladen", st.session_state["pdf_bytes"], file_name="geheimnis-verhandlung.pdf", mime="application/pdf", key="pdf_download")

st.markdown("---")
st.caption(
    "Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – "
    "Operations Research und Machine Learning ([Über mich](https://sebastianhanisch.net/ueber-mich.html)). "
    "Mehr zu den Demos: [Interaktive Demos](https://sebastianhanisch.net/demos.html)."
)
