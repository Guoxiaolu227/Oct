from pathlib import Path

from r3_agent.skills import load_skills
from r3_agent.source_audit import verify_source_traceability


ROOT = Path(__file__).resolve().parents[1]


def test_all_skill_rules_have_source_edges() -> None:
    report = verify_source_traceability(ROOT)
    assert report["status"] == "ok"
    assert report["skill_rule_count"] == 20
    assert report["source_count"] >= 15


def test_registry_loads_exactly_five_skills() -> None:
    skills = load_skills(ROOT / "rubrics" / "r3_profile.yaml", ROOT / "skills")
    assert len(skills) == 5
    assert {skill.mechanism_id for skill in skills} == {f"FM-R3-0{index}" for index in range(1, 6)}
    assert all(skill.artifact_hashes for skill in skills)
