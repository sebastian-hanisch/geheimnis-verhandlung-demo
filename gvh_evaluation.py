"""Auswertung: Kennzahlen je Reiter und die Verdikte der App als reine Funktionen `verdict_*(...) -> (Art, Text)` (Art = Name einer st-Methode).

Die Zahlen stammen aus den geschlossenen Formeln von `gvh_double_auction` und `gvh_coase`; der Gitterbeweis (Beste-Antwort-Lücke) läuft live als Gegenprobe."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

import gvh_coase as CO
import gvh_constants as C
import gvh_double_auction as DA
from gvh_scenario import Settings


def de(x: float, nd: int = 2) -> str:
    """Zahl mit deutschem Dezimalkomma, Tausenderpunkt und typografischem Minus."""
    text = f"{x:,.{nd}f}"
    text = text.replace(",", "\0").replace(".", ",").replace("\0", ".")
    if text.startswith("-") and float(text.replace(".", "").replace(",", ".")) == 0:
        text = text[1:]
    return text.replace("-", "−")


def pct(x: float, nd: int = 1) -> str:
    """Anteil als Prozentzahl mit Komma (x ist ein Anteil, 0,5 gibt „50,0“)."""
    return de(100 * x, nd)


# ====================================================================================================================================================
# Reiter 1: doppelte Auktion
# ====================================================================================================================================================
@dataclass(frozen=True)
class AuctionView:
    s: Settings
    st: DA.Strategies
    validity: DA.Validity
    gap_seller: float
    gap_buyer: float
    fb_prob: float
    fb_gain: float
    sb_prob: float
    sb_gain: float
    theta: float
    cs_prob: float | None          # None: Formel gilt nicht
    cs_gain: float | None
    no_gain_possible: bool          # v1 <= c0

    @property
    def gap(self) -> float:
        return max(self.gap_seller, self.gap_buyer)

    @property
    def grid_agrees(self) -> bool:
        """Die Gitterprüfung bestätigt das Urteil der Formel (Gültigkeit genau dann, wenn die Lücke null ist)."""
        return (self.gap <= C.GAP_TOL) == self.validity.valid

    @property
    def trade_threshold(self) -> float | None:
        """Bei kappa = 1/2: Handel genau bei v - c >= L/4 (Euro), sonst None."""
        return self.s.big_l / 4 if self.s.kappa == 50 else None


def analyse_auction(s: Settings) -> AuctionView:
    v0, v1, c0, c1, k = float(s.v0), float(s.v1), float(s.c0), float(s.c1), s.kappa_f
    st = DA.cs_coefficients(v0, v1, c0, c1, k)
    if v1 <= c0:
        return AuctionView(s, st, DA.Validity(0.0, 0.0, False, 0.0), 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, None, None, True)
    val = DA.cs_validity(v0, v1, c0, c1, k, tol=C.VALID_TOL)
    gs, gb = DA.best_response_gap(v0, v1, c0, c1, k, ntypes=C.GRID_TYPES, ngrid=C.GRID_POINTS)
    fp, fg = DA.first_best_stats(v0, v1, c0, c1)
    sp, sg, th = DA.second_best_stats(v0, v1, c0, c1)
    cp = cg = None
    if val.valid:
        cp, cg = DA.cs_stats(v0, v1, c0, c1, k)
    return AuctionView(s, st, val, gs, gb, fp, fg, sp, sg, th, cp, cg, False)


def verdict_auction(v: AuctionView) -> tuple[str, str]:
    """Hauptverdikt von Reiter 1: Gültigkeit der Formel, Gewinn gegen Erst- und Zweitbestes."""
    s = v.s
    if v.no_gain_possible:
        return "info", f"Der höchste Wert ({de(s.v1, 0)} Euro) liegt nicht über den niedrigsten Kosten ({de(s.c0, 0)} Euro): es gibt keinen Handelsgewinn, nichts zu verhandeln."
    if not v.validity.valid:
        parts = []
        if v.validity.margin_low < -C.VALID_TOL and s.kappa < 100:
            parts.append(f"die niedrigste Forderung liegt {de(-v.validity.margin_low)} Euro unter dem niedrigsten Gebot")
        if v.validity.margin_high < -C.VALID_TOL and s.kappa > 0:
            parts.append(f"die höchste Forderung liegt {de(-v.validity.margin_high)} Euro unter dem höchsten Gebot")
        why = " und ".join(parts) if parts else "die Bereiche sind entartet"
        extra = ""
        if s.kappa == 50:
            extra = f" (Bedingung für κ = ½: v₀ − c₀ = {de(s.v0 - s.c0, 0)} und v₁ − c₁ = {de(s.v1 - s.c1, 0)} dürfen höchstens L/4 = {de(s.big_l / 4)} Euro betragen)"
        return "warning", (f"Formel gilt hier nicht: {why}{extra}. Dann ist das lineare Profil kein Gleichgewicht, und die App rechnet keinen Gleichgewichtsgewinn aus. "
                           f"Ein Gleichgewicht müsste anders aussehen (in dieser Demo nicht berechnet). Gegenprobe am Gitter: größte Lücke {de(v.gap)} Euro. "
                           f"Als Schranke bleibt das Zweitbeste: {de(v.sb_gain)} Euro je Tour (Erstbestes {de(v.fb_gain)}).")
    lost = 1 - v.cs_prob / v.fb_prob if v.fb_prob > 0 else 0.0
    share = v.cs_gain / v.fb_gain if v.fb_gain > 0 else 0.0
    if v.trade_threshold is not None:
        rule = f"Gehandelt wird genau, wenn der Wert die Kosten um mindestens L/4 = {de(v.trade_threshold)} Euro übersteigt."
    else:
        rule = "Gehandelt wird genau, wenn das Gebot die Forderung erreicht."
    equal = abs(v.cs_gain - v.sb_gain) <= 1e-9 * max(1.0, v.sb_gain)
    if equal:
        second = "Das ist das Zweitbeste (Myerson und Satterthwaite): mehr schafft kein Verfahren, bei dem beide freiwillig mitmachen und niemand Geld zuschießt."
    else:
        second = f"Das liegt {pct(1 - v.cs_gain / v.sb_gain)} % unter dem Zweitbesten ({de(v.sb_gain)} Euro)."
    return "success", (f"{rule} Gewinn je Tour: {de(v.cs_gain)} Euro, das sind {pct(share)} % des Erstbesten ({de(v.fb_gain)} Euro); {pct(lost)} % der Touren, die sich lohnen würden, "
                       f"kommen nicht zustande. {second}")


def verdict_grid_check(v: AuctionView) -> tuple[str, str]:
    """Gegenprobe am Gitter (Beste Antwort gegen die Formelstrategie der anderen Seite)."""
    if v.no_gain_possible:
        return "info", "Kein Handelsgewinn möglich: nichts zu prüfen."
    where = f"{C.GRID_TYPES} Typen je Seite, {C.GRID_POINTS} Gebote im Gitter"
    if v.grid_agrees and v.validity.valid:
        return "success", f"Gegenprobe am Gitter ({where}): kein Typ gewinnt durch Abweichen, größte Lücke {de(v.gap, 6)} Euro."
    if v.grid_agrees:
        return "info", f"Gegenprobe am Gitter ({where}): ein Typ gewinnt durch Abweichen, größte Lücke {de(v.gap)} Euro. Das bestätigt, dass die Formel hier nicht gilt."
    return "error", f"Gegenprobe am Gitter ({where}) widerspricht dem Gültigkeitskriterium: größte Lücke {de(v.gap, 6)} Euro, Kriterium {'gültig' if v.validity.valid else 'ungültig'}."


# --- Preisregel (Experiment E2) -----------------------------------------------------------------------------------------------------------------------
@dataclass(frozen=True)
class KappaRow:
    kappa: int          # Prozent
    valid: bool
    gain: float | None
    share_first: float | None


def kappa_rows(s: Settings) -> list[KappaRow]:
    """Gewinn des linearen Profils je Preisregel (Prozent), nur wo die Formel gilt. Bereiche und Erstbestes wie in der Seitenleiste."""
    v0, v1, c0, c1 = float(s.v0), float(s.v1), float(s.c0), float(s.c1)
    if v1 <= c0:
        return [KappaRow(k, False, None, None) for k in C.KAPPA_GRID]
    _fp, fg = DA.first_best_stats(v0, v1, c0, c1)
    rows = []
    for kp in C.KAPPA_GRID:
        val = DA.cs_validity(v0, v1, c0, c1, kp / 100, tol=C.VALID_TOL)
        if val.valid:
            _p, g = DA.cs_stats(v0, v1, c0, c1, kp / 100)
            rows.append(KappaRow(kp, True, g, g / fg if fg > 0 else 0.0))
        else:
            rows.append(KappaRow(kp, False, None, None))
    return rows


def verdict_kappa(rows: list[KappaRow], s: Settings) -> tuple[str, str]:
    """Verdikt zur Preisregel: wo der Gewinn am größten ist, und ob die Kurve symmetrisch ist (nur über gültige Paare)."""
    ok = [r for r in rows if r.valid]
    if not ok:
        return "warning", "Für keine Preisregel gilt die Formel bei diesen Bereichen: keine Kurve."
    best = max(ok, key=lambda r: r.gain)
    pairs = [(r, next(q for q in rows if q.kappa == 100 - r.kappa)) for r in ok if r.kappa < 50]
    both = [(a, b) for a, b in pairs if b.valid]
    sym = all(abs(a.gain - b.gain) <= 1e-9 * max(1.0, abs(a.gain)) for a, b in both)
    ends = [r for r in ok if r.kappa in (0, 100)]
    ends_txt = ""
    if ends:
        ends_txt = " Die beiden Ränder (der Verkäufer setzt den Preis, der Käufer setzt den Preis) liefern " + " und ".join(f"{pct(r.share_first)} %" for r in ends) + " des Erstbesten."
    pairs_txt = "Paar" if len(both) == 1 else "Paare"
    sym_txt = f" Die Kurve ist in κ ↔ 1 − κ symmetrisch ({len(both)} {pairs_txt} geprüft)." if sym and both else (" Die Kurve ist nicht symmetrisch." if both else "")
    where = f"{len(ok)} von {len(rows)} Preisregeln gelten"
    return "info", (f"Am größten ist der Gewinn bei κ = {de(best.kappa / 100, 2)}: {de(best.gain)} Euro je Tour, {pct(best.share_first)} % des Erstbesten ({where}).{ends_txt}{sym_txt}")


# ====================================================================================================================================================
# Reiter 2: Einpreis-Gleichgewichte
# ====================================================================================================================================================
@dataclass(frozen=True)
class OnePriceView:
    s: Settings
    prob: float
    gain: float
    gap_seller: float
    gap_buyer: float
    sb_gain: float
    fb_gain: float
    cs_gain: float | None
    curve_p: np.ndarray
    curve_gain: np.ndarray

    @property
    def gap(self) -> float:
        return max(self.gap_seller, self.gap_buyer)


def analyse_one_price(s: Settings, cs_gain: float | None) -> OnePriceView:
    v0, v1, c0, c1 = float(s.v0), float(s.v1), float(s.c0), float(s.c1)
    p = float(s.p)
    prob, gain = DA.one_price_stats(v0, v1, c0, c1, p)
    gs, gb = DA.one_price_gap(v0, v1, c0, c1, p, ntypes=C.GRID_TYPES, ngrid=C.GRID_POINTS)
    if v1 > c0:
        _sp, sg, _th = DA.second_best_stats(v0, v1, c0, c1)
        _fp, fg = DA.first_best_stats(v0, v1, c0, c1)
    else:
        sg = fg = 0.0
    grid = np.linspace(min(v0, c0), max(v1, c1), 241)
    curve = np.array([DA.one_price_stats(v0, v1, c0, c1, float(q))[1] for q in grid])
    return OnePriceView(s, prob, gain, gs, gb, sg, fg, cs_gain, grid, curve)


def verdict_one_price(v: OnePriceView) -> tuple[str, str]:
    s = v.s
    if v.sb_gain <= 0:
        return "info", "Kein Handelsgewinn möglich: auch kein Einpreis-Gleichgewicht hat etwas zu verteilen."
    best_i = int(np.argmax(v.curve_gain))
    best_p, best_gain = float(v.curve_p[best_i]), float(v.curve_gain[best_i])
    eq = "Gegenprobe am Gitter: kein Typ gewinnt durch Abweichen" if v.gap <= C.GAP_TOL else f"Gegenprobe am Gitter schlägt an (Lücke {de(v.gap)} Euro)"
    cmp_cs = ""
    if v.cs_gain is not None:
        cmp_cs = f" Das lineare Gleichgewicht aus Reiter 1 schafft {de(v.cs_gain)} Euro."
    if v.prob <= 0:
        return "info", (f"Beim Einpreis {de(s.p, 0)} Euro handelt niemand: auch das ist ein Gleichgewicht (kein Typ gewinnt durch Abweichen am Gitter: {eq.split(':')[-1].strip()}), mit Gewinn 0. "
                        f"Der beste Einpreis auf dem Raster liegt bei {de(best_p, 1)} Euro mit {de(best_gain)} Euro je Tour.{cmp_cs}")
    return "info", (f"Einpreis {de(s.p, 0)} Euro: Gewinn {de(v.gain)} Euro je Tour, {pct(v.gain / v.sb_gain)} % des Zweitbesten ({de(v.sb_gain)} Euro); {eq}. "
                    f"Der beste Einpreis auf dem Raster ({de(best_p, 1)} Euro) schafft {de(best_gain)} Euro, {pct(best_gain / v.sb_gain)} % des Zweitbesten.{cmp_cs}")


# ====================================================================================================================================================
# Reiter 3: Warten statt Handeln
# ====================================================================================================================================================
@dataclass(frozen=True)
class CoaseView:
    s: Settings
    path: CO.Path            # Gleichgewichtspfad ohne Selbstbindung
    bound: CO.Path           # Pfad mit Selbstbindung (ein Angebot zum Preis V/2)
    t_tol: int | None
    limit: float

    @property
    def shown(self) -> CO.Path:
        """Der Pfad, den die Diagramme zeigen: je nach Schalter „Selbstbindung“."""
        return self.bound if self.s.commit else self.path

    @property
    def scale(self) -> float:
        return float(self.s.vmax)

    @property
    def first_price(self) -> float:
        return self.path.price[0] * self.scale


def analyse_coase(s: Settings) -> CoaseView:
    path = CO.equilibrium_path(s.delta_f, s.T)
    t_tol = CO.horizon_for_tolerance(s.delta_f, 0.01, t_max=20_000) if s.delta < 100 else None
    return CoaseView(s, path, CO.commitment_path(), t_tol, CO.limit_price(s.delta_f))


def visible_rounds(path: CO.Path, share: float = 0.9999) -> int:
    """Wie viele Runden die Diagramme zeigen: bis die aufgelaufenen Käufer `share` aller Verlader erreichen (mindestens fünf, höchstens alle); danach ändert sich nichts Sichtbares mehr."""
    total = 0.0
    n = len(path.mass)
    for i, m in enumerate(path.mass, 1):
        total += m
        if total >= share:
            return max(i, min(5, n))
    return n


def coase_totals(v: CoaseView) -> dict:
    """Gewinn, Überschuss, Gesamtwert (alle in Euro je Tour) ohne und mit Selbstbindung; das Erstbeste ist V / 2."""
    sc = v.scale
    cp, cs_, cw, cn = CO.commitment_outcome()
    return {
        "free": {"profit": v.path.profit * sc, "surplus": v.path.surplus * sc, "welfare": v.path.welfare * sc, "unsold": v.path.unsold},
        "bound": {"profit": cp * sc, "surplus": cs_ * sc, "welfare": cw * sc, "unsold": cn},
        "first_best": 0.5 * sc,
    }


def verdict_coase(v: CoaseView) -> tuple[str, str]:
    s = v.s
    tot = coase_totals(v)
    f, b = tot["free"], tot["bound"]
    first = v.first_price
    head = (f"Bei δ = {de(s.delta_f, 2)} und {s.T} Runden bietet der Spediteur in Runde 1 {de(first)} Euro ({pct(v.path.price[0])} % von V = {de(v.scale, 0)} Euro; "
            f"das Einmalangebot mit Selbstbindung wäre {de(v.scale / 2)} Euro).")
    if s.T == 1:
        return "info", head + " Bei einer einzigen Runde gibt es nichts abzuwarten: ohne und mit Selbstbindung ist alles gleich."
    gain_txt = f" Gewinn {de(f['profit'])} Euro statt {de(b['profit'])} Euro mit Selbstbindung ({pct(f['profit'] / b['profit'])} %)"
    surplus_txt = f", Überschuss des Verladers {de(f['surplus'])} statt {de(b['surplus'])} Euro"
    whole = "höher" if f["welfare"] > b["welfare"] + 1e-12 else ("gleich" if abs(f["welfare"] - b["welfare"]) <= 1e-12 else "niedriger")
    welfare_txt = f", diskontierter Gesamtwert {de(f['welfare'])} statt {de(b['welfare'])} Euro ({whole} ohne Selbstbindung; Erstbestes {de(tot['first_best'])})."
    wait = f" Käufer warten im Mittel {de(v.path.mean_wait)} Runden; {pct(v.path.mass[0])} % aller Typen kaufen schon in Runde 1."
    horizon = ""
    if v.t_tol is not None:
        if s.T >= v.t_tol:
            horizon = f" Ab {v.t_tol} Runden liegt der erste Preis erstmals höchstens 1 % neben seinem Grenzwert bei unendlichem Horizont ({pct(v.limit)} % von V); dieser Horizont ist erreicht."
        else:
            horizon = f" Bis zum Grenzwert bei unendlichem Horizont ({pct(v.limit)} % von V) fehlt Horizont: erst ab {v.t_tol} Runden liegt der erste Preis höchstens 1 % daneben."
    return "info", head + gain_txt + surplus_txt + welfare_txt + wait + horizon


# ====================================================================================================================================================
# Reiter 4: Rundenlänge und Horizont
# ====================================================================================================================================================
@dataclass(frozen=True)
class HorizonRow:
    dt: float
    rounds: int
    horizon: float        # tatsächlicher Horizont T * dt
    delta: float
    price: float          # erster Preis, Anteil von V
    limit_long: float     # Grenzwert bei unendlichem Horizont zu diesem delta
    limit_fixed: float    # (1/2) exp(-H) zum tatsächlichen Horizont


def fixed_horizon_rows(s: Settings) -> list[HorizonRow]:
    """Erster Preis je Rundenlänge bei festem Zeithorizont (Rate r = 1: Zeit in Einheiten von 1/r)."""
    rows = []
    for dt in C.DT_CHOICES:
        t = CO.rounds_for_horizon(s.H, dt)
        d = CO.round_discount(1.0, dt)
        horizon = t * dt
        rows.append(HorizonRow(dt, t, horizon, d, CO.first_price(d, t), CO.limit_price(d), CO.fixed_horizon_limit(1.0, horizon)))
    return rows


def delta_curve() -> list[tuple[float, float]]:
    """Grenzwert des ersten Preises bei unendlichem Horizont über dem Diskontfaktor (Messhypothese s / (1 + s))."""
    return [(p / 100, CO.limit_price(p / 100)) for p in C.DELTA_CURVE]


CURVE_ROUNDS = (2, 10, 30, 200)


def price_curves(rounds: int) -> dict[int, list[float]]:
    """Erster Preis (Anteil von V) über dem Diskontfaktor 0, 0,01 ... 0,99 für feste Rundenzahlen: einige feste und die gewählte."""
    ts = sorted(set(CURVE_ROUNDS) | {rounds})
    return {t: [CO.first_price(p / 100, t) for p in C.DELTA_CURVE] for t in ts}


def verdict_delta_curves(curves: dict[int, list[float]], rounds: int) -> tuple[str, str]:
    """Wo hat der erste Preis sein Minimum über δ? Bei kurzem Horizont steigt er für große δ wieder."""
    parts = []
    for t, prices in sorted(curves.items()):
        i = prices.index(min(prices))
        d_min = C.DELTA_CURVE[i] / 100
        if i == len(prices) - 1:
            parts.append(f"T = {t}: fällt über das ganze Raster bis δ = {de(d_min, 2)}")
        else:
            parts.append(f"T = {t}: Minimum {pct(prices[i])} % bei δ = {de(d_min, 2)}, danach wieder höher (bei δ = 0,99: {pct(prices[-1])} %)")
    return "info", "Erster Preis (Anteil von V) über dem Diskontfaktor auf dem Raster 0,00 bis 0,99 — " + "; ".join(parts) + f". Die gewählte Rundenzahl der Seitenleiste ist T = {rounds}."


HORIZON_DELTAS = (0.5, 0.7, 0.9, 0.95, 0.99, 0.995)


def horizon_needed_rows() -> list[dict]:
    """Kleinstes T, bei dem der erste Preis höchstens 1 % vom Grenzwert abweicht, für einige Diskontfaktoren (vorgerechnet im Aufruf, O(T))."""
    rows = []
    for d in HORIZON_DELTAS:
        t = CO.horizon_for_tolerance(d, 0.01)
        rows.append({"delta": d, "limit": CO.limit_price(d), "T": t, "ratio": t * (1 - d) if t else None})
    return rows


def verdict_fixed(rows: list[HorizonRow], s: Settings) -> tuple[str, str]:
    """Verdikt zu Reiter 4: der erste Preis über der Rundenlänge bei festem Horizont, neben den beiden Formeln (Messhypothesen)."""
    first, last = rows[0], rows[-1]
    mono = all(a.price >= b.price - 1e-12 for a, b in zip(rows, rows[1:]))
    cur = next(r for r in rows if abs(r.dt - s.dt) < 1e-12)
    note = "" if s.H <= 2 else " Die Formel ½·e^(−H) ist nur für H bis 2 gemessen; bei H = 4 war sie noch nicht erreicht."
    plural = "n" if first.rounds != 1 else ""
    trend = " (der Preis sinkt über alle elf Rundenlängen)" if mono else " (nicht über alle elf Rundenlängen monoton)"
    return "info", (f"Bei Rundenlänge {de(first.dt, 4)} ({first.rounds} Runde{plural}) bietet der Spediteur zuerst {pct(first.price)} % von V, bei {de(last.dt, 4)} ({last.rounds} Runden) {pct(last.price)} %{trend}. "
                    f"Bei der kürzesten Rundenlänge läge der Grenzwert bei unendlichem Horizont bei nur {pct(last.limit_long)} % von V; ½·e^(−H) für den Horizont {de(last.horizon, 2)} ist {pct(last.limit_fixed)} %.{note} "
                    f"Gewählt: Rundenlänge {de(cur.dt, 4)}, {cur.rounds} Runden, δ = {de(cur.delta, 4)}, erster Preis {pct(cur.price)} % von V.")

# ====================================================================================================================================================
# Tabellen und Verdikte der Reiter
# ====================================================================================================================================================
def auction_rows(v: AuctionView) -> list[dict]:
    """Strategien und Schwellen der Hauptansicht (Euro je Tour)."""
    if v.no_gain_possible:
        return [{"Größe": "Handelsgewinn", "Wert": "keiner möglich"}]
    st = v.st
    rows = [
        {"Größe": "Gebot des Verladers b(v)", "Wert": f"{de(st.ab)} + {de(st.bb, 4)}·v"},
        {"Größe": "Forderung des Spediteurs s(c)", "Wert": f"{de(st.as_)} + {de(st.bs, 4)}·c"},
        {"Größe": "niedrigste Forderung minus niedrigstes Gebot", "Wert": de(v.validity.margin_low)},
        {"Größe": "höchste Forderung minus höchstes Gebot", "Wert": de(v.validity.margin_high)},
        {"Größe": "Handelswahrscheinlichkeit: Erstbestes / Zweitbestes", "Wert": f"{pct(v.fb_prob)} % / {pct(v.sb_prob)} %"},
        {"Größe": "Schwelle des Zweitbesten (Handel bei v − c ≥ θ·L)", "Wert": f"θ = {de(v.theta, 4)}, also {de(v.theta * v.s.big_l)} Euro"},
    ]
    if v.cs_prob is not None:
        rows.insert(4, {"Größe": "Handelswahrscheinlichkeit im Gleichgewicht", "Wert": f"{pct(v.cs_prob)} %"})
    return rows


def best_one_price_gain(s: Settings) -> float | None:
    """Größter Gewinn eines Einpreis-Gleichgewichts über dem Raster der Preise (None, wenn kein Handelsgewinn möglich ist)."""
    v0, v1, c0, c1 = float(s.v0), float(s.v1), float(s.c0), float(s.c1)
    if v1 <= c0:
        return None
    grid = np.linspace(min(v0, c0), max(v1, c1), 241)
    return max(DA.one_price_stats(v0, v1, c0, c1, float(q))[1] for q in grid)


SHIFT_FRACTIONS = (0.0, 0.1, 0.2, 0.3, 1 / 3, 0.4, 0.6, 0.8, 1.0)


@dataclass(frozen=True)
class ShiftRow:
    shift: float
    v0: float
    valid: bool
    margin: float
    gap: float
    cs_gain: float | None
    share_first: float | None
    share_second: float | None
    equals_second: bool | None


def shift_rows(s: Settings) -> list[ShiftRow]:
    """Der Wertebereich der Seitenleiste um x Euro nach oben verschoben (x = Bruchteile der Kostenbreite), Breiten, Kosten und κ der Seitenleiste."""
    rows = []
    for frac in SHIFT_FRACTIONS:
        x = frac * s.wc
        v0, v1, c0, c1 = s.v0 + x, s.v0 + x + s.wv, float(s.c0), float(s.c1)
        k = s.kappa_f
        if v1 <= c0:
            rows.append(ShiftRow(x, v0, False, 0.0, 0.0, None, None, None, None))
            continue
        val = DA.cs_validity(v0, v1, c0, c1, k, tol=C.VALID_TOL)
        gs, gb = DA.best_response_gap(v0, v1, c0, c1, k, ntypes=C.GRID_TYPES, ngrid=C.GRID_POINTS)
        _fp, fg = DA.first_best_stats(v0, v1, c0, c1)
        _sp, sg, _th = DA.second_best_stats(v0, v1, c0, c1)
        margin = val.margin
        if val.valid:
            _p, cg = DA.cs_stats(v0, v1, c0, c1, k)
            rows.append(ShiftRow(x, v0, True, margin, max(gs, gb), cg, cg / fg, cg / sg, abs(cg - sg) <= 1e-9 * max(1.0, sg)))
        else:
            rows.append(ShiftRow(x, v0, False, margin, max(gs, gb), None, None, None, None))
    return rows


def shift_table(rows: list[ShiftRow]) -> list[dict]:
    return [{"Verschiebung (Euro)": de(r.shift), "untere Wertgrenze": de(r.v0), "kleinster Abstand Forderung − Gebot": de(r.margin), "Formel gilt": "ja" if r.valid else "nein",
             "Lücke am Gitter": de(r.gap, 4), "Gewinn Gleichgewicht": de(r.cs_gain) if r.cs_gain is not None else "–",
             "Anteil am Erstbesten": f"{pct(r.share_first)} %" if r.share_first is not None else "–",
             "Anteil am Zweitbesten": f"{pct(r.share_second)} %" if r.share_second is not None else "–"} for r in rows]


def verdict_shift(rows: list[ShiftRow], s: Settings) -> tuple[str, str]:
    valid = [r for r in rows if r.valid]
    if not valid:
        return "warning", f"Bei keiner der {len(rows)} Verschiebungen gilt die Formel; die Tabelle zeigt, wie groß die Lücke am Gitter dort ist."
    equal = [r for r in valid if r.equals_second]
    grid_ok = sum(1 for r in rows if (r.gap <= C.GAP_TOL) == r.valid)
    last_valid = max(valid, key=lambda r: r.shift)
    first_invalid = min((r for r in rows if not r.valid and r.shift > last_valid.shift), key=lambda r: r.shift, default=None)
    edge = f" Die nächste Verschiebung ({de(first_invalid.shift)} Euro) liegt schon außerhalb: Lücke am Gitter {de(first_invalid.gap, 4)} Euro." if first_invalid else ""
    return "info", (f"Die Formel gilt bei {len(valid)} von {len(rows)} Verschiebungen, bis zur Verschiebung {de(last_valid.shift)} Euro.{edge} Im Gültigkeitsbereich trifft der Gewinn des Gleichgewichts das Zweitbeste "
                    f"in {len(equal)} von {len(valid)} Zeilen. Die Gitterprüfung stimmt in {grid_ok} von {len(rows)} Zeilen mit dem Kriterium überein.")


def rows_validity(tables: dict) -> list[dict]:
    out = []
    for mode, name in (("half", "κ = ½"), ("random", "zufälliges κ (0,1 bis 0,9)")):
        sm = tables["validity"][mode]["summary"]
        out.append({"Preisregel": name, "Instanzen": sm["total"], "beide gültig": sm["both_valid"], "beide ungültig": sm["both_invalid"],
                    "nur Kriterium gültig": sm["criterion_only"], "nur Gitter gültig": sm["numeric_only"],
                    "größte relative Abweichung Gleichgewicht / Zweitbestes": f"{sm['rel_dev_max']:.1e}" if sm["valid_with_second_best"] else "–"})
    return out


def verdict_table_validity(tables: dict) -> tuple[str, str]:
    half, rand = tables["validity"]["half"]["summary"], tables["validity"]["random"]["summary"]
    miss = half["criterion_only"] + half["numeric_only"] + rand["criterion_only"] + rand["numeric_only"]
    kind = "success" if miss == 0 else "warning"
    return kind, (f"Kriterium und Gitter stimmen in {half['both_valid'] + half['both_invalid']} von {half['total']} Zufallsinstanzen bei κ = ½ überein ({half['both_valid']} gültig, {half['both_invalid']} ungültig) "
                  f"und in {rand['both_valid'] + rand['both_invalid']} von {rand['total']} bei zufälligem κ ({rand['both_valid']} gültig); Abweichungen: {miss}. "
                  f"In den {half['valid_with_second_best']} gültigen Fällen bei κ = ½ liegt der Gewinn des Gleichgewichts höchstens {half['rel_dev_max']:.1e} (relativ) neben dem Zweitbesten.")


def kappa_table(rows: list[KappaRow]) -> list[dict]:
    pick = {0, 10, 25, 40, 50, 60, 75, 90, 100}
    return [{"κ": de(r.kappa / 100, 2), "Formel gilt": "ja" if r.valid else "nein", "Gewinn (Euro je Tour)": de(r.gain) if r.gain is not None else "–",
             "Anteil am Erstbesten": f"{pct(r.share_first)} %" if r.share_first is not None else "–"} for r in rows if r.kappa in pick]


def one_price_rows(s: Settings) -> list[dict]:
    """Einpreis-Gleichgewichte bei fünf Preisen (10, 30, 50, 70 und 90 Prozent der Spanne von der kleinsten bis zur größten Grenze), mit Gegenprobe am Gitter."""
    v0, v1, c0, c1 = float(s.v0), float(s.v1), float(s.c0), float(s.c1)
    lo, hi = min(v0, c0), max(v1, c1)
    sg = DA.second_best_stats(v0, v1, c0, c1)[1] if v1 > c0 else 0.0
    rows = []
    for frac in (0.1, 0.3, 0.5, 0.7, 0.9):
        p = lo + frac * (hi - lo)
        prob, gain = DA.one_price_stats(v0, v1, c0, c1, p)
        gs, gb = DA.one_price_gap(v0, v1, c0, c1, p, ntypes=C.GRID_TYPES, ngrid=C.GRID_POINTS)
        rows.append({"Einpreis p": de(p), "Handelswahrscheinlichkeit": f"{pct(prob)} %", "Gewinn": de(gain), "Anteil am Zweitbesten": f"{pct(gain / sg)} %" if sg > 0 else "–",
                     "Lücke am Gitter": de(max(gs, gb), 6)})
    return rows


def commitment_rows(v: CoaseView) -> list[dict]:
    tot = coase_totals(v)
    out = []
    for name, key, path in (("ohne Selbstbindung", "free", v.path), ("mit Selbstbindung", "bound", v.bound)):
        t = tot[key]
        out.append({"Pfad": name, "erster Preis": de(path.price[0] * v.scale), "Gewinn Spediteur": de(t["profit"]), "Überschuss Verlader": de(t["surplus"]), "Gesamtwert": de(t["welfare"]),
                    "nie gekauft": f"{pct(t['unsold'])} %", "mittlere Wartezeit der Käufer (Runden)": de(path.mean_wait, 2)})
    return out


def fixed_table(rows: list[HorizonRow]) -> list[dict]:
    return [{"Rundenlänge Δ": de(r.dt, 4), "Runden": r.rounds, "Horizont": de(r.horizon, 2), "δ": de(r.delta, 4), "erster Preis (% von V)": pct(r.price),
             "Grenzwert unendlicher Horizont (%)": pct(r.limit_long), "½·e^(−H) (%)": pct(r.limit_fixed)} for r in rows]


def horizon_table() -> list[dict]:
    return [{"δ": de(r["delta"], 3), "Grenzwert s/(1+s) (% von V)": pct(r["limit"]), "kleinstes T": r["T"] if r["T"] is not None else "über 2 000 000",
             "T·(1 − δ)": de(r["ratio"], 2) if r["ratio"] is not None else "–"} for r in horizon_needed_rows()]


def rows_deviation(tables: dict) -> list[dict]:
    return [{"δ": de(r["delta"], 2), "Runden bis": r["horizon"], "größte Gewinnsteigerung durch Abweichen": f"{r['worst']:.1e}", "Skimming verletzt in": f"{r['violations']} von {r['horizon']}"}
            for r in tables["deviation"]]


def verdict_table_deviation(tables: dict) -> tuple[str, str]:
    rows = tables["deviation"]
    ok = all(r["worst"] <= 1e-9 and r["violations"] == 0 for r in rows)
    return ("success" if ok else "warning"), ("Für δ = " + ", ".join(de(r["delta"], 2) for r in rows) + f" und alle Rundenzahlen von 1 bis {rows[0]['horizon']} gewinnt kein abweichender Spediteur "
            f"(größte Steigerung {max(r['worst'] for r in rows):.1e}); die Käufer-Antwort wurde durch Aufzählung aller späteren Kaufrunden bestimmt. "
            "Der Prüfer ist ein Gleichgewichts-Nachweis (Ein-Abweichungs-Prinzip), kein unabhängiges Lösen.")
