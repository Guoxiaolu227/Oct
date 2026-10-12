from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .artifact_manifest import write_artifact_manifest
from .config import load_config
from .errors import R3AgentError
from .models import AuditResult
from .orchestrator import run_review
from .provider import DeepSeekProvider
from .source_audit import verify_source_traceability
from .trace import load_events, summarize_events


PACKAGE_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONFIG = PACKAGE_ROOT / "configs" / "default.yaml"
SAFE_DETAIL_KEYS = {"phase", "resource", "assessment_status", "reason_count", "assessment_count", "finish_reason"}


def _review(args: argparse.Namespace) -> int:
    config = load_config(args.config)
    if args.no_verifier:
        config.execution.verifier_enabled = False
    provider = DeepSeekProvider(config.provider)
    result, run_dir = run_review(
        manuscript_path=args.input,
        config=config,
        provider=provider,
        condition=args.condition,
        paper_id=args.paper_id,
    )
    print(json.dumps({"review_run_id": result.review_run_id, "run_dir": str(run_dir), "status": result.run_status}, ensure_ascii=False))
    return 0


def _validate(args: argparse.Namespace) -> int:
    payload = json.loads(args.result.read_text(encoding="utf-8"))
    result = AuditResult.model_validate(payload)
    print(json.dumps({"status": "valid", "review_run_id": result.review_run_id, "assessments": len(result.assessments)}))
    return 0


def _summarize(args: argparse.Namespace) -> int:
    events = load_events(args.run_dir / "events.jsonl")
    summary = summarize_events(events)
    target = args.run_dir / "trace_summary.json"
    target.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(str(target))
    return 0


def _export(args: argparse.Namespace) -> int:
    events = load_events(args.run_dir / "events.jsonl")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8", newline="\n") as handle:
        for event in events:
            payload = event.model_dump(mode="json")
            payload["details"] = {
                key: value for key, value in event.details.items() if key in SAFE_DETAIL_KEYS
            }
            handle.write(json.dumps(payload, ensure_ascii=False) + "\n")
    print(json.dumps({"status": "exported", "events": len(events), "output": str(args.output)}))
    return 0


def _verify_sources(_: argparse.Namespace) -> int:
    report = verify_source_traceability(PACKAGE_ROOT)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["status"] == "ok" else 1


def _build_manifest(args: argparse.Namespace) -> int:
    target = write_artifact_manifest(PACKAGE_ROOT, args.output)
    payload = json.loads(target.read_text(encoding="utf-8"))
    print(
        json.dumps(
            {
                "status": "written",
                "output": str(target),
                "artifact_count": payload["artifact_count"],
                "root_digest": payload["root_digest"],
            }
        )
    )
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="R3 paper audit agent")
    subparsers = parser.add_subparsers(dest="command", required=True)

    review = subparsers.add_parser("review", help="Audit one UTF-8 MMD manuscript")
    review.add_argument("input", type=Path)
    review.add_argument("--condition", default="progressive")
    review.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    review.add_argument("--paper-id")
    review.add_argument("--no-verifier", action="store_true")
    review.set_defaults(handler=_review)

    validate = subparsers.add_parser("validate", help="Validate an audit result")
    validate.add_argument("result", type=Path)
    validate.set_defaults(handler=_validate)

    summarize = subparsers.add_parser("summarize-trace", help="Rebuild a trace summary")
    summarize.add_argument("run_dir", type=Path)
    summarize.set_defaults(handler=_summarize)

    export = subparsers.add_parser("export-telemetry", help="Export sanitized event telemetry")
    export.add_argument("run_dir", type=Path)
    export.add_argument("--output", type=Path, required=True)
    export.set_defaults(handler=_export)

    sources = subparsers.add_parser("verify-sources", help="Validate source and rule traceability")
    sources.set_defaults(handler=_verify_sources)

    manifest = subparsers.add_parser("build-manifest", help="Hash versioned research artifacts")
    manifest.add_argument("--output", type=Path)
    manifest.set_defaults(handler=_build_manifest)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return int(args.handler(args))
    except (R3AgentError, ValueError, OSError, json.JSONDecodeError) as exc:
        print(str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
