"""Feste Texte der App (Einleitung, Erklärungen, Annahmen, Formeln). Zahlen, die ein Befund sind, stehen hier nicht: sie kommen als f-String aus der Rechnung (Verdikte in
gvh_evaluation.py) oder stehen in der README und in tests/test_claims.py. Die Annahmentabelle steht wortgleich in der README (tests/test_texts.py vergleicht)."""

INTRO = """
Ein **Verlader** will eine Tour fahren lassen, ein **Spediteur** will sie fahren. Was die Tour dem Verlader wert ist und was sie den Spediteur kostet, weiß jeder nur von sich selbst: das ist das **Geheimnis**.
`verhandlung-demo` setzt voraus, dass beide alles voneinander wissen; hier ist die private Information der Gegenstand. Zwei Fragen: Kommt der Handel zustande, wenn beide gleichzeitig ein Gebot und eine Forderung nennen
(**doppelte Auktion**, nach Chatterjee und Samuelson), und was ändert sich, wenn nur der Verlader ein Geheimnis hat und der Spediteur in jeder Runde einen Preis bietet (**Warten statt Handeln**, die Frage der Coase-Vermutung)?
Beträge sind Euro je Tour. Eigennutz, Gleichverteilung, Unabhängigkeit der Werte, Diskont und die Kenntnis der Verteilungen sind **Modellannahmen**, keine Aussagen über echte Betriebe.

Weiter unten: vier Reiter mit den Experimenten E1 bis E5, **🚧 Wo die Annahmen enden**, **Nicht umgesetzt** und der Expander **📐 Mathematische Formulierung**.
"""

EXPLAINER = """
1. **Jeder kennt nur sich selbst.** Der Verlader kennt seinen Wert v, der Spediteur seine Kosten c; die Verteilung der anderen Seite (gleichverteilt zwischen zwei Grenzen) kennen beide.
2. **Beide nennen gleichzeitig eine Zahl:** der Verlader ein Gebot b, der Spediteur eine Forderung a. Ist b ≥ a, wird gehandelt, zum Preis (1 − κ)·a + κ·b; bei κ = ½ in der Mitte.
3. **Ehrlich melden lohnt nicht:** ein Verlader, der seinen Wert nennt, zahlt zu viel; ein Spediteur, der seine Kosten nennt, verdient nichts. Im **Gleichgewicht** ist jede Strategie die beste Antwort auf die der anderen Seite.
   Bei Gleichverteilung gibt es ein Gleichgewicht mit geraden Linien b(v) und s(c); bei κ = ½ haben sie die Neigung 2/3 statt 1 der ehrlichen Meldung (Reiter 1).
4. **Warum Handel ausbleibt:** wer weniger bietet, als er zahlen würde, und mehr fordert, als er braucht, verpasst Geschäfte, bei denen beide gewonnen hätten. Reiter 1 zählt, wie viele.
5. **Zweiter Teil (Reiter 3 und 4):** nur der Verlader hat ein Geheimnis; der Spediteur bietet in jeder Runde einen Preis und wartet, wenn niemand kauft. Warten kostet beide Zeit (Diskontfaktor δ); wer den höchsten Wert hat, kauft zuerst.
"""

CONTROLS_TABLE = """
| Begriff oder Regler | Bedeutung |
|---|---|
| **Wert v, Kosten c** | privat: der Verlader kennt v, der Spediteur c (Euro je Tour); beide gleichverteilt zwischen den Grenzen der Seitenleiste |
| **Gebot, Forderung** | was der Verlader bzw. der Spediteur nennt; gehandelt wird, wenn das Gebot die Forderung erreicht |
| **Preisregel κ** | Preis = (1 − κ)·Forderung + κ·Gebot; ½ ist die Mitte, 0 der Preis des Spediteurs, 1 der Preis des Verladers |
| **Gleichgewicht** | niemand gewinnt, wenn er allein anders meldet; hier: Bayes-Nash-Gleichgewicht der beiden Meldungen bei bekannten Verteilungen |
| **Erstbestes** | Handel genau dann, wenn v ≥ c: alle Gewinne gehoben, aber nicht erreichbar, wenn jeder sein Geheimnis behält |
| **Zweitbestes** | das Beste, was ein Verfahren schafft, bei dem beide freiwillig mitmachen, niemand Geld zuschießt und jeder nach eigenem Vorteil meldet (Myerson und Satterthwaite) |
| **Gültigkeitsbereich** | die Formelstrategien sind nur dort ein Gleichgewicht, wo die niedrigste Forderung nicht unter dem niedrigsten Gebot und die höchste nicht unter dem höchsten liegt (bei κ = 0 entfällt die zweite, bei κ = 1 die erste Bedingung) |
| **Einpreis-Gleichgewicht** | alle Verlader mit Wert ab p bieten p, alle Spediteure mit Kosten bis p fordern p: auch das ist ein Gleichgewicht, mit weniger Handelsgewinn (Reiter 2) |
| **Selbstbindung** | der Spediteur legt sich auf ein einziges Angebot zum Preis V/2 fest und kann in späteren Runden nicht nachbessern |
| **Diskontfaktor δ, Runden T** | δ: so viel ist ein Euro eine Runde später noch wert; T: wie viele Runden der Spediteur bieten kann |
| **Skimming** | wer den höchsten Wert hat, kauft zuerst; mit jeder Runde sinkt der Preis und es kaufen niedrigere Werte |
| **Coase-Vermutung** | die Vermutung, dass der erste Preis gegen die Kosten fällt, wenn die Runden kurz werden (Reiter 4 misst, wann und wann nicht) |
| **Rundenlänge Δ, Horizont H** | Zeit in Einheiten von 1/r (r: Rate, mit der Warten Wert kostet): δ = e^(−r·Δ), T = H/Δ Runden |
"""

ASSUMPTIONS_MARKDOWN = """
| Annahme | Was passiert, wenn sie verletzt ist | Wer setzt an |
|---|---|---|
| **Gleichverteilte, voneinander unabhängige Werte und Kosten; beide kennen die Verteilung der Gegenseite** | Bei anderen Verteilungen sind die Linien kein Gleichgewicht mehr; ein anderes Gleichgewicht wird nicht gerechnet. | – |
| **Gültigkeitsbereich der Formel** (bei κ = ½: v₀ − c₀ ≤ L/4 und v₁ − c₁ ≤ L/4, L = v₁ − c₀) | Außerhalb ist das lineare Profil kein Gleichgewicht (am Gitter gemessen). Die App meldet „Formel gilt hier nicht“ und rechnet keinen Gleichgewichtsgewinn; das Gleichgewicht dort ist nicht berechnet. | – |
| **Ein Verlader und ein Spediteur** | Viele Käufer und Verkäufer (mehr Bieter, Handelsreduktion) rechnet diese Demo nicht. | – |
| **Der Spediteur macht alle Angebote; der Verlader nur kaufen oder warten** | Machen beide abwechselnd Angebote, ist das ein anderes Modell. Bei vollständiger Information rechnet `verhandlung-demo` es; mit privater Information ist es hier nicht gerechnet. | `verhandlung-demo` (volle Information) |
| **Kosten des Spediteurs gleich dem niedrigsten Wert des Verladers (kein Abstand)** | Mit Abstand zwischen Kosten und niedrigstem Wert ändert sich das Bild; dieser Fall ist nicht gerechnet (die Gitter-Löser versagten, siehe README). | – |
| **Private Information nur beim Verlader (Reiter 3 und 4)** | Haben beide Seiten ein Geheimnis und verzögern strategisch, ist das ein anderes Modell; hier nicht gerechnet. | – |
| **Beide diskontieren gleich, der Horizont ist bekannt, Eigennutz** | Ungeduld, unbekannter Horizont oder Fairness bei den Menschen ändern die Zahlen; die App sagt nichts über echte Verhandler. | – |
| **Keine Daten echter Betriebe** | Alle Werte sind Modellwerte; die Zahlen gelten für diese Gleichverteilungen, nicht für die Praxis. | – |
"""

MATH_MARKDOWN = r"""
**Doppelte Auktion.** Werte $v \sim U[v_0, v_1]$, Kosten $c \sim U[c_0, c_1]$ unabhängig. Gebot $b(v)$, Forderung $a(c)$; Handel genau bei $b \ge a$ zum Preis $(1-\kappa)\,a + \kappa\,b$.
Lineares Gleichgewicht $b(v) = \alpha_b + \beta_b v$, $a(c) = \alpha_s + \beta_s c$ aus den Bedingungen erster Ordnung:

$$\beta_s = \frac{1}{2-\kappa}, \qquad \beta_b = \frac{1}{1+\kappa}, \qquad a(c) = \frac{c + (1-\kappa)\,(\alpha_b + \beta_b v_1)}{2-\kappa}, \qquad b(v) = \frac{v + \kappa\,(\alpha_s + \beta_s c_0)}{1+\kappa}.$$

Für $\kappa = \tfrac12$: $b(v) = \tfrac{2}{3}v + \tfrac{v_1 + 3c_0}{12}$, $a(c) = \tfrac{2}{3}c + \tfrac{3v_1 + c_0}{12}$; gehandelt wird genau bei $v - c \ge L/4$ mit $L = v_1 - c_0$.

**Gültigkeit.** Das Profil ist genau dann ein Gleichgewicht, wenn $a(c_0) \ge b(v_0)$ und $a(c_1) \ge b(v_1)$; bei $\kappa = 0$ entfällt die zweite, bei $\kappa = 1$ die erste Bedingung (Herleitung: die Auszahlung ist zwischen niedrigstem und höchstem Gebot konkav, außerhalb steigend bzw. null; bei $\kappa = 0$ hängt der Preis nicht vom Gebot ab).
Für $\kappa = \tfrac12$ heißt das $v_0 - c_0 \le L/4$ und $v_1 - c_1 \le L/4$. Dann ist die Handelsmenge ein Dreieck mit Katheten $3L/4$:
Handelswahrscheinlichkeit $\tfrac{9L^2}{32\,W_vW_c}$, Gewinn $\tfrac{9L^3}{64\,W_vW_c}$ mit den Breiten $W_v = v_1 - v_0$, $W_c = c_1 - c_0$.

**Zweitbestes** (Myerson–Satterthwaite, Gleichverteilung): Handel genau bei $v - c \ge \theta L$, wobei $\theta = 0$, falls $G(0) \ge 0$, sonst die Wurzel in $[0, \tfrac12)$ von

$$G(\theta) = \mathbb{E}\big[(2(v-c) - L)\,\mathbf 1\{v - c \ge \theta L\}\big] = 0 .$$

**Einpreis.** Verlader mit $v \ge p$ bieten $p$, Spediteure mit $c \le p$ fordern $p$: Handel genau bei $v \ge p \ge c$ zum Preis $p$.

**Warten statt Handeln.** Kosten 0, Wert $v \sim U[0, V]$, $T$ Runden, Diskontfaktor $\delta$. Bei $t$ verbleibenden Runden und Träger $[0, x]$ ist der Preis $\pi_t\,x$, die Kaufgrenze $w_t\,x$ und der Gewinn $k_t\,x^2$ (Dichte 1):

$$\rho = 1 - \delta\,(1 - \pi_{t-1}), \qquad \pi_t = \frac{\rho^2}{2\,(\rho - \delta k_{t-1})}, \qquad w_t = \frac{\pi_t}{\rho}, \qquad k_t = \pi_t\,(1 - w_t) + \delta\,k_{t-1}\,w_t^2, \qquad \pi_1 = \tfrac12,\; k_1 = \tfrac14 .$$

Der Grenztyp ist zwischen jetzt und der nächsten Runde indifferent. Aus Messungen (keine Herleitung): bei unendlichem Horizont $\pi_\infty = \frac{s}{1+s}$ mit $s = \sqrt{1-\delta}$;
bei festem Zeithorizont $H$ und Rundenlänge gegen null $\tfrac12 e^{-rH}$ (gemessen für $rH \le 2$).

**Literatur** (Titel und Fundstellen laut Einzelplan, dort nur nach Abstract oder Suchauszug; in diesem Bau nicht nachgelesen, nicht im Volltext geprüft): Chatterjee/Samuelson, Operations Research 31(5), 1983; Myerson/Satterthwaite, Journal of Economic Theory 29, 1983;
Gul/Sonnenschein/Wilson, Journal of Economic Theory 39(1), 1986; Ausubel/Deneckere, Econometrica 60(3), 1992; Cramton, Review of Economic Studies 59(1), 1992; Leininger/Linhart/Radner, Journal of Economic Theory 48(1), 1989.
"""

NOT_IMPLEMENTED_MARKDOWN = """
- **Der Fall mit Abstand zwischen Kosten und niedrigstem Wert** (die Kosten des Spediteurs liegen unter dem niedrigsten Wert des Verladers): nicht gerechnet. Die Gitter-Löser, mit denen er geprüft werden sollte, versagten ab etwa fünf Runden; ein besser gestellter Löser fehlt.
- **Das Gleichgewicht außerhalb des Gültigkeitsbereichs:** die App meldet „Formel gilt hier nicht“ und zeigt keine Zahl; ein anderes Gleichgewicht wird nicht hergeleitet.
- **Diskrete Gleichgewichte** (Beste-Antwort-Dynamik auf Typengittern): nicht berechnet.
- **Mehrere Käufer und Verkäufer, zweiseitige private Information mit strategischer Verzögerung, abwechselnde Angebote mit privater Information, lernende Verhandler:** nicht gerechnet.
"""
