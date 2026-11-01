"""Gemeinsame Fixtures: die Mini-Instanzen, an denen jede Einheit von Hand geprüft wird (DEMO-PLAYBOOK §1b). Alle Erwartungswerte sind von Hand gerechnet (Rechnung im Docstring)
und stehen als Brüche da; die Formeln der Demo laufen mit Fraction genauso wie mit float."""

import sys
from fractions import Fraction as F
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))


@pytest.fixture
def klassiker():
    """Doppelte Auktion, v und c gleichverteilt auf [0, 1], Mittelpunkt (kappa = 1/2).

    Bedingungen erster Ordnung: bs = 1/(2 - 1/2) = 2/3, bb = 1/(1 + 1/2) = 2/3, p = q = 1/3; ab = (1/9 * 2/3)/(1 - 1/9) = 1/12, as = 1/3 * (1/12 + 2/3) = 1/4.
    Also b(v) = 2v/3 + 1/12 und s(c) = 2c/3 + 1/4; b(1) = 3/4, b(0) = 1/12, s(0) = 1/4, s(1) = 11/12.
    Handel genau bei b(v) >= s(c), das heißt 2/3 (v - c) >= 1/6, also v - c >= 1/4 (= L/4). Die Handelsmenge ist ein rechtwinkliges Dreieck mit Katheten 3/4:
    Fläche (3/4)^2/2 = 9/32 = Handelswahrscheinlichkeit; der mittlere Gewinn auf dem Dreieck ist 1/4 + (3/4)/3 = 1/2, also Gewinn 9/32 * 1/2 = 9/64.
    Erstbestes: Handel bei v >= c: Wahrscheinlichkeit 1/2, mittlerer Gewinn 1/3, Gewinn 1/6. Zweitbestes: G(1/4) = 2 * 9/64 - 1 * 9/32 = 0, Schwelle 1/4.
    Typenpaare: (v, c) = (1/2, 1/4): b = 5/12 = s, Handel bei Gleichstand, Preis 5/12; (1/2, 1/2): b = 5/12 < s = 7/12, kein Handel; (1, 0): b = 3/4, s = 1/4, Preis 1/2."""
    return {"range": (F(0), F(1), F(0), F(1)), "kappa": F(1, 2), "ab": F(1, 12), "bb": F(2, 3), "as": F(1, 4), "bs": F(2, 3), "thr": F(1, 4),
            "prob": F(9, 32), "gain": F(9, 64), "fb_prob": F(1, 2), "fb_gain": F(1, 6), "theta": F(1, 4)}


@pytest.fixture
def grenzfall():
    """Werte v ~ U[1/3, 4/3], Kosten c ~ U[0, 1], kappa = 1/2: L = v1 - c0 = 4/3, L/4 = 1/3 = v0 - c0 (Grenzfall, noch gültig); v1 - c1 = 1/3 = L/4 ebenfalls.

    b(v) = 2v/3 + (v1 + 3 c0)/12 = 2v/3 + 1/9, s(c) = 2c/3 + (3 v1 + c0)/12 = 2c/3 + 1/3. Niedrigste Forderung s(0) = 1/3 = niedrigstes Gebot b(1/3) = 2/9 + 1/9 = 1/3 (Abstand 0);
    höchste Forderung s(1) = 1 = höchstes Gebot b(4/3) = 8/9 + 1/9 = 1 (Abstand 0). Handelsmenge: Dreieck mit Katheten 3L/4 = 1, Fläche 1/2 = Wahrscheinlichkeit
    (Rechteck hat Fläche 1); mittlerer Gewinn L/4 + 1/3 = 2/3 = L/2; Gewinn 1/2 * 2/3 = 1/3 (= 9 L^3 / 64 für Rechteckfläche 1)."""
    return {"range": (F(1, 3), F(4, 3), F(0), F(1)), "kappa": F(1, 2), "prob": F(1, 2), "gain": F(1, 3)}


@pytest.fixture
def ungueltig():
    """Werte v ~ U[2/5, 7/5], Kosten c ~ U[0, 1], kappa = 1/2: L = 7/5, L/4 = 7/20 < v0 - c0 = 2/5.

    Abstand niedrigste Forderung minus niedrigstes Gebot = 2/3 * (L/4 - (v0 - c0)) = 2/3 * (7/20 - 8/20) = -1/30; dasselbe für die höchsten (v1 - c1 = 2/5)."""
    return {"range": (F(2, 5), F(7, 5), F(0), F(1)), "kappa": F(1, 2), "margin": F(-1, 30)}


@pytest.fixture
def verkaeufer_preis():
    """kappa = 0 (der Verkäufer setzt den Preis), v, c ~ U[0, 1]: bs = 1/2, bb = 1, p = 1/2, q = 0: ab = 0, as = 1/2 * (0 + 1 * 1) = 1/2. Also b(v) = v, s(c) = 1/2 + c/2.

    Handel bei v >= (1 + c)/2: Wahrscheinlichkeit 1/4 (Integral von (1 - c)/2), Gewinn 1/8 (mit u = (1 + c)/2: 2 * Integral über u von 1/2 bis 1 von (3/2 - 3u + 3u^2/2) = 2 * (1/2 - 7/16))."""
    return {"range": (F(0), F(1), F(0), F(1)), "kappa": F(0), "ab": F(0), "bb": F(1), "as": F(1, 2), "bs": F(1, 2), "prob": F(1, 4), "gain": F(1, 8)}


@pytest.fixture
def coase_halb():
    """Coase-Rekursion bei delta = 1/2 (Kosten 0, Verlader U[0, 1]).

    T = 1: Preis 1/2, Grenze 1/2, Gewinn 1/4. T = 2: rho = 1 - 1/2 * (1 - 1/2) = 3/4; pi2 = (9/16)/(2 * (3/4 - 1/2 * 1/4)) = (9/16)/(5/4) = 9/20; Grenze w2 = (9/20)/(3/4) = 3/5;
    Gewinn k2 = 9/20 * 2/5 + 1/2 * 1/4 * 9/25 = 9/50 + 9/200 = 9/40. Probe der Indifferenz: der Grenztyp 3/5 gewinnt jetzt 3/5 - 9/20 = 3/20, in Runde 2 (Preis 3/10) 1/2 * (3/5 - 3/10) = 3/20.
    T = 3: rho = 1 - 1/2 * (1 - 9/20) = 29/40; pi3 = (841/1600)/(2 * (29/40 - 9/80)) = (841/1600)/(49/40) = 841/1960; w3 = 29/49.
    Pfad T = 2: Runde 1 Preis 9/20, Käufer ab 3/5 (Anteil 2/5); Runde 2 Preis 1/2 * 3/5 = 3/10, Käufer 3/10 bis 3/5 (Anteil 3/10), nie gekauft 3/10.
    Gewinn 9/20 * 2/5 + 1/2 * 3/10 * 3/10 = 9/40; Überschuss: Runde 1 (1 - 9/25)/2 - 9/50 = 7/50, Runde 2 1/2 * ((9/25 - 9/100)/2 - 9/100) = 9/400, Summe 13/80;
    Gesamtwert 8/25 + 1/2 * 27/200 = 31/80 (= 9/40 + 13/80); mittlere Wartezeit der Käufer (0 * 2/5 + 1 * 3/10)/(7/10) = 3/7."""
    return {"delta": F(1, 2), "pi": {1: F(1, 2), 2: F(9, 20), 3: F(841, 1960)}, "w": {1: F(1, 2), 2: F(3, 5), 3: F(29, 49)}, "k": {1: F(1, 4), 2: F(9, 40)},
            "profit2": F(9, 40), "surplus2": F(13, 80), "welfare2": F(31, 80), "unsold2": F(3, 10), "wait2": F(3, 7)}
