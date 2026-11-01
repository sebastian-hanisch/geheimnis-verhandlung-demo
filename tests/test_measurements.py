"""Vorgerechnete Messreihen (data/tables.json): gehören zum aktuellen Rechencode, sind in sich stimmig, und eine Probe wird neu gerechnet."""

import json

import pytest

import gvh_experiments as XP


@pytest.fixture(scope="module")
def tables():
    t = XP.load_tables()
    assert t is not None, "data/tables.json fehlt oder gehört zu einem anderen Rechencode: python tools/make_grid.py"
    return t


def test_the_file_belongs_to_the_current_generator(tables):
    assert json.loads(XP.TABLES_FILE.read_text(encoding="utf-8"))["generator_hash"] == XP.tables_hash()
    assert tables["seeds"] == list(XP.TABLE_SEEDS) == [11, 22, 33, 44]


def test_a_stale_hash_is_refused(tmp_path, monkeypatch):
    payload = json.loads(XP.TABLES_FILE.read_text(encoding="utf-8"))
    payload["generator_hash"] = "0" * 16
    fake = tmp_path / "tables.json"
    fake.write_text(json.dumps(payload), encoding="utf-8")
    monkeypatch.setattr(XP, "TABLES_FILE", fake)
    assert XP.load_tables() is None


def test_a_missing_file_gives_no_tables(tmp_path, monkeypatch):
    monkeypatch.setattr(XP, "TABLES_FILE", tmp_path / "gibt_es_nicht.json")
    assert XP.load_tables() is None


def test_counts_are_consistent(tables):
    for mode in XP.MODES:
        sm = tables["validity"][mode]["summary"]
        assert sm["total"] == sm["both_valid"] + sm["both_invalid"] + sm["criterion_only"] + sm["numeric_only"] == sum(len(b["rows"]) for b in tables["validity"][mode]["blocks"])
        assert len(sm["mismatches"]) == sm["criterion_only"] + sm["numeric_only"]
        assert [b["seed"] for b in tables["validity"][mode]["blocks"]] == list(XP.TABLE_SEEDS)
        assert sm["both_valid"] > 0 and sm["both_invalid"] > 0               # beide Zweige kommen vor
    assert [r["delta"] for r in tables["deviation"]] == list(XP.DEV_DELTAS)


def test_probe_validity_block_is_recomputed_identically(tables):
    block = XP.job_validity(11, "half", count=6)
    stored = tables["validity"]["half"]["blocks"][0]["rows"][:6]
    assert [r["inst"] for r in block["rows"]] == [r["inst"] for r in stored]
    assert [r["criterion"] for r in block["rows"]] == [r["criterion"] for r in stored]
    assert [r["gap"] for r in block["rows"]] == pytest.approx([r["gap"] for r in stored], rel=1e-12, abs=1e-15)


def test_probe_random_kappa_block_uses_other_kappas(tables):
    block = XP.job_validity(22, "random", count=6)
    kappas = {r["inst"][4] for r in block["rows"]}
    assert len(kappas) > 1 and all(0.1 <= k <= 0.9 for k in kappas)


def test_probe_deviation_block_is_recomputed_identically(tables):
    res = XP.job_deviation(0.5)
    stored = next(r for r in tables["deviation"] if r["delta"] == 0.5)
    assert res["worst"] == pytest.approx(stored["worst"], abs=1e-12) and res["violations"] == stored["violations"] == 0


def test_instances_are_reproducible_and_independent_of_python_hash():
    assert XP.instances(11, "half", 10) == XP.instances(11, "half", 10)
    assert XP.instances(11, "half", 10) != XP.instances(22, "half", 10)
    assert XP.instances(11, "half", 10) != XP.instances(11, "random", 10)
