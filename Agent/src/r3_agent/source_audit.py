from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml


def verify_source_traceability(root: Path) -> dict[str, Any]:
    provenance = root / "provenance"
    registry = yaml.safe_load((provenance / "source_registry.yaml").read_text(encoding="utf-8"))
    sources = {item["source_id"]: item for item in registry.get("sources", [])}
    edges = [
        json.loads(line)
        for line in (provenance / "traceability_edges.jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    rule_ids: set[str] = set()
    for path in (root / "skills").glob("*/references/decision-rules.yaml"):
        payload = yaml.safe_load(path.read_text(encoding="utf-8"))
        rule_ids.update(item["rule_id"] for item in payload.get("rules", []))

    errors: list[str] = []
    edge_rule_ids: set[str] = set()
    for edge in edges:
        missing = [
            key
            for key in (
                "rule_id",
                "mechanism_id",
                "source_id",
                "source_locator",
                "short_excerpt",
                "mapping_rationale",
                "relation_strength",
                "verification_status",
            )
            if not edge.get(key)
        ]
        if missing:
            errors.append(f"edge {edge.get('rule_id', '<unknown>')} missing {missing}")
        if edge.get("source_id") not in sources:
            errors.append(f"unknown source_id: {edge.get('source_id')}")
        if edge.get("relation_strength") not in {"direct", "supporting", "contextual"}:
            errors.append(f"invalid relation strength: {edge.get('rule_id')}")
        edge_rule_ids.add(str(edge.get("rule_id")))
    missing_edges = sorted(rule_ids - edge_rule_ids)
    if missing_edges:
        errors.append(f"rules without traceability edges: {missing_edges}")
    unverified = sum(
        edge.get("verification_status") != "verified" for edge in edges
    )
    return {
        "status": "ok" if not errors else "error",
        "source_count": len(sources),
        "edge_count": len(edges),
        "skill_rule_count": len(rule_ids),
        "unverified_edge_count": unverified,
        "errors": errors,
    }
