"""Einstellungen der Demo als unveränderliches, hashbares Objekt (Schlüssel der Zwischenspeicher) und die daraus abgeleiteten Größen."""

from __future__ import annotations

from dataclasses import dataclass

import gvh_constants as C


@dataclass(frozen=True)
class Settings:
    """Alle Regler der Seitenleiste. Beträge in Euro je Tour; Prozentregler als ganze Zahlen (kein Gleitkomma-Vergleich bei Presets)."""

    v0: int = C.DEFAULT_V0          # untere Grenze des Werts des Verladers
    wv: int = C.DEFAULT_WV          # Breite des Wertebereichs
    c0: int = C.DEFAULT_C0          # untere Grenze der Kosten des Spediteurs
    wc: int = C.DEFAULT_WC          # Breite des Kostenbereichs
    kappa: int = C.DEFAULT_KAPPA    # Preisregel in Prozent
    p: int = C.DEFAULT_P            # Einpreis (Reiter 2)
    delta: int = C.DEFAULT_DELTA    # Diskontfaktor in Prozent (Reiter 3)
    T: int = C.DEFAULT_T            # Zahl der Runden (Reiter 3)
    vmax: int = C.DEFAULT_VMAX      # Obergrenze des Werts (Reiter 3)
    commit: bool = C.DEFAULT_COMMIT  # Selbstbindung (Reiter 3)
    dt: float = C.DEFAULT_DT        # Rundenlänge (Reiter 4)
    H: float = C.DEFAULT_H          # Horizont (Reiter 4)

    @property
    def v1(self) -> int:
        return self.v0 + self.wv

    @property
    def c1(self) -> int:
        return self.c0 + self.wc

    @property
    def big_l(self) -> int:
        """L = v1 - c0: der größte mögliche Handelsgewinn je Tour."""
        return self.v1 - self.c0

    @property
    def kappa_f(self) -> float:
        return self.kappa / 100

    @property
    def delta_f(self) -> float:
        return self.delta / 100
