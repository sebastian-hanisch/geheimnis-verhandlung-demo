"""PDF-Export (fpdf2, Kernschriften): Einstellungen, Kennzahlen der Hauptansicht und des Warte-Modells, dazu die Verdikte. Erst nach Klick erzeugt (DEMO-PLAYBOOK §1c)."""

from __future__ import annotations

from fpdf import FPDF

import gvh_evaluation as V
from gvh_scenario import Settings

_REPLACE = {"–": "-", "—": "-", "≤": "<=", "≥": ">=", "≠": "!=", "√": "Wurzel", "²": "2", "Σ": "Summe", "°": " Grad", "·": "*", "−": "-", "„": '"', "“": '"', "∞": "unendlich",
            "→": "->", "ε": "eps", "β": "beta", "α": "alpha", "θ": "theta", "λ": "lambda", "σ": "sigma", "π": "pi", "δ": "delta", "η": "eta", "Δ": "Delta", "γ": "gamma", "ρ": "rho",
            "κ": "kappa", "φ": "phi", "≈": "~", "½": "1/2", "…": "...", "‚": ",", "‘": "'", "’": "'", "”": '"', "µ": "mu", "∈": "in", "¹": "1", "₀": "0", "₁": "1", "₂": "2",
            "±": "+-", "⋅": "*", "€": "EUR", "⁻": "-", "⁰": "0"}


def _latin(text: str) -> str:
    """Kernschriften kennen nur Latin-1 (Umlaute gehören dazu): Sonderzeichen ersetzen, Markdown-Zeichen entfernen."""
    for a, b in _REPLACE.items():
        text = text.replace(a, b)
    return text.replace("**", "").replace("`", "").encode("latin-1", "replace").decode("latin-1")


def build_pdf(s: Settings, av: V.AuctionView, cv: V.CoaseView, verdicts: list[tuple[str, str]]) -> bytes:
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 15)
    pdf.cell(0, 9, _latin("Verhandeln mit privaten Werten"), new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 10)
    pdf.multi_cell(0, 5, _latin(f"Werte des Verladers: {V.de(s.v0, 0)} bis {V.de(s.v1, 0)} Euro je Tour; Kosten des Spediteurs: {V.de(s.c0, 0)} bis {V.de(s.c1, 0)} Euro; Preisregel kappa = {V.de(s.kappa_f, 2)}; "
                                f"Einpreis {V.de(s.p, 0)} Euro. Warten: delta = {V.de(s.delta_f, 2)}, {s.T} Runden, V = {V.de(s.vmax, 0)} Euro; Selbstbindung {'an' if s.commit else 'aus'}. "
                                f"Rundenlänge {V.de(s.dt, 4)}, Horizont {V.de(s.H, 2)}."), new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 7, "Doppelte Auktion (Euro je Tour)", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 10)
    lines = [f"Erstbestes: {V.de(av.fb_gain, 2)}; Zweitbestes: {V.de(av.sb_gain, 2)}."]
    if av.cs_gain is not None:
        lines.append(f"Gleichgewicht (linear): {V.de(av.cs_gain, 2)}, das sind {V.pct(av.cs_gain / av.fb_gain)} % des Erstbesten.")
    else:
        lines.append("Das lineare Profil ist bei diesen Bereichen kein Gleichgewicht: kein Gleichgewichtsgewinn.")
    tot = V.coase_totals(cv)
    lines.append(f"Warten statt Handeln: erster Preis {V.de(cv.first_price, 2)} Euro; Gewinn des Spediteurs {V.de(tot['free']['profit'], 2)} (mit Selbstbindung {V.de(tot['bound']['profit'], 2)}); "
                 f"Gesamtwert {V.de(tot['free']['welfare'], 2)} (mit Selbstbindung {V.de(tot['bound']['welfare'], 2)}).")
    for line in lines:
        pdf.multi_cell(0, 5, _latin(line), new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 7, "Verdikte", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 10)
    for _, text in verdicts:
        pdf.multi_cell(0, 5, _latin(text), new_x="LMARGIN", new_y="NEXT")
        pdf.ln(1)
    pdf.set_font("Helvetica", "I", 8)
    pdf.multi_cell(0, 4, _latin("Werte, Kosten, Gleichverteilung, Eigennutz und Diskont sind Modellannahmen, keine Aussagen über echte Betriebe. Alle Zahlen sind eigene Rechnung "
                                "(geschlossene Formeln), gestützt durch Handrechnung und unabhängige Rechenwege in den Tests."), new_x="LMARGIN", new_y="NEXT")
    return bytes(pdf.output())
