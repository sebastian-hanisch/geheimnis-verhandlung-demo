"""Literaturwerte (ORACLE-PLAYBOOK §5.1).

Quelle der Werte: die README der `myerson-satterthwaite-demo` (Abschnitt „Gegenprobe zur Literatur“, Stand der Einsicht 2026-11-01): bei gleichverteilten Typen auf [0, 1]^2 erstbest 1/6,
zweitbest 9/64 (84,4 %), bester Festpreis 1/2 mit Gewinn 1/8. Die README nennt diese Werte als Erwartung der Theorie (Myerson und Satterthwaite 1983) und prüft sie mit einem Typengitter;
sie sind kein Wert, den diese Demo mit ihrem eigenen Code erzeugt hat. Liegt die README nicht im Portfolio-Ordner, überspringen sich die Tests.

NICHT eingesehen, deshalb kein Test (in der README als „offen“ geführt): die Originalarbeiten Chatterjee/Samuelson 1983 (lineares Gleichgewicht und sein Gültigkeitsbereich),
Myerson/Satterthwaite 1983 (Satz zum Zweitbesten), Gul/Sonnenschein/Wilson 1986 (Grenzwert der Coase-Rekursion), Leininger/Linhart/Radner 1989 (Menge der Gleichgewichte)."""

from fractions import Fraction as F
from pathlib import Path

import pytest

import gvh_double_auction as DA

MS_README = Path(__file__).resolve().parent.parent.parent / "myerson-satterthwaite-demo" / "README.md"


@pytest.fixture(scope="module")
def ms_text():
    if not MS_README.exists():
        pytest.skip("README der myerson-satterthwaite-demo liegt nicht im Portfolio-Ordner")
    return " ".join(MS_README.read_text(encoding="utf-8").split())          # Zeilenumbrüche der README einebnen


def test_the_literature_values_are_stated_in_the_source(ms_text):
    assert "erstbest $1/6$, zweitbest $9/64$ (84,4 %)" in ms_text and "der beste Festpreis liegt bei 1/2 mit Gewinn 1/8" in ms_text


def test_first_best_second_best_and_best_fixed_price_match_the_source(ms_text):
    unit = (F(0), F(1), F(0), F(1))
    assert DA.first_best_stats(*unit)[1] == F(1, 6)
    assert abs(DA.second_best_stats(*unit)[1] - F(9, 64)) < F(1, 10 ** 12)
    assert float(F(9, 64) / F(1, 6)) == pytest.approx(0.844, abs=5e-4)                          # 84,4 %
    assert DA.one_price_stats(*unit, F(1, 2))[1] == F(1, 8)
    best = max(DA.one_price_stats(*unit, F(k, 100))[1] for k in range(101))
    assert best == F(1, 8)


def test_the_double_auction_equilibrium_reaches_the_second_best_in_the_linear_case(ms_text):
    """Die README nennt es als Literaturaussage: Chatterjee/Samuelson, lineares Gleichgewicht erreicht im gleichverteilten Fall das Zweitbeste."""
    assert "lineares Gleichgewicht erreicht im" in ms_text and "gleichverteilten Fall das Zweitbeste" in ms_text
    assert DA.cs_stats(F(0), F(1), F(0), F(1), F(1, 2))[1] == F(9, 64)
