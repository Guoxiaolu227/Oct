from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


MechanismId = Literal["FM-R3-01", "FM-R3-02", "FM-R3-03", "FM-R3-04", "FM-R3-05"]
AssessmentStatus = Literal[
    "confirmed_flaw",
    "plausible_risk",
    "reporting_gap",
    "refuted",
    "not_applicable",
    "insufficient_evidence",
]
MissingnessStatus = Literal["not_missing", "suspected_missing", "verified_missing"]
EventType = Literal[
    "review_started",
    "skill_considered",
    "skill_invoked",
    "resource_loaded",
    "model_request_started",
    "model_request_completed",
    "model_request_failed",
    "skill_completed",
    "skill_skipped",
    "assessment_emitted",
    "assessment_verified",
    "assessment_rejected",
    "review_completed",
    "review_failed",
]


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Evidence(StrictModel):
    evidence_id: str
    paper_sha256: str = Field(pattern=r"^[a-f0-9]{64}$")
    quote: str = Field(min_length=1)
    start_line: int = Field(ge=1)
    end_line: int = Field(ge=1)
    char_start: int = Field(ge=0)
    char_end: int = Field(ge=1)
    role: Literal["supporting", "counterevidence"]

    @model_validator(mode="after")
    def validate_ranges(self) -> "Evidence":
        if self.end_line < self.start_line:
            raise ValueError("end_line must not precede start_line")
        if self.char_end <= self.char_start:
            raise ValueError("char_end must be greater than char_start")
        return self


class Verification(StrictModel):
    deterministic_valid: bool
    model_verdict: Literal["not_run", "accept", "downgrade", "reject"] = "not_run"
    reasons: list[str] = Field(default_factory=list)


class MechanismAssessment(StrictModel):
    assessment_id: str
    mechanism_ids: list[MechanismId] = Field(min_length=1)
    status: AssessmentStatus
    claim_under_review: str
    hypothesis: str
    causal_chain: list[str]
    supporting_evidence: list[Evidence]
    counterevidence: list[Evidence]
    missing_information: list[str]
    missingness_status: MissingnessStatus
    resolution_needed: list[str]
    severity: None = None
    verification: Verification

    @model_validator(mode="after")
    def validate_semantics(self) -> "MechanismAssessment":
        if len(self.mechanism_ids) != len(set(self.mechanism_ids)):
            raise ValueError("mechanism_ids must be unique")
        if self.missingness_status == "verified_missing":
            raise ValueError("machine assessments cannot verify missingness")
        if self.status in {"confirmed_flaw", "plausible_risk", "reporting_gap"}:
            if not self.claim_under_review.strip():
                raise ValueError("a finding requires a claim under review")
            if not self.hypothesis.strip():
                raise ValueError("a finding requires a falsifiable hypothesis")
            if not self.supporting_evidence:
                raise ValueError("a finding requires supporting evidence")
            if not self.causal_chain:
                raise ValueError("a finding requires a causal chain")
        if self.status == "reporting_gap" and self.missingness_status != "suspected_missing":
            raise ValueError("reporting_gap requires suspected_missing")
        return self


class TokenUsage(StrictModel):
    input: int | None = None
    output: int | None = None
    total: int | None = None
    cached: int | None = None


class SkillInvocationEvent(StrictModel):
    schema_version: Literal["skill-event-0.1"] = "skill-event-0.1"
    event_id: str
    sequence: int = Field(ge=1)
    timestamp: datetime
    review_run_id: str
    trace_id: str
    span_id: str
    parent_span_id: str | None
    event_type: EventType
    paper_id: str
    paper_sha256: str = Field(pattern=r"^[a-f0-9]{64}$")
    skill_id: str | None
    skill_version: str | None
    mechanism_id: MechanismId | None
    trigger_source: Literal["orchestrator_fixed", "router_selected", "user_explicit", "system"]
    artifact_hashes: dict[str, str]
    model: str | None
    attempt: int | None = Field(default=None, ge=0)
    tokens: TokenUsage = Field(default_factory=TokenUsage)
    latency_ms: float | None = Field(default=None, ge=0)
    status: str
    error_code: str | None
    assessment_ids: list[str] = Field(default_factory=list)
    details: dict[str, Any] = Field(default_factory=dict)


class AuditResult(StrictModel):
    schema_version: Literal["audit-result-0.1"] = "audit-result-0.1"
    review_run_id: str
    paper_id: str
    paper_sha256: str = Field(pattern=r"^[a-f0-9]{64}$")
    condition: str
    rubric_version: str
    started_at: datetime
    completed_at: datetime | None
    artifact_hashes: dict[str, str]
    assessments: list[MechanismAssessment]
    run_status: Literal["completed", "incomplete", "failed"]
    run_stats: dict[str, Any]
