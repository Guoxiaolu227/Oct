from __future__ import annotations

import json
from pathlib import Path

from r3_agent.artifact_manifest import build_artifact_manifest, write_artifact_manifest


def test_manifest_is_stable_and_does_not_hash_itself(tmp_path: Path) -> None:
    (tmp_path / "prompts").mkdir()
    (tmp_path / "prompts" / "system.md").write_text("policy", encoding="utf-8")
    target = tmp_path / "provenance" / "artifact_manifest.json"

    first = build_artifact_manifest(tmp_path, target)
    write_artifact_manifest(tmp_path, target)
    second = build_artifact_manifest(tmp_path, target)

    assert first["root_digest"] == second["root_digest"]
    assert first["artifact_count"] == 1
    assert first["artifacts"][0]["path"] == "prompts/system.md"
    assert "artifact_manifest.json" not in target.read_text(encoding="utf-8")
    assert json.loads(target.read_text(encoding="utf-8"))["hash_algorithm"] == "sha256"
