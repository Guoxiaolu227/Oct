from __future__ import annotations

import json
import os
import time
import uuid
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .models import SkillInvocationEvent, TokenUsage


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def new_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex}"


class TraceRecorder:
    def __init__(
        self,
        *,
        run_dir: Path,
        review_run_id: str,
        paper_id: str,
        paper_sha256: str,
        artifact_hashes: dict[str, str],
    ) -> None:
        self.run_dir = run_dir
        self.run_dir.mkdir(parents=True, exist_ok=False)
        self.review_run_id = review_run_id
        self.paper_id = paper_id
        self.paper_sha256 = paper_sha256
        self.artifact_hashes = artifact_hashes
        self.trace_id = new_id("trace")
        self.events_path = run_dir / "events.jsonl"
        self.events: list[SkillInvocationEvent] = []
        self.sequence = 0

    def emit(
        self,
        event_type: str,
        *,
        span_id: str,
        parent_span_id: str | None,
        skill_id: str | None = None,
        skill_version: str | None = None,
        mechanism_id: str | None = None,
        trigger_source: str = "system",
        artifact_hashes: dict[str, str] | None = None,
        model: str | None = None,
        attempt: int | None = None,
        tokens: TokenUsage | None = None,
        latency_ms: float | None = None,
        status: str = "ok",
        error_code: str | None = None,
        assessment_ids: list[str] | None = None,
        details: dict[str, Any] | None = None,
    ) -> SkillInvocationEvent:
        self.sequence += 1
        event = SkillInvocationEvent.model_validate(
            {
                "event_id": new_id("event"),
                "sequence": self.sequence,
                "timestamp": utc_now(),
                "review_run_id": self.review_run_id,
                "trace_id": self.trace_id,
                "span_id": span_id,
                "parent_span_id": parent_span_id,
                "event_type": event_type,
                "paper_id": self.paper_id,
                "paper_sha256": self.paper_sha256,
                "skill_id": skill_id,
                "skill_version": skill_version,
                "mechanism_id": mechanism_id,
                "trigger_source": trigger_source,
                "artifact_hashes": artifact_hashes or self.artifact_hashes,
                "model": model,
                "attempt": attempt,
                "tokens": tokens or TokenUsage(),
                "latency_ms": latency_ms,
                "status": status,
                "error_code": error_code,
                "assessment_ids": assessment_ids or [],
                "details": details or {},
            }
        )
        with self.events_path.open("a", encoding="utf-8", newline="\n") as handle:
            handle.write(event.model_dump_json() + "\n")
            handle.flush()
            os.fsync(handle.fileno())
        self.events.append(event)
        return event

    def write_private_json(self, category: str, item_id: str, payload: dict[str, Any]) -> Path:
        target_dir = self.run_dir / category
        target_dir.mkdir(parents=True, exist_ok=True)
        target = target_dir / f"{item_id}.json"
        target.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        return target

    def write_private_text(self, name: str, value: str) -> Path:
        target = self.run_dir / name
        target.write_text(value, encoding="utf-8")
        return target

    def summary(self) -> dict[str, Any]:
        return summarize_events(self.events)

    def write_summary(self) -> Path:
        target = self.run_dir / "trace_summary.json"
        target.write_text(json.dumps(self.summary(), ensure_ascii=False, indent=2), encoding="utf-8")
        return target


def load_events(path: Path) -> list[SkillInvocationEvent]:
    return [
        SkillInvocationEvent.model_validate_json(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def summarize_events(events: list[SkillInvocationEvent]) -> dict[str, Any]:
    if not events:
        raise ValueError("Cannot summarize an empty event stream")
    by_skill: dict[str, dict[str, Any]] = {}
    grouped: dict[str, list[SkillInvocationEvent]] = defaultdict(list)
    for event in events:
        if event.skill_id:
            grouped[event.skill_id].append(event)
    for skill_id, skill_events in sorted(grouped.items()):
        types = Counter(event.event_type for event in skill_events)
        statuses = Counter(
            str(event.details.get("assessment_status"))
            for event in skill_events
            if event.event_type == "assessment_emitted" and event.details.get("assessment_status")
        )
        resources = sorted(
            {
                str(event.details["resource"])
                for event in skill_events
                if event.event_type == "resource_loaded" and event.details.get("resource")
            }
        )
        by_skill[skill_id] = {
            "considered": types["skill_considered"],
            "invoked": types["skill_invoked"],
            "completed": types["skill_completed"],
            "skipped": types["skill_skipped"],
            "model_requests": types["model_request_started"],
            "model_failures": types["model_request_failed"],
            "input_tokens": sum(event.tokens.input or 0 for event in skill_events),
            "output_tokens": sum(event.tokens.output or 0 for event in skill_events),
            "total_tokens": sum(event.tokens.total or 0 for event in skill_events),
            "latency_ms": round(sum(event.latency_ms or 0 for event in skill_events), 3),
            "resources": resources,
            "assessment_statuses": dict(statuses),
            "finding_count": sum(
                statuses[name] for name in ("confirmed_flaw", "plausible_risk", "reporting_gap")
            ),
        }
    terminal = next(
        (event.event_type for event in reversed(events) if event.event_type in {"review_completed", "review_failed"}),
        None,
    )
    first = events[0]
    return {
        "schema_version": "trace-summary-0.1",
        "review_run_id": first.review_run_id,
        "paper_id": first.paper_id,
        "paper_sha256": first.paper_sha256,
        "trace_id": first.trace_id,
        "event_count": len(events),
        "run_status": "completed" if terminal == "review_completed" else "incomplete",
        "by_skill": by_skill,
    }


class Stopwatch:
    def __enter__(self) -> "Stopwatch":
        self.started = time.perf_counter_ns()
        return self

    def __exit__(self, *_: object) -> None:
        self.elapsed_ms = (time.perf_counter_ns() - self.started) / 1_000_000
