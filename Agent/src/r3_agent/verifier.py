from __future__ import annotations

import json
import uuid
from typing import Any

from .hashing import sha256_text
from .manuscript import Manuscript
from .models import Evidence, MechanismAssessment, Verification


ALLOWED_STATUSES = {
    "confirmed_flaw",
    "plausible_risk",
    "reporting_gap",
    "refuted",
    "not_applicable",
    "insufficient_evidence",
}
ALLOWED_MECHANISMS = {f"FM-R3-0{index}" for index in range(1, 6)}


def _as_string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item).strip() for item in value if str(item).strip()]


def _normalize_evidence(
    raw_items: Any,
    *,
    role: str,
    manuscript: Manuscript,
    reasons: list[str],
) -> list[Evidence]:
    if not isinstance(raw_items, list):
        reasons.append(f"{role} evidence must be an array")
        return []
    evidence: list[Evidence] = []
    for index, raw in enumerate(raw_items):
        if not isinstance(raw, dict):
            reasons.append(f"{role} evidence item {index} is not an object")
            continue
        try:
            quote = str(raw.get("quote", ""))
            start_line = int(raw.get("start_line"))
            end_line = int(raw.get("end_line"))
            verified = manuscript.verify_quote(quote, start_line, end_line)
        except (TypeError, ValueError) as exc:
            reasons.append(f"{role} evidence item {index}: {exc}")
            continue
        evidence_id = (
            f"{manuscript.paper_id}:{start_line}-{end_line}:"
            f"{sha256_text(quote)[:12]}"
        )
        evidence.append(
            Evidence(
                evidence_id=evidence_id,
                paper_sha256=manuscript.sha256,
                quote=verified.quote,
                start_line=verified.start_line,
                end_line=verified.end_line,
                char_start=verified.char_start,
                char_end=verified.char_end,
                role=role,
            )
        )
    return evidence


def normalize_assessment(
    raw: dict[str, Any],
    *,
    active_mechanism: str,
    manuscript: Manuscript,
) -> MechanismAssessment:
    reasons: list[str] = []
    raw_mechanisms = raw.get("mechanism_ids", [])
    mechanisms = []
    if isinstance(raw_mechanisms, list):
        mechanisms = [str(item) for item in raw_mechanisms if str(item) in ALLOWED_MECHANISMS]
    mechanisms = list(dict.fromkeys(mechanisms))
    if active_mechanism not in mechanisms:
        reasons.append("assessment omitted the active mechanism; it was restored")
        mechanisms.insert(0, active_mechanism)

    raw_status = str(raw.get("status", "insufficient_evidence"))
    status = raw_status if raw_status in ALLOWED_STATUSES else "insufficient_evidence"
    if status != raw_status:
        reasons.append(f"unsupported status {raw_status!r} was downgraded")

    missingness = str(raw.get("missingness_status", "not_missing"))
    if missingness not in {"not_missing", "suspected_missing", "verified_missing"}:
        missingness = "not_missing"
        reasons.append("invalid missingness status was reset")
    if missingness == "verified_missing":
        missingness = "suspected_missing"
        reasons.append("machine output cannot verify missingness")

    supporting = _normalize_evidence(
        raw.get("supporting_evidence", []),
        role="supporting",
        manuscript=manuscript,
        reasons=reasons,
    )
    counter = _normalize_evidence(
        raw.get("counterevidence", []),
        role="counterevidence",
        manuscript=manuscript,
        reasons=reasons,
    )
    causal_chain = _as_string_list(raw.get("causal_chain", []))
    claim = str(raw.get("claim_under_review", "")).strip()
    hypothesis = str(raw.get("hypothesis", "")).strip()
    if status in {"confirmed_flaw", "plausible_risk", "reporting_gap"} and (
        not claim or not hypothesis or not supporting or not causal_chain
    ):
        status = "insufficient_evidence"
        reasons.append(
            "finding lacked a bound claim, falsifiable hypothesis, verified evidence, or causal chain"
        )
    if status == "reporting_gap" and missingness != "suspected_missing":
        missingness = "suspected_missing"
        reasons.append("reporting_gap was normalized to suspected_missing")
    if status != "reporting_gap" and missingness == "suspected_missing" and not raw.get("missing_information"):
        reasons.append("suspected_missing has no named missing information")

    return MechanismAssessment(
        assessment_id=f"assessment_{uuid.uuid4().hex}",
        mechanism_ids=mechanisms,
        status=status,
        claim_under_review=claim,
        hypothesis=hypothesis,
        causal_chain=causal_chain,
        supporting_evidence=supporting,
        counterevidence=counter,
        missing_information=_as_string_list(raw.get("missing_information", [])),
        missingness_status=missingness,
        resolution_needed=_as_string_list(raw.get("resolution_needed", [])),
        severity=None,
        verification=Verification(
            deterministic_valid=not reasons,
            model_verdict="not_run",
            reasons=reasons,
        ),
    )


def empty_assessment(active_mechanism: str, reason: str) -> MechanismAssessment:
    return MechanismAssessment(
        assessment_id=f"assessment_{uuid.uuid4().hex}",
        mechanism_ids=[active_mechanism],
        status="insufficient_evidence",
        claim_under_review="",
        hypothesis="No schema-valid assessment was returned.",
        causal_chain=[],
        supporting_evidence=[],
        counterevidence=[],
        missing_information=[],
        missingness_status="not_missing",
        resolution_needed=[reason],
        severity=None,
        verification=Verification(
            deterministic_valid=False,
            model_verdict="not_run",
            reasons=[reason],
        ),
    )


def apply_model_verdict(assessment: MechanismAssessment, verdict: dict[str, Any]) -> MechanismAssessment:
    value = str(verdict.get("verdict", "reject"))
    if value not in {"accept", "downgrade", "reject"}:
        value = "reject"
    recommended = str(verdict.get("recommended_status", assessment.status))
    reasons = _as_string_list(verdict.get("reasons", []))
    handling = str(verdict.get("counterevidence_handling", "")).strip()
    if handling:
        reasons.append(f"counterevidence: {handling}")

    status = assessment.status
    if value == "reject":
        status = "insufficient_evidence"
    elif value == "downgrade":
        if recommended in ALLOWED_STATUSES and recommended != "confirmed_flaw":
            status = recommended
        else:
            status = "insufficient_evidence"
            reasons.append("invalid or promoting verifier recommendation was ignored")
    elif assessment.status != "confirmed_flaw" and recommended == "confirmed_flaw":
        reasons.append("verifier promotion to confirmed_flaw was ignored")

    payload = assessment.model_dump()
    payload["status"] = status
    payload["verification"] = {
        "deterministic_valid": assessment.verification.deterministic_valid,
        "model_verdict": value,
        "reasons": assessment.verification.reasons + reasons,
    }
    if status == "reporting_gap":
        payload["missingness_status"] = "suspected_missing"
    return MechanismAssessment.model_validate(payload)


def assessment_json(assessment: MechanismAssessment) -> str:
    return json.dumps(assessment.model_dump(mode="json"), ensure_ascii=False, indent=2)
