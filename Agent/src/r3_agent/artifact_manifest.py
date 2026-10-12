from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .hashing import sha256_file


INCLUDED_DIRECTORIES = (
    "configs",
    "docs",
    "examples",
    "probes",
    "prompts",
    "rubrics",
    "schemas",
    "skills",
    "src",
    "tests",
)
INCLUDED_FILES = (
    "CHANGELOG.md",
    "README.md",
    "pyproject.toml",
    "provenance/decisions.md",
    "provenance/out_of_scope_candidates.yaml",
    "provenance/source_registry.yaml",
    "provenance/traceability_edges.jsonl",
)


def _category(path: str) -> str:
    return path.split("/", 1)[0] if "/" in path else "package"


def _is_versioned_artifact(path: Path) -> bool:
    return (
        path.is_file()
        and "__pycache__" not in path.parts
        and path.suffix not in {".pyc", ".pyo"}
        and not any(part.endswith(".egg-info") for part in path.parts)
    )


def _artifact_paths(root: Path, output: Path) -> list[Path]:
    paths: set[Path] = set()
    for directory in INCLUDED_DIRECTORIES:
        base = root / directory
        if base.is_dir():
            paths.update(path for path in base.rglob("*") if _is_versioned_artifact(path))
    for relative in INCLUDED_FILES:
        path = root / relative
        if path.is_file():
            paths.add(path)
    paths.discard(output)
    return sorted(paths, key=lambda path: path.relative_to(root).as_posix())


def build_artifact_manifest(root: Path, output: Path | None = None) -> dict[str, Any]:
    root = root.resolve()
    output = (output or root / "provenance" / "artifact_manifest.json").resolve()
    artifacts = []
    digest_input = bytearray()
    for path in _artifact_paths(root, output):
        relative = path.relative_to(root).as_posix()
        digest = sha256_file(path)
        artifacts.append(
            {
                "path": relative,
                "category": _category(relative),
                "sha256": digest,
                "bytes": path.stat().st_size,
            }
        )
        digest_input.extend(f"{relative}\0{digest}\n".encode("utf-8"))
    return {
        "schema_version": "artifact-manifest-0.1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "hash_algorithm": "sha256",
        "artifact_count": len(artifacts),
        "root_digest": hashlib.sha256(digest_input).hexdigest(),
        "artifacts": artifacts,
    }


def write_artifact_manifest(root: Path, output: Path | None = None) -> Path:
    root = root.resolve()
    target = (output or root / "provenance" / "artifact_manifest.json").resolve()
    target.parent.mkdir(parents=True, exist_ok=True)
    payload = build_artifact_manifest(root, target)
    target.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return target
