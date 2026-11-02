# Verhandeln mit privaten Werten: Was kostet das Geheimnis? – Streamlit-Demo

<!-- TODO nach dem Deploy: direkt hierher den Live-Link setzen (Leerzeile davor und danach):
**[→ Demo live ausprobieren](https://sebastianhanisch-geheimnis-verhandlung-demo.streamlit.app/)** -->

Stück B2 der Linie **regeln-verhandeln** (Arbeitsname; Name, Bereich und Themenfeld werden erst bei der Einbindung in die Website festgelegt) in der „Konzepte“-Reihe für die Website „Sebastian Hanisch – Operations Research und Machine Learning“. Der rote Faden der Linie: wer sich zuerst festlegt, lenkt. Hier ist die Information das Thema: ein **Verlader** (Käufer, privater Wert *v* der Tour) und ein **Spediteur** (Verkäufer, private Kosten *c*) kennen jeder nur das Eigene. Die Demo rechnet zwei Wege, wie das Geheimnis kostet: in der **doppelten Auktion** (beide nennen gleichzeitig Gebot und Forderung, Chatterjee–Samuelson) bleibt Handel aus, bei **einseitiger Information und Angeboten Runde für Runde** (Coase) kommt er später. Beträge sind Euro je Tour; Eigennutz, Gleichverteilung, Unabhängigkeit der Werte, Diskont und die Kenntnis der Verteilungen sind **Modellannahmen**, keine Aussagen über echte Betriebe.

Abgrenzung: [`verhandlung-demo`](https://github.com/sebastian-hanisch/verhandlung-demo) rechnet Verhandlung bei **vollständiger** Information (abwechselnde Angebote, Nash-Lösung) und nennt private Information dort als nicht gebaut; hier ist sie der Gegenstand. `myerson-satterthwaite-demo` rechnet Mechanismen auf einem Typengitter (das Zweitbeste als lineares Programm); der Mittelpunkt-Preis ist dort nur die Beste Antwort gegen einen ehrlichen Verkäufer, und das Gleichgewicht der doppelten Auktion steht dort unter „Bewusst nicht umgesetzt“: hier ist es in geschlossener Form gerechnet, mit seinem Gültigkeitsbereich. `einzelgut-auktion-demo` setzt die Selbstbindung des Verkäufers voraus; hier wird gemessen, was sie wert ist und was ohne sie geschieht. `vertragsdesign-demo` hat private Information über das **Handeln**, nicht über Werte. `vorabsignale-demo` rechnet Absprachen ohne private Information und ohne teure Signale.

## Kernfrage

*Was ändert sich beim Verhandeln, wenn Wert und Kosten privat sind: bleibt der Handel aus, oder kommt er später?* Die Antwort hat vier Teile. (1) **Bei gleichzeitigen Geboten bleibt Handel aus:** sind Werte und Kosten gleichverteilt auf 0 bis 60 Euro je Tour und der Preis liegt in der Mitte, liegt der Gewinn im Gleichgewicht bei 8,44 Euro statt 10,00 Euro im Erstbesten (84,4 %); 7/16 (43,8 %) der Touren, die sich lohnen würden, kommen nicht zustande. Das ist im Gültigkeitsbereich bei κ = ½ das Zweitbeste (Myerson–Satterthwaite), auch bei ungleichen Bereichen. (2) **Die Formel hat einen Gültigkeitsbereich:** das lineare Profil ist nur dort ein Gleichgewicht, wo die niedrigste Forderung nicht unter dem niedrigsten Gebot und die höchste nicht unter dem höchsten liegt; bei κ = ½ heißt das *v*₀ − *c*₀ ≤ *L*/4 und *v*₁ − *c*₁ ≤ *L*/4. Außerhalb meldet die App „Formel gilt hier nicht“. (3) **Das Gleichgewicht ist nicht das einzige:** ein Einpreis bei 30 Euro ist auch eines, mit 7,50 Euro (88,9 % des Zweitbesten), ein Einpreis bei 6 Euro mit 2,70 Euro (32,0 %); welches gespielt wird, sagt die Rechnung nicht. (4) **Bei einseitiger Information kommt der Handel später:** bietet der Spediteur 200 Runden lang und diskontieren beide mit δ = 0,9, nennt er in Runde 1 14,42 Euro statt 30,00 Euro mit Selbstbindung; sein Gewinn sinkt auf 48,1 % des Gewinns mit Selbstbindung, aber der **Gesamtwert steigt** (26,40 statt 22,50 Euro), und der Verlader gewinnt (19,19 statt 7,50 Euro). Im Modell (gleichverteilter Wert, Kosten 0, nur der Verlader privat) verliert gegenüber der Selbstbindung nur der Spediteur. Der erste Preis folgt bei langem Horizont einer Grenzform (Messhypothese) und fällt bei festem Zeithorizont (gemessen bis *rH* = 2) nicht auf null, sondern gegen ½·e^(−*rH*).

## Befunde und Korrekturen gegenüber dem Plan

Der Einzelplan (Vormessung vom 2026-11-01, Wegwerfskripte) wurde nicht blind übernommen; jede Zahl ist im Bau neu gemessen. Die Zahlen des Plans bestätigten sich, soweit sie nicht von Zufallsströmen abhängen (Plan: Gleichgewicht = Zweitbestes in 64 von 64 gültigen und Kriterium in 192 von 192 Zufallsinstanzen; hier 59 und 189 mit anderen Zufallsströmen, siehe H3 und H4). Abweichungen und neue Funde:

- **Das Gültigkeitskriterium ist hergeleitet, nicht nur gemessen, und gilt für jedes κ.** Der Plan hatte es für κ = ½ als Messung. Die Auszahlung des Verkäufers ist zwischen niedrigstem und höchstem Gebot konkav, davor wächst sie, danach ist sie null; daraus folgen die zwei Bedingungen (niedrigste Forderung ≥ niedrigstes Gebot, höchste Forderung ≥ höchstes Gebot) für jedes κ. Das Kriterium stimmt in 189 von 189 Zufallsinstanzen bei κ = ½ und in 189 von 189 bei zufälligem κ mit der Gitterlücke überein (H4).
- **Randfund bei κ = 0 und κ = 1 (bei der Prüfung der Voreinstellung „Verkäufer setzt den Preis“ gefunden):** bei κ = 0 hängt der Preis nicht vom Gebot ab, bei κ = 1 nicht von der Forderung. Dort entfällt je eine der beiden Bedingungen (bei κ = 0 die obere, bei κ = 1 die untere). Das erste Kriterium meldete „ungültig“, wo das Gitter keine Lücke fand; die Beispielrechnung in `tests/test_units.py` und der Zufallstest mit κ ∈ {0, 1} (H4) halten die Korrektur.
- **Geschlossene Handelsmenge:** im Gültigkeitsbereich ist die Handelsmenge bei κ = ½ ein Dreieck mit Katheten 3*L*/4; Wahrscheinlichkeit 9*L*²/(32 *W*ᵥ*W*꜀) und Gewinn 9*L*³/(64 *W*ᵥ*W*꜀) (Breiten *W*ᵥ und *W*꜀). Daraus folgt, dass das Gleichgewicht das Zweitbeste trifft (H3). Der Plan rechnete die Wohlfahrt über 400 001 Stützstellen; hier steht die geschlossene Form, die Stützstellen sind das Orakel.
- **Erwartung „Asymmetrie senkt den Anteil am Zweitbesten“ widerlegt (H3):** im Gültigkeitsbereich ist er bei κ = ½ immer 100 %; nur der Anteil am Erstbesten schwankt (Tabelle zu Reiter 1).
- **Neu gegen die Erwartung: der erste Preis ist bei festem *T* in δ nicht monoton (H13).** Der Plan nannte „Preis der ersten Runde in δ nicht steigend (nur wo belegt)“; belegt ist es nur bei langem Horizont. Bei *T* = 2 bis 30 steigt er für große δ wieder (Minimum bei δ = 0,67 / 0,73 / 0,80 / 0,87 / 0,94 für *T* = 2 / 3 / 5 / 10 / 30, auf dem Raster 0,00 bis 0,99).
- **Neu gemessen (nicht im Plan): drei Folgerungen aus der Grenzform (H9).** Der Gewinn im Grenzfall ist die Hälfte des ersten Preises, der Anteil der Käufer in Runde 1 gleich dem ersten Preis, die mittlere Wartezeit der Käufer 1/√(1 − δ) Runden. Alle drei Messhypothesen ohne Beweis.
- **Gitter-Löser:** das Versagen ab sechs bis neun Runden (Plan: ab etwa fünf) ist als Test festgehalten (`test_grid_maximum_solver_is_fine_for_three_rounds_and_fails_later`); die Ursache ist weiter offen (Verdacht: das Maximum über die nächste Grenze ist flach). Das unabhängige Lösen gelingt nur bis *T* = 3; bis *T* = 200 steht der Abweichungsprüfer, ein Gleichgewichts-Nachweis.
- **Vier Reiter, anders geschnitten als im Plan:** die doppelte Auktion steht als Hauptansicht über den Reitern (Gewinn, Diagramme, Gitterprobe); Reiter 1 enthält die Experimente zur Gültigkeit (E1) und zur Preisregel (E2).
- **Schalter „Selbstbindung“ statt zweier Regler:** er wählt, welchen Pfad die Diagramme zeigen; die Tabelle zeigt beide. Der Regler *T* geht bis 3 000 (der Plan sagte 2 000 und im Preset 3 000).
- **Nicht aufgenommen:** der Lückenfall (Kosten unter dem niedrigsten Wert) und das Gleichgewicht außerhalb des Gültigkeitsbereichs (siehe „Bewusst nicht umgesetzt“); die Vormessung zu diskreten Gleichgewichten (Beste-Antwort-Dynamik, Plan V3b) wurde im Bau **nicht wiederholt**.
- **Port 9226** (laut `.claude/launch.json` frei, TCP-Prüfung ohne Hörer).

## Modell

**Doppelte Auktion.** Eine Tour, ein Verlader (Wert *v* ~ U[*v*₀, *v*₁]), ein Spediteur (Kosten *c* ~ U[*c*₀, *c*₁]), unabhängig. Der Verlader nennt ein Gebot *b*, der Spediteur eine Forderung *a*; ist *b* ≥ *a*, wird gehandelt (Gleichstand: Handel) zum Preis (1 − κ)·*a* + κ·*b*. Die Bedingungen erster Ordnung geben ein Gleichgewicht mit geraden Linien: β_s = 1/(2 − κ), β_b = 1/(1 + κ), bei κ = ½ *b*(*v*) = 2*v*/3 + (*v*₁ + 3*c*₀)/12 und *a*(*c*) = 2*c*/3 + (3*v*₁ + *c*₀)/12; gehandelt wird genau bei *v* − *c* ≥ *L*/4 mit *L* = *v*₁ − *c*₀. **Erstbestes:** Handel bei *v* ≥ *c*. **Zweitbestes** (Myerson–Satterthwaite, Gleichverteilung): Handel bei *v* − *c* ≥ θ*L*, wobei θ = 0, falls *G*(0) ≥ 0, sonst die Wurzel in [0, ½) von *G*(θ) = E[(2(*v* − *c*) − *L*)·1{*v* − *c* ≥ θ*L*}]. **Einpreis:** Verlader mit *v* ≥ *p* bieten *p*, Spediteure mit *c* ≤ *p* fordern *p*.

**Warten statt Handeln.** Kosten des Spediteurs 0 (nur der Aufschlag zählt), Wert *v* ~ U[0, *V*], *T* Runden, Diskontfaktor δ je Runde; der Spediteur bietet in jeder Runde einen Preis, der Verlader kauft oder wartet, der Spediteur kann sich nicht binden. Bei *t* verbleibenden Runden und Träger [0, *x*] ist der Preis π_t·*x*, die Kaufgrenze *w*_t·*x* und der Gewinn *k*_t·*x*² (Dichte 1): ρ = 1 − δ(1 − π_{t−1}), π_t = ρ²/(2(ρ − δ*k*_{t−1})), *w*_t = π_t/ρ, *k*_t = π_t(1 − *w*_t) + δ*k*_{t−1}*w*_t², π₁ = ½, *k*₁ = ¼. Der Grenztyp ist zwischen jetzt und der nächsten Runde indifferent. **Selbstbindung:** ein einziges Angebot zum Preis *V*/2 (Gewinn ¼, Überschuss ⅛, Gesamtwert ⅜ in Einheiten von *V*). Zeit in Reiter 4 in Einheiten von 1/*r*: δ = e^(−*r*·Δ), *T* = *H*/Δ.

## Methodik

- **Geschlossene Formeln:** Koeffizienten, Gültigkeit, Handelswahrscheinlichkeit und Gewinn (drei Streifen, Polynomintegrale), Zweitbestes (Bisektion auf *G*), Einpreis; alles läuft mit Gleitkomma wie mit Brüchen (die Mini-Instanzen der Tests rechnen exakt). Die Coase-Rekursion ist O(*T*).
- **Gitterprobe live:** die Auszahlung jeder Formelstrategie gegen die der Gegenseite, geprüft gegen ein Gitter von 2 001 Geboten für 21 Typen je Seite (mit den Eckpunkten der Beste-Antwort-Struktur im Gitter); in den Tests ohne Eckpunkte und feiner.
- **Vorgerechnete Reihen:** `tools/make_grid.py` rechnet Zufallsinstanzen (SplitMix64, vier Zufalls-Seeds, 50 je Seed und Modus) und den Abweichungsprüfer; Erzeuger-Hash in `data/tables.json`.
- **Orakel:** siehe „Tests“. Das Zweitbeste wird gegen ein lineares Programm geprüft (scipy nur in den Tests), das Gleichgewicht gegen numerische Integration und ein Gitter in Brüchen, die Coase-Rekursion gegen Brüche, 100-stellige Dezimalrechnung, verschachtelte Optimierung (*T* ≤ 3), den Abweichungsprüfer und die Pfadsumme.

## Befunde (gemessen, keine Behauptungen)

Skala der Zahlen im Text: Werte und Kosten gleichverteilt auf 0 bis 1, Gewinne in Einheiten dieser Skala; die App rechnet mit 0 bis 60 Euro je Tour (Gewinne skalieren linear, Wahrscheinlichkeiten nicht). „Plan“ steht für die Vormessung vom 2026-11-01.

| Nr. | Aussage | Stand | Nachweis |
|---|---|---|---|
| H1 | Die Linien *b*(*v*) = 2*v*/3 + 1/12 und *a*(*c*) = 2*c*/3 + 1/4 sind Beste Antworten; Gewinn 9/64, Handelswahrscheinlichkeit 9/32 | **Ja** (Brüche: Lücke exakt 0 auf dem Gitter 1/120; numerische Integration; Gitter 4 001; ehrliche Forderung 3/32 statt 1/8) | `test_claims.py::test_h1`, `test_oracle_auction.py` |
| H2 | Das Gleichgewicht trifft das Zweitbeste (Schwelle ¼, Gewinn 9/64) | **Ja** (*G*(¼) = 0 in Brüchen; lineares Programm mit Richardson aus 24 und 32 Typen: 0,14106 gegen 9/64 = 0,140625; aus 32 und 40: 0,14089) | `test_claims.py::test_h2`, `test_oracle_auction.py` |
| H3 | Für allgemeine Gleichverteilungen: Handel genau bei *v* − *c* ≥ *L*/4, Zweitbestes mit derselben Schwelle, solange das Profil ein Gleichgewicht ist; Erwartung „Asymmetrie senkt den Anteil am Zweitbesten“ | **Ja** für die Gleichheit (59 von 59 gültigen Zufallsinstanzen, größte relative Abweichung 5,3·10⁻¹³; hergeleitet über das Dreieck); **Nein** für die Erwartung (Anteil am Zweitbesten in allen 59 gültigen Instanzen 100 %) | `test_claims.py::test_h3` |
| H4 | Gültigkeit genau bei (i) niedrigste Forderung ≥ niedrigstes Gebot und (ii) höchste Forderung ≥ höchstes Gebot; bei κ = 0 entfällt (ii), bei κ = 1 (i) | **Ja** (vorgerechnet: 189 von 189 bei κ = ½, 189 von 189 bei zufälligem κ; in den Tests am reinen Gitter mit 4 001 Geboten ohne Abweichung an 52, 57 und 53 Zufallsinstanzen bei κ = ½, zufälligem κ und κ ∈ {0, 1}; hergeleitet) | `test_claims.py::test_h4`, `test_oracle_auction.py::test_validity_criterion_agrees_with_the_grid_gap` |
| H5 | Preisregel (Werte und Kosten gleichverteilt auf demselben Bereich): κ = ½ maximiert den Gewinn, die Kurve ist in κ ↔ 1 − κ symmetrisch; κ = 0 (der Verkäufer setzt den Preis) gibt 1/8 | **Ja** (21 Preisregeln in Schritten von 0,05 bei Werten und Kosten 0 bis 1, 10 Paare symmetrisch) | `test_claims.py::test_h5` |
| H6 | Einpreis-Gleichgewichte mit Gewinn *p*(1 − *p*)/2 | **Ja** (5 Preise, Lücke am Gitter höchstens 10⁻¹²; ein falscher Preis der Spediteure: Lücke 0,25) | `test_claims.py::test_h6` |
| H7 | Beste-Antwort-Dynamik auf diskreten Typengittern liefert einen Zielwert | **Nein** (Plan V3b, im Bau nicht wiederholt) | – |
| H8 | Die Coase-Rekursion ist das Gleichgewicht für alle *T* | **Ja** als Gleichgewichts-Nachweis bis *T* = 200 (Abweichungsprüfer); unabhängig gelöst nur bis *T* = 3; der Gitter-Löser (801 Punkte, kein Skalierungsansatz) weicht erstmals bei *T* = 6 (δ = 0,5 und 0,9) bzw. *T* = 9 (δ = 0,99) um mehr als 0,01 ab, bis *T* = 30 um bis zu 0,081 / 0,221 / 0,055 (Ursache offen) | `test_claims.py::test_h8`, `test_oracle_coase.py` |
| H9 | Grenzform des ersten Preises bei unendlichem Horizont: s/(1 + s), s = √(1 − δ); dazu Gewinn = Preis/2, Käufer in Runde 1 = Preis, Wartezeit 1/s | **Ja** als Messung (9 Diskontfaktoren; in Brüchen exakt an 6 Punkten); **Beweis offen** | `test_claims.py::test_h9` |
| H10 | Fester Zeithorizont *H*, Runde gegen 0: erster Preis gegen ½·e^(−*rH*) | **Ja** für *rH* ≤ 2 (Richardson in der Rundenlänge; Abweichung höchstens 2·10⁻⁵, 7,3·10⁻⁷ bei *rH* = 1); **Nein, noch nicht erreicht** bei *rH* = 3 und 4 (Abweichung 1,4·10⁻⁴ bei *rH* = 3, 1,1·10⁻³ bei *rH* = 4); Beweis offen | `test_claims.py::test_h10`, `test_oracle_coase.py` |
| H11 | Ohne Selbstbindung ist der Gesamtwert höher | **Ja** (8 von 8 Diskontfaktoren); der Spediteur verliert | `test_claims.py::test_h11` |
| H12 | Lückenfall: der Preis fällt nicht auf die Kosten | **Offen** (nicht gemessen, Plan V7) | – |
| H13 | Der erste Preis fällt mit δ (bei festem *T*) | **Nein** bei kurzem Horizont (*T* = 2 bis 30 steigt er für große δ wieder); **Ja** bei *T* = 200 und 3 000 | `test_claims.py::test_h13`, `test_eigenschaften_geheimnis.py` |

### Reiter 1: Gültigkeit und Preisregel (E1, E2)

Der Wertebereich verschoben gegen den Kostenbereich 0 bis 60 Euro (Breiten 60 Euro, κ = ½). Der Grenzfall liegt bei der Verschiebung 20 Euro (ein Drittel der Breite); dahinter hört das lineare Profil auf, ein Gleichgewicht zu sein (Spalte „Lücke am Gitter“):

| Verschiebung (Euro) | untere Wertgrenze | kleinster Abstand Forderung − Gebot | Formel gilt | Lücke am Gitter | Gewinn Gleichgewicht | Anteil am Erstbesten | Anteil am Zweitbesten |
|---|---|---|---|---|---|---|---|
| 0,00 | 0,00 | 10,00 | ja | 0,0000 | 8,44 | 84,4 % | 100,0 % |
| 6,00 | 6,00 | 7,00 | ja | 0,0000 | 11,23 | 84,5 % | 100,0 % |
| 12,00 | 12,00 | 4,00 | ja | 0,0000 | 14,58 | 85,2 % | 100,0 % |
| 18,00 | 18,00 | 1,00 | ja | 0,0000 | 18,54 | 86,5 % | 100,0 % |
| 20,00 | 20,00 | 0,00 | ja | 0,0000 | 20,00 | 87,1 % | 100,0 % |
| 24,00 | 24,00 | −2,00 | nein | 1,0000 | – | – | – |
| 36,00 | 36,00 | −8,00 | nein | 4,0000 | – | – | – |
| 48,00 | 48,00 | −14,00 | nein | 7,0000 | – | – | – |
| 60,00 | 60,00 | −20,00 | nein | 10,0000 | – | – | – |

Zufallsinstanzen (vorgerechnet, vier Zufalls-Seeds; Kriterium gegen die numerische Lücke; bei κ = ½ 59 gültig / 130 ungültig, bei zufälligem κ 70 gültig / 119 ungültig):

| Preisregel | Instanzen | beide gültig | beide ungültig | nur Kriterium gültig | nur Gitter gültig | größte relative Abweichung Gleichgewicht / Zweitbestes |
|---|---|---|---|---|---|---|
| κ = ½ | 189 | 59 | 130 | 0 | 0 | 5.3e-13 |
| zufälliges κ (0,1 bis 0,9) | 189 | 70 | 119 | 0 | 0 | – |

Preisregel bei Werten und Kosten 0 bis 60 Euro (Auszug):

| κ | Formel gilt | Gewinn (Euro je Tour) | Anteil am Erstbesten |
|---|---|---|---|
| 0,00 | ja | 7,50 | 75,0 % |
| 0,10 | ja | 7,84 | 78,4 % |
| 0,25 | ja | 8,20 | 82,0 % |
| 0,40 | ja | 8,40 | 84,0 % |
| 0,50 | ja | 8,44 | 84,4 % |
| 0,60 | ja | 8,40 | 84,0 % |
| 0,75 | ja | 8,20 | 82,0 % |
| 0,90 | ja | 7,84 | 78,4 % |
| 1,00 | ja | 7,50 | 75,0 % |

### Reiter 2: Einpreis-Gleichgewichte (E3)

Fünf Einpreise bei Werten und Kosten 0 bis 60 Euro (10, 30, 50, 70 und 90 Prozent der Spanne); Zweitbestes 8,44 Euro:

| Einpreis p | Handelswahrscheinlichkeit | Gewinn | Anteil am Zweitbesten | Lücke am Gitter |
|---|---|---|---|---|
| 6,00 | 9,0 % | 2,70 | 32,0 % | 0,000000 |
| 18,00 | 21,0 % | 6,30 | 74,7 % | 0,000000 |
| 30,00 | 25,0 % | 7,50 | 88,9 % | 0,000000 |
| 42,00 | 21,0 % | 6,30 | 74,7 % | 0,000000 |
| 54,00 | 9,0 % | 2,70 | 32,0 % | 0,000000 |

### Reiter 3: Warten statt Handeln (E4)

Ohne und mit Selbstbindung (Euro je Tour, *V* = 60 Euro; δ = 0,5 und 0,9 mit 200 Runden, δ = 0,99 mit 3 000):

| δ | Pfad | erster Preis | Gewinn Spediteur | Überschuss Verlader | Gesamtwert | nie gekauft | mittlere Wartezeit der Käufer (Runden) |
|---|---|---|---|---|---|---|---|
| 0,50 | ohne Selbstbindung | 24,85 | 12,43 | 11,36 | 23,79 | 0,0 % | 1,41 |
| 0,50 | mit Selbstbindung | 30,00 | 15,00 | 7,50 | 22,50 | 50,0 % | 0,00 |
| 0,90 | ohne Selbstbindung | 14,42 | 7,21 | 19,19 | 26,40 | 0,0 % | 3,16 |
| 0,90 | mit Selbstbindung | 30,00 | 15,00 | 7,50 | 22,50 | 50,0 % | 0,00 |
| 0,99 | ohne Selbstbindung | 5,45 | 2,73 | 25,91 | 28,64 | 0,0 % | 10,00 |
| 0,99 | mit Selbstbindung | 30,00 | 15,00 | 7,50 | 22,50 | 50,0 % | 0,00 |

Das Erstbeste wäre 30,00 Euro. Der Gewinn des Spediteurs ohne Selbstbindung liegt bei 82,8 % (δ = 0,5), 48,1 % (δ = 0,9) und 18,2 % (δ = 0,99) des Gewinns mit Selbstbindung; der Gesamtwert ist ohne Selbstbindung bei δ = 0,5; 0,6; 0,7; 0,8; 0,85; 0,9; 0,95 und 0,99 höher (8 von 8), der Überschuss des Verladers ebenfalls.

### Reiter 4: Rundenlänge und Horizont (E5)

Erster Preis bei festem Horizont *H* = 1 (Zeit in Einheiten von 1/*r*) über der Rundenlänge:

| Rundenlänge Δ | Runden | Horizont | δ | erster Preis (% von V) | Grenzwert unendlicher Horizont (%) | ½·e^(−H) (%) |
|---|---|---|---|---|---|---|
| 1,0000 | 1 | 1,00 | 0,3679 | 50,0 | 44,3 | 18,4 |
| 0,5000 | 2 | 1,00 | 0,6065 | 44,5 | 38,5 | 18,4 |
| 0,2500 | 4 | 1,00 | 0,7788 | 38,4 | 32,0 | 18,4 |
| 0,1000 | 10 | 1,00 | 0,9048 | 30,9 | 23,6 | 18,4 |
| 0,0500 | 20 | 1,00 | 0,9512 | 26,5 | 18,1 | 18,4 |
| 0,0200 | 50 | 1,00 | 0,9802 | 22,4 | 12,3 | 18,4 |
| 0,0100 | 100 | 1,00 | 0,9900 | 20,6 | 9,1 | 18,4 |
| 0,0050 | 200 | 1,00 | 0,9950 | 19,6 | 6,6 | 18,4 |
| 0,0020 | 500 | 1,00 | 0,9980 | 18,9 | 4,3 | 18,4 |
| 0,0010 | 1000 | 1,00 | 0,9990 | 18,6 | 3,1 | 18,4 |
| 0,0005 | 2000 | 1,00 | 0,9995 | 18,5 | 2,2 | 18,4 |

Wie lang muss der Horizont sein? Kleinste Rundenzahl, bei der der erste Preis höchstens 1 % vom Grenzwert bei unendlichem Horizont abweicht (das 2,5- bis 4,1-fache von 1/(1 − δ)):

| δ | Grenzwert s/(1+s) (% von V) | kleinstes T | T·(1 − δ) |
|---|---|---|---|
| 0,500 | 41,4 | 5 | 2,50 |
| 0,700 | 35,4 | 9 | 2,70 |
| 0,900 | 24,0 | 31 | 3,10 |
| 0,950 | 18,3 | 66 | 3,30 |
| 0,990 | 9,1 | 384 | 3,84 |
| 0,995 | 6,6 | 823 | 4,12 |

Abweichungsprüfer (vorgerechnet; kein Spediteur gewinnt durch Abweichen, die Käufer-Antwort durch Aufzählung aller späteren Kaufrunden):

| δ | Runden bis | größte Gewinnsteigerung durch Abweichen | Skimming verletzt in |
|---|---|---|---|
| 0,50 | 200 | -9.0e-13 | 0 von 200 |
| 0,90 | 200 | -4.1e-14 | 0 von 200 |
| 0,99 | 200 | -8.3e-17 | 0 von 200 |

## Ehrliche Grenzen

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

**Bekannte Probleme und Unsicherheiten**
- Beide Grenzformeln des Warte-Modells (unendlicher Horizont, fester Horizont) sind **Messhypothesen ohne Beweis**; die Gleichung des Grenzfalls ist in sechs Punkten exakt in Brüchen erfüllt, das ist kein Beweis für alle δ. Die Formel für den festen Horizont ist nur für *rH* ≤ 2 gemessen.
- Das unabhängige Lösen der Coase-Rekursion (ohne die Rekursionsformel) gelingt nur bis *T* = 3; bis *T* = 200 gibt es den Abweichungsprüfer, der Gleichgewicht nachweist, aber nicht neu löst.
- Die Gültigkeitsbedingung ist hergeleitet (Skizze im 📐-Expander) und an Zufallsinstanzen und Randfällen gemessen, aber nicht als Beweis ausgeschrieben.
- Das Zweitbeste stützt sich auf die Beschreibung in der README der `myerson-satterthwaite-demo` (die Originalarbeit ist nicht eingesehen) und auf ein lineares Programm mit Richardson-Extrapolation (Abweichung 4,3·10⁻⁴ bei 24 und 32 Typen), nicht auf den Volltext.
- Die Oberfläche ist im Browser nur stichprobenartig geprüft (Rechner und Telefonbreite), nicht auf allen Geräten; die Linux-CI (Python 3.12) ist noch nicht gelaufen.

## Literatur

Titel und Fundstellen stehen so im Einzelplan (Vormessung vom 2026-11-01), dort **nur nach Titel, Abstract oder Suchauszug**; in diesem Bau wurde keine Quelle nachgelesen, **nichts ist im Volltext geprüft**. Kein Test stützt sich auf sie (außer den Werten 1/6, 9/64 und 1/8 aus der README der `myerson-satterthwaite-demo`); offen sind Satznummern, Voraussetzungen und Seiten.

- Chatterjee/Samuelson, „Bargaining under Incomplete Information“, Operations Research 31(5), 835–851, 1983 (doppelte Auktion; lineares Gleichgewicht). Das Gültigkeitskriterium dieser Demo ist eigene Herleitung und Messung, nicht dieser Quelle entnommen.
- Myerson/Satterthwaite, „Efficient mechanisms for bilateral trading“, Journal of Economic Theory 29, 1983 (Zweitbestes). Die Werte 1/6 und 9/64 stammen aus der README der `myerson-satterthwaite-demo`.
- Gul/Sonnenschein/Wilson, Journal of Economic Theory 39(1), 155–190, 1986 (laut Auszug: der Verkäufer bietet in jeder Periode, die Preise gehen mit kürzerer Periode gegen null oder den niedrigsten Wert). Die Grenzformeln dieser Demo stammen aus Messungen, nicht aus dieser Quelle.
- Ausubel/Deneckere, Econometrica 60(3), 597–625, 1992 (laut Abstract: „Silence Theorem“, kein Gap); stützt das Modell „nur der Spediteur bietet“ bei kurzen Runden, nicht geprüft.
- Cramton, Review of Economic Studies 59(1), 205–225, 1992 (zweiseitige Information, strategische Verzögerung); nicht gerechnet.
- Leininger/Linhart/Radner, Journal of Economic Theory 48(1), 63–106, 1989 (laut Arbeitspapier-Abstract: für die Gleichverteilung eine sehr große Menge von Gleichgewichten, von zweitbest bis wertlos).
- Fudenberg/Levine/Tirole 1985, Stokey 1981, Bulow 1982: aus dem Gedächtnis, nicht geprüft; nicht verwendet.

## Tests

**242 Tests**, Laufzeit rund 200 Sekunden seriell (am 2026-11-02 gemessen) auf Windows mit Python 3.14 (die AppTest-Dateien brauchen den größten Teil). Linux-CI (Python 3.12) ist noch nicht gelaufen. Zusammensetzung:

- **Orakel (`tests/test_oracle_auction.py`, `tests/test_oracle_coase.py`):** die Beste Antwort durch numerische Integration über die Gegenseite und durch ein Gitter in Brüchen; Wahrscheinlichkeit und Gewinn durch Integration über *v* mit exakter innerer Integration; das Zweitbeste gegen ein lineares Programm (scipy, Richardson aus zwei Feinheiten); das Gültigkeitskriterium gegen die Gitterlücke an Zufallsinstanzen (κ = ½, zufälliges κ, κ ∈ {0, 1}); Einpreis gegen ein Gitter mit Negativkontrolle; die Coase-Rekursion gegen Brüche (*T* ≤ 8), 100-stellige Dezimalrechnung (*T* ≤ 200), verschachtelte Optimierung ohne Skalierungsansatz (*T* ≤ 3), den Abweichungsprüfer (*T* ≤ 60 im Repo, 200 in den Reihen), die Pfadsumme gegen Kauf je Typ, die Fixpunktgleichung (brentq) und Richardson für den festen Horizont; der dokumentierte Negativbefund des Gitter-Lösers.
- **Einheiten an von Hand gerechneten Mini-Instanzen (`test_units.py`):** drei Auktions-Instanzen (Klassiker, Grenzfall, ungültig) und der Verkäufer-Preis in `tests/conftest.py` mit Rechnung im Docstring, alle in Brüchen; die Coase-Rekursion bei δ = ½ für *T* ≤ 3 und der Pfad für *T* = 2.
- **Eigenschaftstests (`test_eigenschaften_geheimnis.py`):** Verschiebung und Skalierung aller Beträge, Rollentausch (*v*, *c*) → (−*c*, −*v*) mit κ → 1 − κ, Rangfolge Erstbestes ≥ Zweitbestes ≥ jedes Gleichgewicht, Gleichheit mit dem Zweitbesten genau bei κ = ½, Einpreis-Symmetrie, Monotonie der Coase-Größen in *T* und (nur bei langem Horizont) in δ.
- **Randfälle und Zweige (`test_edge_cases.py`):** kein Handelsgewinn, kleinste Breiten, Werte über den Kosten, κ an den Rändern, Grenzfall der Gültigkeit, Einpreis ohne Handel, δ = 0 und 0,99, *T* = 1 und 3 000, eine Rundenlänge über dem Horizont.
- **Verdikte und Presets (`test_verdicts.py`, `test_presets.py`):** Schwellen und jede Zahl im Text an Handinstanzen; je Preset die angekündigte Wirkung (das Preset „Ungültig“ meldet keine Zahl, „Sehr geduldig“ nennt die Horizontbedingung).
- **Literatur (`test_literatur_geheimnis.py`):** 1/6, 9/64, 1/8 aus der README der `myerson-satterthwaite-demo`; die Originalarbeiten sind nicht eingesehen, deshalb dort kein Test.
- **Messreihen (`test_measurements.py`):** Erzeuger-Hash, Summen in sich stimmig, Blöcke neu gerechnet.
- **Claims (`test_claims.py`):** jede Zahl der README; die Tabellen werden mit denselben Zeilenbauern der App erzeugt und als Text in der README gesucht; Hypothesenzeilen H1 bis H13.
- **App (`test_app.py`, `test_layout.py`, `test_footer.py`, `test_runtime_imports.py`, `test_copies.py`):** jeder Knopf, jeder Regler an beiden Rändern, alle Minima und alle Maxima zusammen, jede Rundenlänge, der Schalter, PDF, Hervorhebung des aktiven Presets, Footer, Laufzeit-Importe, Kopietest des Zufallsgenerators.

Ein Mutationstest läuft für diese Demo nicht (Entscheidung des Betreibers, 2026-10-28). Das Laufzeit-Maximum liegt bei den AppTest-Dateien; unter Last (parallele Läufe) kann ein AppTest länger als 180 Sekunden brauchen (Umgebungsvariable `APPTEST_TIMEOUT`).

## Dateistruktur

| Datei | Inhalt |
|---|---|
| `app.py` | Streamlit-Oberfläche: Hauptansicht, vier Reiter, Verdikte, PDF |
| `gvh_double_auction.py` | Doppelte Auktion: Koeffizienten, Gültigkeit, Handelsmenge und Gewinn in geschlossener Form, Zweitbestes, Einpreis, Gitterprobe |
| `gvh_coase.py` | Coase-Rekursion, Pfad, Selbstbindung, Grenzformen |
| `gvh_evaluation.py` | Kennzahlen je Reiter, Tabellen, alle Verdikte als reine Funktionen |
| `gvh_experiments.py` | Zufallsinstanzen, Abweichungsprüfer, vorgerechnete Reihen mit Erzeuger-Hash |
| `gvh_visualization.py`, `gvh_pdf_export.py`, `gvh_layout.py` | Diagramme, PDF (fpdf2), fester Kopf |
| `gvh_presets.py`, `gvh_constants.py`, `gvh_scenario.py`, `gvh_texts.py` | Regler, Presets, Einstellungen, feste Texte |
| `gvh_rng.py` | SplitMix64, wörtliche Kopie von `ab-test-demo/abt_rng.py` |
| `tools/make_grid.py`, `data/tables.json` | Messreihen neu rechnen; gespeicherte Reihen |
| `tests/` | siehe „Tests“ |

## Bewusst nicht umgesetzt

- **Der Fall mit Abstand zwischen Kosten und niedrigstem Wert** (die Kosten des Spediteurs liegen unter dem niedrigsten Wert des Verladers): nicht gerechnet. Die Gitter-Löser, mit denen er geprüft werden sollte, versagten ab sechs bis neun Runden; ein besser gestellter Löser fehlt.
- **Das Gleichgewicht außerhalb des Gültigkeitsbereichs:** die App meldet „Formel gilt hier nicht“ und zeigt keine Zahl; ein anderes Gleichgewicht wird nicht hergeleitet.
- **Diskrete Gleichgewichte** (Beste-Antwort-Dynamik auf Typengittern): nicht berechnet.
- **Mehrere Käufer und Verkäufer, zweiseitige private Information mit strategischer Verzögerung, abwechselnde Angebote mit privater Information, lernende Verhandler:** nicht gerechnet.
- **Stärkere Quellenprüfung:** die sechs Quellen sind nur nach Abstract eingeordnet; ein Abgleich der Grenzformeln mit Gul/Sonnenschein/Wilson steht aus.
- **Vormessung diskreter Gleichgewichte** (Beste-Antwort-Dynamik auf Typengittern, Plan V3b): im Bau nicht wiederholt, in dieser README deshalb nur als „H7: Nein (Plan)“.

## Lokal ausführen

```bash
pip install -r requirements.txt
streamlit run app.py
```

Python 3.12 oder neuer; die Streamlit-Cloud-Einstellung der Python-Version ist beim Deploy zu setzen und hier nachzutragen. Messreihen neu rechnen: `python tools/make_grid.py` (rund 5 Sekunden).

## Tests ausführen

```bash
pip install -r requirements-dev.txt
python -m pytest tests -q
```

Gebaut mit Streamlit, Plotly und fpdf2.

Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – Operations Research und Machine Learning ([Über mich](https://sebastianhanisch.net/ueber-mich.html)). Mehr zu den Demos: [Interaktive Demos](https://sebastianhanisch.net/demos.html).
