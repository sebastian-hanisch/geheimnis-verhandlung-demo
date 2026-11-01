"""Vorgerechnete Messreihen (data/tables.json) mit Erzeuger-Hash und die Zählungen dahinter.

Zwei Reihen: (1) das Gültigkeitskriterium des linearen Gleichgewichts gegen die numerische Beste-Antwort-Lücke an Zufallsinstanzen (vier Zufalls-Seeds mal 50, SplitMix64, kein Python-hash;
einmal für kappa = 1/2, einmal für zufälliges kappa), (2) der Abweichungsprüfer der Coase-Rekursion bis T = 200 für drei Diskontfaktoren.
Aufträge sind kleine, einzeln und in beliebiger Reihenfolge berechenbare Blöcke; `tools/make_grid.py` verteilt sie auf Prozesse und setzt sie zusammen.
Ändert sich eine der Quelldateien in TABLE_SOURCES, stimmt der Hash nicht mehr: die App zeigt die Reihen dann nicht, `tests/test_measurements.py` schlägt an."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np

import gvh_coase as CO
import gvh_double_auction as DA
from gvh_rng import SplitMix64

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
TABLES_FILE = DATA / "tables.json"
TABLE_SOURCES = ("gvh_double_auction.py", "gvh_coase.py", "gvh_rng.py", "gvh_experiments.py")
TABLE_SEEDS = (11, 22, 33, 44)                            # Zufalls-Seeds der vorgerechneten Zufallsinstanzen
N_RANDOM = 50                                             # Zufallsinstanzen je Zufalls-Seed und Modus
MIN_RANGE = 0.05                                          # Instanzen mit L <= 0,05 (normiert) werden verworfen

GRID_TYPES, GRID_POINTS, GAP_VALID = 41, 8001, 1e-7      # Gitter der vorgerechneten Reihe (feiner als in der App); Lücke unter GAP_VALID zählt als null
DEV_DELTAS = (0.5, 0.9, 0.99)
DEV_HORIZON = 200
DEV_PRICES = 40_001
MODES = ("half", "random")                                # kappa = 1/2 bzw. zufälliges kappa in [0,1; 0,9]


def tables_hash() -> str:
    h = hashlib.sha256()
    for name in TABLE_SOURCES:
        text = (ROOT / name).read_text(encoding="utf-8").replace("\r\n", "\n")
        h.update(name.encode() + b"\0" + text.encode("utf-8") + b"\0")
    return h.hexdigest()[:16]


def load_tables():
    """Die vorgerechneten Reihen, oder None, wenn die Datei fehlt oder zu einem anderen Rechencode gehört."""
    if not TABLES_FILE.exists():
        return None
    try:
        payload = json.loads(TABLES_FILE.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    return payload if payload.get("generator_hash") == tables_hash() else None


def write_json(path: Path, payload: dict):
    path.parent.mkdir(exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=1, sort_keys=True) + "\n", encoding="utf-8")


# --- Zufallsinstanzen ------------------------------------------------------------------------------------------------------------------------------
def random_instance(rng: SplitMix64, mode: str) -> tuple[float, float, float, float, float]:
    """(v0, v1, c0, c1, kappa), normiert auf Größenordnung 1: v0 in [0, 1), Breite 0,2 bis 2; c0 in [-0,5, 1), Breite 0,2 bis 2; kappa = 1/2 oder in [0,1; 0,9]."""
    v0 = rng.uniform()
    v1 = v0 + 0.2 + 1.8 * rng.uniform()
    c0 = -0.5 + 1.5 * rng.uniform()
    c1 = c0 + 0.2 + 1.8 * rng.uniform()
    kappa = 0.1 + 0.8 * rng.uniform() if mode == "random" else 0.5
    return v0, v1, c0, c1, kappa


def instances(seed: int, mode: str, count: int = N_RANDOM) -> list[tuple[float, float, float, float, float]]:
    """Die ersten `count` Zufallsinstanzen des Stroms SplitMix64(seed + Modus), ohne die verworfenen (L <= 0,05)."""
    rng = SplitMix64(seed * 10 + (0 if mode == "half" else 1))
    out = []
    for _ in range(count):
        inst = random_instance(rng, mode)
        if inst[1] - inst[2] > MIN_RANGE:
            out.append(inst)
    return out


def job_validity(seed: int, mode: str, count: int = N_RANDOM) -> dict:
    """Je Instanz: Urteil des Kriteriums, größte Lücke am reinen Gitter, bei kappa = 1/2 in gültigen Fällen die relative Abweichung Gleichgewicht gegen Zweitbestes."""
    rows = []
    for v0, v1, c0, c1, kappa in instances(seed, mode, count):
        val = DA.cs_validity(v0, v1, c0, c1, kappa, tol=1e-12)
        gs, gb = DA.best_response_gap(v0, v1, c0, c1, kappa, ntypes=GRID_TYPES, ngrid=GRID_POINTS, corners=False)
        rel = None
        if val.valid and mode == "half":
            _p, cg = DA.cs_stats(v0, v1, c0, c1, kappa)
            _sp, sg, _th = DA.second_best_stats(v0, v1, c0, c1)
            rel = abs(cg - sg) / sg
        rows.append({"inst": [v0, v1, c0, c1, kappa], "criterion": bool(val.valid), "gap": max(gs, gb), "rel_dev": rel})
    return {"seed": seed, "mode": mode, "rows": rows}


def job_deviation(delta: float, horizon: int = DEV_HORIZON) -> dict:
    """Abweichungsprüfer (siehe tests/test_oracle_coase.py): größte Gewinnsteigerung und Zahl der Skimming-Verletzungen für T = 1..horizon."""
    par = CO.coase_params(delta, horizon)
    prices = np.linspace(1e-5, 1.0, DEV_PRICES)
    worst = -np.inf
    violations = 0
    for t in range(1, horizon + 1):
        if t == 1:
            worst = max(worst, float((prices * (1 - prices)).max() - par.k[1]))
            continue
        kappa, x, kappa_next = 0.0, 1.0, None
        for s in range(1, t):
            left = t - s
            q = par.pi[left] * x
            kappa = max(kappa, delta ** s * (1 - q))
            if s == 1:
                kappa_next = delta * (1 - q)
            x = par.w[left] * x
        if abs(kappa - kappa_next) > 1e-12:
            violations += 1
        w = np.minimum(prices / (1 - kappa), 1.0)
        worst = max(worst, float((prices * (1 - w) + delta * par.k[t - 1] * w * w).max() - par.k[t]))
    return {"delta": delta, "horizon": horizon, "worst": worst, "violations": violations}


def jobs() -> list[tuple]:
    return [("validity", seed, mode) for seed in TABLE_SEEDS for mode in MODES] + [("deviation", d) for d in DEV_DELTAS]


def run_job(job: tuple):
    if job[0] == "validity":
        return job, job_validity(job[1], job[2])
    return job, job_deviation(job[1])


def summarise_validity(blocks: list[dict]) -> dict:
    """Zählung über die Seeds: Kriterium ja/nein gegen numerisch gültig/ungültig (Lücke < GAP_VALID), Abweichungen mit den Instanzen, größte Abweichung Gleichgewicht/Zweitbestes."""
    tp = tn = fp = fn = 0
    mismatches = []
    rel_max = 0.0
    valid_n = 0
    for block in blocks:
        for row in block["rows"]:
            numeric = row["gap"] < GAP_VALID
            crit = row["criterion"]
            if crit and numeric:
                tp += 1
            elif not crit and not numeric:
                tn += 1
            elif crit:
                fp += 1
                mismatches.append(row)
            else:
                fn += 1
                mismatches.append(row)
            if crit and row["rel_dev"] is not None:
                valid_n += 1
                rel_max = max(rel_max, row["rel_dev"])
    return {"total": tp + tn + fp + fn, "both_valid": tp, "both_invalid": tn, "criterion_only": fp, "numeric_only": fn, "mismatches": mismatches,
            "valid_with_second_best": valid_n, "rel_dev_max": rel_max}


def assemble_payload(results: dict) -> dict:
    payload: dict = {"generator_hash": tables_hash(), "seeds": list(TABLE_SEEDS), "validity": {}, "deviation": []}
    for mode in MODES:
        blocks = [results[("validity", seed, mode)] for seed in TABLE_SEEDS]
        payload["validity"][mode] = {"blocks": blocks, "summary": summarise_validity(blocks)}
    payload["deviation"] = [results[("deviation", d)] for d in DEV_DELTAS]
    return payload
