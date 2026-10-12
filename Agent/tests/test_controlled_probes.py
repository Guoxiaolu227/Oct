from __future__ import annotations

import json
from pathlib import Path

import pytest

from r3_agent.manuscript import Manuscript
from r3_agent.verifier import normalize_assessment


ROOT = Path(__file__).resolve().parents[1]
PROBES = [
    json.loads(line)
    for line in (ROOT / "probes" / "controlled_probes.jsonl").read_text(encoding="utf-8").splitlines()
    if line.strip()
]


@pytest.mark.parametrize("probe", PROBES, ids=[item["probe_id"] for item in PROBES])
def test_controlled_probe_statuses(probe: dict, tmp_path: Path) -> None:
    path = tmp_path / f"{probe['probe_id']}.mmd"
    path.write_text(probe["mmd"], encoding="utf-8")
    manuscript = Manuscript.load(path, allowed_extensions=[".mmd"], max_characters=10000)

    assessment = normalize_assessment(
        probe["model_assessment"],
        active_mechanism=probe["mechanism_id"],
        manuscript=manuscript,
    )

    assert assessment.status == probe["expected_status"]
    assert probe["mechanism_id"] in assessment.mechanism_ids
    if probe["category"] == "invalid_evidence":
        assert not assessment.verification.deterministic_valid
        assert assessment.supporting_evidence == []


def test_probe_inventory_has_required_coverage() -> None:
    core = {f"FM-R3-0{index}" for index in range(1, 6)}
    for mechanism in core:
        categories = {item["category"] for item in PROBES if item["mechanism_id"] == mechanism}
        assert {"confirmed", "refuted", "reporting_gap"} <= categories
    assert len(PROBES) >= 20
    assert sum(item["category"] not in {"confirmed", "refuted", "reporting_gap"} for item in PROBES) >= 5
