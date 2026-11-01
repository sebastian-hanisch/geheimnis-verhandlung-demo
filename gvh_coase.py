"""Warten statt Handeln: der Spediteur bietet dem Verlader in jeder von T Runden einen Preis, der Wert des Verladers ist sein Geheimnis.

Modell: Kosten des Spediteurs 0 (nur der Aufschlag zählt, alles andere ist eine Verschiebung), Wert des Verladers v ~ U[0, 1] (in Euro: mal V). In jeder Runde nennt der Spediteur einen Preis;
der Verlader kauft oder wartet auf die nächste Runde. Beide diskontieren mit delta je Runde. Der Spediteur kann sich nicht binden: in jeder Runde bietet er neu.

Gleichgewicht (rückwärts, Skimming: wer den höchsten Wert hat, kauft zuerst). Bei t verbleibenden Runden und Resttyp-Bereich [0, x] ist der Preis pi_t * x und die Kaufgrenze w_t * x.
Skalierungsrekursion (aus den Bedingungen erster Ordnung): rho = 1 - delta * (1 - pi_{t-1}),  pi_t = rho^2 / (2 * (rho - delta * k_{t-1})),  w_t = pi_t / rho,
k_t = pi_t * (1 - w_t) + delta * k_{t-1} * w_t^2 (erwarteter Gewinn je x^2), Start pi_1 = 1/2, k_1 = 1/4.

Jede Funktion ist eine Einheit ohne versteckten Zustand. Die Rekursionsfunktionen laufen mit float wie mit fractions.Fraction (die Brüche wachsen doppelt exponentiell: nur für kleine T)."""

from __future__ import annotations

import math
from typing import NamedTuple


class Params(NamedTuple):
    """Parameter der Rekursion, Index t = Zahl der verbleibenden Runden (Index 0 ungenutzt)."""

    pi: list
    w: list
    k: list


class Path(NamedTuple):
    """Gleichgewichtspfad bei Start-Bereich [0, 1] (alles mal V in Euro): je Runde s = 1..T der Preis, die Obergrenze der noch nicht gekauft habenden Typen nach der Runde,
    die Kaufwahrscheinlichkeit in der Runde (Anteil an allen Typen), dazu Gewinn des Spediteurs, Überschuss des Verladers und diskontierter Gesamtwert."""

    price: list
    upper: list
    mass: list
    profit: float
    surplus: float
    welfare: float
    unsold: float
    mean_wait: float


def coase_step(delta, pi_prev, k_prev):
    """Eine Stufe der Rekursion: aus Preis-Anteil und Gewinn-Anteil bei t - 1 verbleibenden Runden die bei t. Rückgabe (pi, w, k)."""
    rho = 1 - delta * (1 - pi_prev)
    pi = rho * rho / (2 * (rho - delta * k_prev))
    w = pi / rho
    k = pi * (1 - w) + delta * k_prev * w * w
    return pi, w, k


def coase_params(delta, horizon: int) -> Params:
    """Alle Stufen der Rekursion für 1..horizon verbleibende Runden (float oder Fraction, je nach delta)."""
    half = (delta * 0 + 1) / 2                  # 1/2 im Zahlentyp von delta: float bleibt float, Fraction bleibt exakt
    pi = [None, half]
    w = [None, half]
    k = [None, half * half]
    for t in range(2, horizon + 1):
        p, wt, kt = coase_step(delta, pi[t - 1], k[t - 1])
        pi.append(p)
        w.append(wt)
        k.append(kt)
    return Params(pi, w, k)


def first_price(delta, horizon: int):
    """Preis der ersten Runde (Anteil an V) bei `horizon` Runden, ohne die Listen aufzubauen (für lange Horizonte)."""
    pi = 0.5
    k = 0.25
    for _ in range(2, horizon + 1):
        pi, _w, k = coase_step(delta, pi, k)
    return pi


def first_price_and_profit(delta, horizon: int):
    """Wie first_price, dazu der Gewinn des Spediteurs (Anteil an V)."""
    pi = 0.5
    k = 0.25
    for _ in range(2, horizon + 1):
        pi, _w, k = coase_step(delta, pi, k)
    return pi, k


def equilibrium_path(delta: float, horizon: int) -> Path:
    """Gleichgewichtspfad ab Start-Bereich [0, 1]: Runde s hat t = horizon - s + 1 verbleibende Runden; Preis pi_t * x, neue Grenze w_t * x.

    Gewinn = Summe delta^(s-1) * Preis * Kaufwahrscheinlichkeit; Überschuss = Summe delta^(s-1) * (Wert der Käufer - Zahlung); Gesamtwert = Summe delta^(s-1) * Wert der Käufer."""
    par = coase_params(delta, horizon)
    x = 1.0
    price: list[float] = []
    upper: list[float] = []
    mass: list[float] = []
    profit = surplus = welfare = wait = sold = 0.0
    disc = 1.0
    for s in range(1, horizon + 1):
        t = horizon - s + 1
        p = par.pi[t] * x
        xn = par.w[t] * x
        m = x - xn
        value = (x * x - xn * xn) / 2          # Summe der Werte der Käufer dieser Runde (Dichte 1 auf [0, 1])
        profit += disc * p * m
        surplus += disc * (value - p * m)
        welfare += disc * value
        wait += (s - 1) * m
        sold += m
        price.append(p)
        upper.append(xn)
        mass.append(m)
        x = xn
        disc *= delta
    return Path(price, upper, mass, profit, surplus, welfare, x, wait / sold if sold > 0 else 0.0)


def commitment_outcome():
    """Selbstbindung: ein einziges Angebot zum Preis 1/2 (das statische Monopol). Rückgabe (Gewinn, Überschuss, Gesamtwert, nie gekauft), alles je V."""
    return 0.25, 0.125, 0.375, 0.5


def commitment_path() -> Path:
    """Pfad mit Selbstbindung: eine Runde, Preis 1/2, es kaufen die Werte ab 1/2 (Anteil 1/2); wer nicht kauft, kauft nie."""
    gain, surplus, welfare, unsold = commitment_outcome()
    return Path([0.5], [0.5], [0.5], gain, surplus, welfare, unsold, 0.0)


def limit_price(delta):
    """Aus Messungen erkannte Grenzform des ersten Preises bei unendlichem Horizont: s / (1 + s) mit s = sqrt(1 - delta) (Messhypothese, kein Beweis)."""
    s = math.sqrt(1 - delta)
    return s / (1 + s)


def fixed_horizon_limit(rate, horizon_time):
    """Aus Messungen erkannter Grenzwert des ersten Preises bei festem Zeithorizont H und Rundenlänge gegen 0: (1/2) * exp(-r * H) (Messhypothese, kein Beweis)."""
    return 0.5 * math.exp(-rate * horizon_time)


def round_discount(rate, round_length):
    """Diskontfaktor je Runde bei stetiger Rate r und Rundenlänge D: exp(-r * D)."""
    return math.exp(-rate * round_length)


def rounds_for_horizon(horizon_time, round_length):
    """Zahl der Runden eines Zeithorizonts: H / D, gerundet, mindestens 1."""
    return max(1, round(horizon_time / round_length))


def horizon_for_tolerance(delta, tol=0.01, t_max=2_000_000):
    """Kleinste Rundenzahl T, bei der der erste Preis höchstens tol (relativ) von seinem Grenzwert bei unendlichem Horizont abweicht; None, wenn t_max nicht reicht."""
    target = limit_price(delta)
    pi = 0.5
    k = 0.25
    if abs(pi - target) <= tol * target:
        return 1
    for t in range(2, t_max + 1):
        pi, _w, k = coase_step(delta, pi, k)
        if abs(pi - target) <= tol * target:
            return t
    return None


def stationary_residual(delta, p):
    """Stationäre Gleichung des Grenzfalls (Preis p wiederholt sich von Runde zu Runde): F(p) = k * (1 - delta * w^2) - p * (1 - w), mit rho = 1 - delta + delta * p,
    w = p / rho, k = (rho - rho^2 / (2 p)) / delta. F(p) = 0 genau im Fixpunkt der Rekursion. Läuft mit float und Fraction."""
    rho = 1 - delta + delta * p
    w = p / rho
    k = (rho - rho * rho / (2 * p)) / delta
    return k * (1 - delta * w * w) - p * (1 - w)
