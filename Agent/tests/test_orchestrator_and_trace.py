from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

import r3_agent.orchestrator as orchestrator_module
from r3_agent.cli import main
from r3_agent.config import load_config
from r3_agent.errors import ProviderError, RequestBudgetExceededError
from r3_agent.models import TokenUsage
from r3_agent.orchestrator import _deduplicate, run_review
from r3_agent.provider import ModelResponse
from r3_agent.trace import load_events, summarize_events
from r3_agent.verifier import normalize_assessment
from r3_agent.manuscript import Manuscript


ROOT = Path(__file__).resolve().parents[1]


class FakeProvider:
    def __init__(self) -> None:
        self.calls = 0

    def complete(self, *, system: str, user: str) -> ModelResponse:
        self.calls += 1
        if "PROPOSED ASSESSMENT" in user:
            content = json.dumps(
                {
                    "verdict": "accept",
                    "recommended_status": "not_applicable",
                    "reasons": ["The status is appropriately bounded."],
                    "counterevidence_handling": "No contrary evidence is required for non-applicability.",
                }
            )
        else:
            match = re.search(r"FM-R3-0[1-5]", user)
            assert match
            mechanism = match.group(0)
            content = json.dumps(
                {
                    "assessments": [
                        {
                            "mechanism_ids": [mechanism],
                            "status": "not_applicable",
                            "claim_under_review": "No applicable claim.",
                            "hypothesis": "The mechanism is not applicable to this synthetic note.",
                            "causal_chain": [],
                            "supporting_evidence": [],
                            "counterevidence": [],
                            "missing_information": [],
                            "missingness_status": "not_missing",
                            "resolution_needed": [],
                            "severity": None,
                        }
                    ]
                }
            )
        return ModelResponse(
            content=content,
            returned_model="fake-model-v1",
            finish_reason="stop",
            usage=TokenUsage(input=100, output=20, total=120, cached=0),
        )


class FailOnceProvider:
    def __init__(self) -> None:
        self.attempts = 0
        self.delegate = FakeProvider()

    def complete(self, *, system: str, user: str) -> ModelResponse:
        self.attempts += 1
        if self.attempts == 1:
            raise ProviderError("synthetic transient failure")
        return self.delegate.complete(system=system, user=user)


def test_end_to_end_review_tracks_every_skill_and_isolates_raw_text(tmp_path: Path) -> None:
    manuscript = tmp_path / "synthetic.mmd"
    secret_sentence = "PRIVATE MANUSCRIPT SENTENCE"
    manuscript.write_text(f"# Note\n{secret_sentence}\nNo empirical claims are made.", encoding="utf-8")
    config = load_config(ROOT / "configs" / "default.yaml")
    config.paths.private_runs = str(tmp_path / "runs")
    provider = FakeProvider()

    result, run_dir = run_review(manuscript_path=manuscript, config=config, provider=provider)

    assert result.run_status == "completed"
    assert len(result.assessments) == 5
    assert provider.calls == 10
    events = load_events(run_dir / "events.jsonl")
    summary = summarize_events(events)
    assert summary["run_status"] == "completed"
    assert len(summary["by_skill"]) == 5
    for skill_summary in summary["by_skill"].values():
        assert skill_summary["considered"] == 1
        assert skill_summary["invoked"] == 1
        assert skill_summary["completed"] == 1
        assert skill_summary["model_requests"] == 2
        assert len(skill_summary["resources"]) == 3

    telemetry = (run_dir / "events.jsonl").read_text(encoding="utf-8")
    assert secret_sentence not in telemetry
    assert secret_sentence in (run_dir / "manuscript.mmd").read_text(encoding="utf-8")

    export = tmp_path / "exported.jsonl"
    assert main(["export-telemetry", str(run_dir), "--output", str(export)]) == 0
    assert secret_sentence not in export.read_text(encoding="utf-8")
    assert main(["validate", str(run_dir / "audit_result.json")]) == 0


def test_non_progressive_conditions_are_not_silently_executed(tmp_path: Path) -> None:
    manuscript = tmp_path / "synthetic.mmd"
    manuscript.write_text("# Note", encoding="utf-8")
    config = load_config(ROOT / "configs" / "default.yaml")
    config.paths.private_runs = str(tmp_path / "runs")

    try:
        run_review(
            manuscript_path=manuscript,
            config=config,
            provider=FakeProvider(),
            condition="all_skills",
        )
    except ValueError as exc:
        assert "Only the progressive condition" in str(exc)
    else:
        raise AssertionError("reserved experimental condition executed unexpectedly")


def test_only_coorigin_findings_are_merged_across_mechanisms(tmp_path: Path) -> None:
    manuscript_path = tmp_path / "overlap.mmd"
    manuscript_path.write_text(
        "# Split\nEvents from each user occur in both train and test sets.",
        encoding="utf-8",
    )
    manuscript = Manuscript.load(
        manuscript_path,
        allowed_extensions=[".mmd"],
        max_characters=1000,
    )
    raw = {
        "mechanism_ids": [],
        "status": "confirmed_flaw",
        "claim_under_review": "Generalization to unseen users.",
        "hypothesis": "User overlap invalidates the generalization claim.",
        "causal_chain": ["Users cross splits", "Identity signals transfer"],
        "supporting_evidence": [
            {
                "quote": "Events from each user occur in both train and test sets.",
                "start_line": 2,
                "end_line": 2,
            }
        ],
        "counterevidence": [],
        "missing_information": [],
        "missingness_status": "not_missing",
        "resolution_needed": [],
        "severity": None,
    }
    leakage = normalize_assessment(raw, active_mechanism="FM-R3-01", manuscript=manuscript)
    split = normalize_assessment(raw, active_mechanism="FM-R3-02", manuscript=manuscript)

    merged = _deduplicate([leakage, split])

    assert len(merged) == 1
    assert merged[0].mechanism_ids == ["FM-R3-01", "FM-R3-02"]

    distinct_payload = {**raw, "hypothesis": "The population sampling frame is biased."}
    distinct = normalize_assessment(
        distinct_payload,
        active_mechanism="FM-R3-02",
        manuscript=manuscript,
    )
    assert len(_deduplicate([leakage, distinct])) == 2


def test_transient_provider_failure_is_retried_and_traced(tmp_path: Path) -> None:
    manuscript = tmp_path / "synthetic.mmd"
    manuscript.write_text("# Note\nNo empirical claims are made.", encoding="utf-8")
    config = load_config(ROOT / "configs" / "default.yaml")
    config.paths.private_runs = str(tmp_path / "runs")
    config.provider.max_retries = 1
    config.execution.retry_backoff_seconds = 0
    provider = FailOnceProvider()

    result, run_dir = run_review(manuscript_path=manuscript, config=config, provider=provider)
    events = load_events(run_dir / "events.jsonl")

    assert result.run_status == "completed"
    assert provider.attempts == 11
    failures = [event for event in events if event.event_type == "model_request_failed"]
    assert len(failures) == 1
    assert failures[0].attempt == 0
    assert any(
        event.event_type == "model_request_completed" and event.attempt == 1
        for event in events
    )


def test_unexpected_interruption_is_recorded_as_incomplete(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    manuscript = tmp_path / "synthetic.mmd"
    manuscript.write_text("# Note", encoding="utf-8")
    config = load_config(ROOT / "configs" / "default.yaml")
    config.paths.private_runs = str(tmp_path / "runs")

    def fail_to_load(*_: object, **__: object) -> list[object]:
        raise RuntimeError("synthetic artifact failure")

    monkeypatch.setattr(orchestrator_module, "load_skills", fail_to_load)
    with pytest.raises(RuntimeError, match="synthetic artifact failure"):
        run_review(manuscript_path=manuscript, config=config, provider=FakeProvider())

    run_dirs = list((tmp_path / "runs").iterdir())
    assert len(run_dirs) == 1
    events = load_events(run_dirs[0] / "events.jsonl")
    assert events[-1].event_type == "review_failed"
    summary = json.loads((run_dirs[0] / "trace_summary.json").read_text(encoding="utf-8"))
    assert summary["run_status"] == "incomplete"


def test_request_budget_stops_before_an_extra_model_call(tmp_path: Path) -> None:
    manuscript = tmp_path / "synthetic.mmd"
    manuscript.write_text("# Note\nNo empirical claims are made.", encoding="utf-8")
    config = load_config(ROOT / "configs" / "default.yaml")
    config.paths.private_runs = str(tmp_path / "runs")
    config.execution.max_model_requests_per_run = 1
    provider = FakeProvider()

    with pytest.raises(RequestBudgetExceededError, match="request_budget_exceeded"):
        run_review(manuscript_path=manuscript, config=config, provider=provider)

    run_dir = next((tmp_path / "runs").iterdir())
    events = load_events(run_dir / "events.jsonl")
    started = [event for event in events if event.event_type == "model_request_started"]
    assert provider.calls == 1
    assert len(started) == 1
    assert events[-1].event_type == "review_failed"
    assert events[-1].error_code == "request_budget_exceeded"
    summary = json.loads((run_dir / "trace_summary.json").read_text(encoding="utf-8"))
    assert summary["run_status"] == "incomplete"
