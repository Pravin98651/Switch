"""Export the authoritative JSON Schemas from the Pydantic models."""

from __future__ import annotations

import json
from pathlib import Path

from .models import (
    ClaimRecord,
    CriticalReview,
    DecisionRecord,
    EvidenceMatrix,
    ExperimentPlan,
    IdeaBrief,
    PrototypePlan,
    SourceManifest,
    UncertaintyRecord,
)

SCHEMAS = {
    "idea_brief.schema.json": IdeaBrief,
    "source_manifest.schema.json": SourceManifest,
    "evidence_matrix.schema.json": EvidenceMatrix,
    "critical_review.schema.json": CriticalReview,
    "prototype_plan.schema.json": PrototypePlan,
    "experiment_plan.schema.json": ExperimentPlan,
    "claim_record.schema.json": ClaimRecord,
    "uncertainty_record.schema.json": UncertaintyRecord,
    "decision_record.schema.json": DecisionRecord,
}


def export_schemas(directory: str | Path) -> list[Path]:
    output = Path(directory)
    output.mkdir(parents=True, exist_ok=True)
    written = []
    for name, model in SCHEMAS.items():
        path = output / name
        path.write_text(json.dumps(model.model_json_schema(), indent=2) + "\n", encoding="utf-8")
        written.append(path)
    return written
