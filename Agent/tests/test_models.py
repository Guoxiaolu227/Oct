import pytest
from pathlib import Path
from pydantic import ValidationError

from r3_agent.models import MechanismAssessment, SkillInvocationEvent, Verification


ROOT = Path(__file__).resolve().parents[1]


def _assessment(**overrides):
    payload = {
        "assessment_id": "a1",
        "mechanism_ids": ["FM-R3-01"],
        "status": "reporting_gap",
        "claim_under_review": "Claim",
        "hypothesis": "Protocol is missing.",
        "causal_chain": ["Missing protocol", "Cannot adjudicate"],
        "supporting_evidence": [],
        "counterevidence": [],
        "missing_information": ["Split order"],
        "missingness_status": "suspected_missing",
        "resolution_needed": ["Split order"],
        "severity": None,
        "verification": Verification(deterministic_valid=True),
    }
    payload.update(overrides)
    return payload


def test_machine_cannot_emit_verified_missing() -> None:
    with pytest.raises(ValidationError, match="cannot verify missingness"):
        MechanismAssessment.model_validate(_assessment(missingness_status="verified_missing"))


def test_confirmed_flaw_requires_evidence() -> None:
    with pytest.raises(ValidationError, match="finding requires supporting evidence"):
        MechanismAssessment.model_validate(_assessment(status="confirmed_flaw", missingness_status="not_missing"))


def test_finding_requires_a_bound_claim() -> None:
    with pytest.raises(ValidationError, match="claim under review"):
        MechanismAssessment.model_validate(_assessment(claim_under_review=""))


def test_sanitized_telemetry_example_is_schema_valid_and_contains_no_raw_fields() -> None:
    line = (ROOT / "examples" / "sanitized_telemetry.jsonl").read_text(encoding="utf-8").strip()
    event = SkillInvocationEvent.model_validate_json(line)

    assert event.event_type == "assessment_verified"
    assert not ({"quote", "prompt", "content", "manuscript"} & set(event.details))
