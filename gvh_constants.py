"""Konstanten: Regler-Grenzen, feste Annahmen, Farben und Presets.

Alle Beträge sind Euro je Tour: der Wert einer Tour für den Verlader und die Kosten des Spediteurs sind Modellannahmen, keine Daten echter Betriebe.
Rechengrenzen (Komplexität am Regler-Maximum): die Auktionsformeln sind geschlossen (O(1)); die Gitterprüfung rechnet 2 * 21 Typen * 2 001 Gebote;
die Coase-Rekursion ist O(T) mit T <= 3 000 (Reiter 3) und O(T) je Rundenlänge mit T <= 40 000 (Reiter 4, elf Rundenlängen)."""

# --- Doppelte Auktion (Reiter 1 und 2): Bereiche als Anfang und Breite, damit obere > untere Grenze immer gilt ---------------------------------------
V0_MIN, V0_MAX, DEFAULT_V0 = 0, 120, 0            # untere Grenze des Werts v (Euro je Tour)
WV_MIN, WV_MAX, DEFAULT_WV = 10, 120, 60          # Breite des Wertebereichs
C0_MIN, C0_MAX, DEFAULT_C0 = 0, 120, 0            # untere Grenze der Kosten c
WC_MIN, WC_MAX, DEFAULT_WC = 10, 120, 60          # Breite des Kostenbereichs
KAPPA_MIN, KAPPA_MAX, DEFAULT_KAPPA = 0, 100, 50  # Preisregel in Prozent: Preis = (1 - kappa) * Forderung + kappa * Gebot
P_MIN, P_MAX, DEFAULT_P = 0, 200, 20              # Einpreis p (Euro je Tour), Reiter 2

# --- Warten statt Handeln (Reiter 3) ------------------------------------------------------------------------------------------------------------------
DELTA_MIN, DELTA_MAX, DEFAULT_DELTA = 0, 99, 50   # Diskontfaktor je Runde in Prozent
T_MIN, T_MAX, DEFAULT_T = 1, 3000, 200            # Zahl der Runden
VMAX_MIN, VMAX_MAX, DEFAULT_VMAX = 10, 120, 60    # Obergrenze des Werts des Verladers (Euro je Tour), Reiter 3
DEFAULT_COMMIT = False                            # Selbstbindung: ein einziges Angebot zum Preis V / 2

# --- Rundenlänge und Horizont (Reiter 4); Zeit in Einheiten von 1 / r (r = Rate der Wartekosten) ------------------------------------------------------
DT_CHOICES = (1.0, 0.5, 0.25, 0.1, 0.05, 0.02, 0.01, 0.005, 0.002, 0.001, 0.0005)
DEFAULT_DT = 0.1
H_MIN, H_MAX, DEFAULT_H, H_STEP = 0.25, 10.0, 1.0, 0.25
FIXED_HORIZON_T_MAX = 40_000                       # H_MAX / min(DT_CHOICES) = 20 000, mit Spielraum

# --- Prüfungen in der App (die Konstanten der vorgerechneten Reihen stehen in gvh_experiments.py) -------------------------------------------------------------
GAP_TOL = 1e-9                                     # Beste-Antwort-Lücke unter dieser Grenze (Euro) zählt als null
VALID_TOL = 1e-9                                   # Rundungsspielraum für die Gültigkeitsabstände (Euro)
GRID_TYPES = 21                                    # Typen je Seite bei der Gitterprüfung in der App
GRID_POINTS = 2001                                 # Gebote im Gitter der App
KAPPA_GRID = tuple(range(0, 101, 5))               # Preisregeln der Kurve in Reiter 1
DELTA_CURVE = tuple(range(0, 100))                 # Diskontfaktoren (Prozent) der Kurve in Reiter 4

# --- Farben ---------------------------------------------------------------------------------------------------------------------------------------------
COLOR_FIRST = "#4c78a8"       # Erstbestes
COLOR_SECOND = "#2F6B65"      # Zweitbestes
COLOR_EQ = "#e08e0b"          # Gleichgewicht der doppelten Auktion
COLOR_ONE = "#8e6bbf"         # Einpreis
COLOR_LOSS = "rgba(200,60,60,0.35)"
COLOR_GAIN = "rgba(47,107,101,0.45)"
COLOR_GREY = "rgba(150,150,150,0.55)"

PRESETS = {
    "Klassiker (beide 0 bis 60 Euro)": {},
    "Verschobene Bereiche (Grenzfall)": {"v0": 20},
    "Ungültig: Bereiche zu weit auseinander": {"v0": 36},
    "Verkäufer setzt den Preis (κ = 0)": {"kappa": 0},
    "Einpreis bei der Mitte (30 Euro)": {"p": 30},
    "Geduldig (δ = 0,9)": {"delta": 90},
    "Sehr geduldig (δ = 0,99, 3 000 Runden)": {"delta": 99, "T": 3000},
    "Kurze Runden bei festem Horizont": {"dt": 0.001, "H": 1.0},
}
PRESET_HELP = {
    "Klassiker (beide 0 bis 60 Euro)": "Wert und Kosten gleichverteilt zwischen 0 und 60 Euro je Tour, Preis in der Mitte zwischen Gebot und Forderung; Warten mit Diskontfaktor 0,5 über 200 Runden.",
    "Verschobene Bereiche (Grenzfall)": "Werte zwischen 20 und 80 Euro, Kosten zwischen 0 und 60: gerade noch im Gültigkeitsbereich der Formel (v₀ − c₀ = L/4).",
    "Ungültig: Bereiche zu weit auseinander": "Werte zwischen 36 und 96 Euro: die Formelstrategien sind hier kein Gleichgewicht; die App meldet das, statt eine Zahl zu zeigen.",
    "Verkäufer setzt den Preis (κ = 0)": "Der Preis ist die Forderung des Spediteurs; der Verlader sagt seinen Wert, der Spediteur fordert aus seinem Kostenwert heraus.",
    "Einpreis bei der Mitte (30 Euro)": "Reiter 2: alle Verlader mit Wert ab 30 Euro bieten 30, alle Spediteure mit Kosten bis 30 fordern 30; auch das ist ein Gleichgewicht.",
    "Geduldig (δ = 0,9)": "Reiter 3: Warten kostet nur 10 Prozent je Runde; der Spediteur bietet 200 Runden lang.",
    "Sehr geduldig (δ = 0,99, 3 000 Runden)": "Reiter 3: Warten kostet 1 Prozent je Runde, der Horizont ist lang (3 000 Runden).",
    "Kurze Runden bei festem Horizont": "Reiter 4: Rundenlänge 0,001 bei einem Horizont von 1: sehr viele kurze Runden, aber nur eine begrenzte Zeit.",
}
