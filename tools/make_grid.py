"""Rechnet die Messreihen (Gültigkeitskriterium an Zufallsinstanzen, Abweichungsprüfer der Coase-Rekursion) neu und schreibt data/tables.json samt Erzeuger-Hash.

Aufruf (im Demo-Ordner, mit dem Test-venv):  python tools/make_grid.py [--workers 4]
Ändert sich eine Quelldatei aus gvh_experiments.TABLE_SOURCES, stimmt der Hash nicht mehr (tests/test_measurements.py schlägt an, die App zeigt die Reihen dann nicht);
danach diesen Aufruf wiederholen. Die Zufallsströme hängen nur an (Zufalls-Seed, Modus): die Reihen sind bei gleichem Code Zahl für Zahl dieselben, auch bei anderer Zahl von Prozessen."""

import argparse
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import gvh_experiments as XP  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=4)
    args = ap.parse_args()
    start = time.time()
    jobs = XP.jobs()
    results = {}
    with ProcessPoolExecutor(max_workers=min(args.workers, 4)) as ex:
        for job, res in ex.map(XP.run_job, jobs, chunksize=1):
            results[job] = res
    XP.write_json(XP.TABLES_FILE, XP.assemble_payload(results))
    print(f"geschrieben: {XP.TABLES_FILE}  ({time.time() - start:.0f} s, Hash {XP.tables_hash()}, {len(jobs)} Aufträge)")


if __name__ == "__main__":
    main()
