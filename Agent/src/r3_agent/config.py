from __future__ import annotations

from pathlib import Path

import yaml
from pydantic import BaseModel, ConfigDict, Field

from .errors import ConfigError


class _Model(BaseModel):
    model_config = ConfigDict(extra="forbid")


class ProviderConfig(_Model):
    name: str
    base_url: str
    model: str
    api_key_env: str
    temperature: float = 0
    max_output_tokens: int = Field(gt=0)
    max_retries: int = Field(ge=0, le=10)


class InputConfig(_Model):
    allowed_extensions: list[str]
    max_characters: int = Field(gt=0)


class ExecutionConfig(_Model):
    condition: str
    output_language: str
    invoke_all_mechanisms: bool
    verifier_enabled: bool
    retry_backoff_seconds: float = Field(ge=0, le=60)


class PathConfig(_Model):
    rubric: str
    system_prompt: str
    orchestrator_prompt: str
    verifier_prompt: str
    skills: str
    private_runs: str
    source_registry: str
    traceability_edges: str


class AgentConfig(_Model):
    schema_version: str
    provider: ProviderConfig
    input: InputConfig
    execution: ExecutionConfig
    paths: PathConfig
    root: Path
    config_path: Path

    def resolve(self, relative: str) -> Path:
        return (self.root / relative).resolve()


def load_config(path: Path) -> AgentConfig:
    path = path.resolve()
    if not path.is_file():
        raise ConfigError(f"Configuration file not found: {path}")
    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, yaml.YAMLError) as exc:
        raise ConfigError(f"Cannot load configuration: {exc}") from exc
    if not isinstance(raw, dict):
        raise ConfigError("Configuration root must be an object")
    root = path.parent.parent if path.parent.name == "configs" else path.parent
    return AgentConfig.model_validate({**raw, "root": root, "config_path": path})
