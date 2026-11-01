from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from .config import Settings
from .models import CaseStatus, utc_now


def safe_case_id(workspace: Path, settings: Settings) -> str:
    date = utc_now().strftime(settings.case_date_format)
    if not re.fullmatch(r"[A-Za-z0-9_-]+", date):
        raise ValueError("case_date_format must produce a filesystem-safe date component")
    stem = f"{settings.case_prefix}-{date}"
    existing = {p.name for p in workspace.glob(f"{stem}-*")}
    index = 1
    while f"{stem}-{index:0{settings.case_sequence_width}d}" in existing:
        index += 1
    return f"{stem}-{index:0{settings.case_sequence_width}d}"


def atomic_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(value, indent=2, default=str) + "\n", encoding="utf-8")
    tmp.replace(path)


class CaseStore:
    def __init__(self, workspace: str | Path | None = None, settings: Settings | None = None):
        self.settings = settings or Settings()
        self.workspace = Path(workspace) if workspace is not None else self.settings.workspace

    def case_path(self, case_id: str) -> Path:
        pattern = rf"{re.escape(self.settings.case_prefix)}-[A-Za-z0-9_-]+-\d{{{self.settings.case_sequence_width}}}"
        if not re.fullmatch(pattern, case_id):
            raise ValueError("invalid case ID")
        return self.workspace / case_id

    def create_case(self, title: str) -> tuple[str, Path]:
        self.workspace.mkdir(parents=True, exist_ok=True)
        case_id = safe_case_id(self.workspace, self.settings)
        root = self.case_path(case_id)
        (root / "sources" / "original").mkdir(parents=True)
        (root / "sources" / "extracted").mkdir(parents=True)
        atomic_json(
            root / "case.json",
            {
                "case_id": case_id,
                "title": title,
                "created_at": utc_now(),
                "status": CaseStatus.DRAFT.value,
            },
        )
        self.create_version(case_id)
        return case_id, root

    def create_version(self, case_id: str) -> tuple[int, Path]:
        versions = self.case_path(case_id) / "versions"
        versions.mkdir(parents=True, exist_ok=True)
        pattern = f"{self.settings.version_prefix}" + "[0-9]" * self.settings.version_width
        numbers = [int(p.name[len(self.settings.version_prefix) :]) for p in versions.glob(pattern)]
        number = max(numbers, default=0) + 1
        path = versions / f"{self.settings.version_prefix}{number:0{self.settings.version_width}d}"
        path.mkdir()
        return number, path

    def version_path(self, case_id: str, version: int | None = None) -> tuple[int, Path]:
        versions = self.case_path(case_id) / "versions"
        pattern = f"{self.settings.version_prefix}" + "[0-9]" * self.settings.version_width
        numbers = sorted(
            int(p.name[len(self.settings.version_prefix) :]) for p in versions.glob(pattern)
        )
        if not numbers:
            raise FileNotFoundError("case has no versions")
        number = version or numbers[-1]
        path = versions / f"{self.settings.version_prefix}{number:0{self.settings.version_width}d}"
        if not path.is_dir():
            raise FileNotFoundError(f"version {number} not found")
        return number, path
