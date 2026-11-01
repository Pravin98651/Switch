"""Runtime configuration with safe defaults and optional local overrides."""

from __future__ import annotations

import json
import os
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field, field_validator


class Settings(BaseModel):
    model_config = ConfigDict(extra="forbid")

    workspace: Path = Path("workspace")
    case_prefix: str = Field(default="IF", pattern=r"^[A-Za-z][A-Za-z0-9_-]*$")
    case_date_format: str = "%Y%m%d"
    case_sequence_width: int = Field(default=3, ge=1, le=12)
    version_prefix: str = Field(default="v", pattern=r"^[A-Za-z][A-Za-z0-9_-]*$")
    version_width: int = Field(default=3, ge=1, le=12)
    max_source_bytes: int = Field(default=25 * 1024 * 1024, ge=1)
    allowed_extensions: dict[str, str] = Field(
        default_factory=lambda: {
            ".txt": "text/plain",
            ".md": "text/markdown",
            ".pdf": "application/pdf",
            ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        }
    )

    @field_validator("allowed_extensions")
    @classmethod
    def extensions_are_normalized(cls, value: dict[str, str]) -> dict[str, str]:
        if not value:
            raise ValueError("at least one source extension must be allowed")
        normalized = {extension.lower(): media_type for extension, media_type in value.items()}
        if any(not extension.startswith(".") for extension in normalized):
            raise ValueError("allowed extension keys must begin with a dot")
        return normalized


def load_settings(
    config_file: str | Path | None = None, workspace: str | Path | None = None
) -> Settings:
    """Load a JSON config file, then apply explicit CLI and environment overrides."""
    candidate = Path(config_file) if config_file else Path(".ideaforge.json")
    values = json.loads(candidate.read_text(encoding="utf-8")) if candidate.is_file() else {}
    env_workspace = os.environ.get("IDEAFORGE_WORKSPACE")
    env_max_bytes = os.environ.get("IDEAFORGE_MAX_SOURCE_BYTES")
    if env_workspace:
        values["workspace"] = env_workspace
    if env_max_bytes:
        values["max_source_bytes"] = int(env_max_bytes)
    if workspace is not None:
        values["workspace"] = str(workspace)
    return Settings.model_validate(values)
