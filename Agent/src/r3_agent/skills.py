from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml

from .errors import ConfigError
from .hashing import sha256_file


@dataclass(frozen=True)
class SkillDefinition:
    skill_id: str
    version: str
    mechanism_id: str
    name: str
    skill_path: Path
    skill_text: str
    methodology_path: Path
    methodology_text: str
    rules_path: Path
    rules: dict
    artifact_hashes: dict[str, str]


def _read(path: Path) -> str:
    if not path.is_file():
        raise ConfigError(f"Required skill artifact is missing: {path}")
    return path.read_text(encoding="utf-8")


def load_skills(rubric_path: Path, skills_root: Path) -> list[SkillDefinition]:
    rubric = yaml.safe_load(_read(rubric_path))
    loaded: list[SkillDefinition] = []
    for mechanism in rubric.get("mechanisms", []):
        skill_id = mechanism["skill_id"]
        skill_root = skills_root / skill_id
        skill_path = skill_root / "SKILL.md"
        methodology_path = skill_root / "references" / "methodology.md"
        rules_path = skill_root / "references" / "decision-rules.yaml"
        rules = yaml.safe_load(_read(rules_path))
        if rules.get("skill_id") != skill_id or rules.get("mechanism_id") != mechanism["mechanism_id"]:
            raise ConfigError(f"Skill registry mismatch for {skill_id}")
        expected_rules = set(mechanism.get("rule_ids", []))
        actual_rules = {item.get("rule_id") for item in rules.get("rules", [])}
        if expected_rules != actual_rules:
            raise ConfigError(f"Rule registry mismatch for {skill_id}")
        loaded.append(
            SkillDefinition(
                skill_id=skill_id,
                version=rules["skill_version"],
                mechanism_id=mechanism["mechanism_id"],
                name=mechanism["name"],
                skill_path=skill_path,
                skill_text=_read(skill_path),
                methodology_path=methodology_path,
                methodology_text=_read(methodology_path),
                rules_path=rules_path,
                rules=rules,
                artifact_hashes={
                    "skill": sha256_file(skill_path),
                    "methodology": sha256_file(methodology_path),
                    "decision_rules": sha256_file(rules_path),
                },
            )
        )
    if len(loaded) != 5:
        raise ConfigError(f"Expected five R3 skills, found {len(loaded)}")
    return loaded
