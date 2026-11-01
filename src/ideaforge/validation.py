from __future__ import annotations

from .models import (
    CriticalReview,
    EvidenceMatrix,
    ExperimentPlan,
    FactType,
    IdeaBrief,
    PrototypePlan,
    SourceManifest,
)


def validate_evidence(manifest: SourceManifest, evidence: EvidenceMatrix) -> list[str]:
    errors: list[str] = []
    sources = {source.source_id: source for source in manifest.sources}
    for index, item in enumerate(evidence.items, 1):
        if item.fact_type == FactType.SOURCE_BACKED:
            source = sources.get(item.source_id or "")
            if source is None:
                errors.append(f"evidence item {index}: unknown source ID {item.source_id}")
            elif not item.locator:
                errors.append(f"evidence item {index}: source-backed claim needs locator")
            elif item.locator not in source.locators:
                errors.append(
                    f"evidence item {index}: locator {item.locator!r} is not in {source.source_id}"
                )
            elif source.extraction_status == "failed":
                errors.append(
                    f"evidence item {index}: points to source {item.source_id} which failed extraction"
                )
    return errors


def validate_artifacts(
    case_id: str,
    version: int,
    idea: IdeaBrief,
    manifest: SourceManifest,
    evidence: EvidenceMatrix,
    review: CriticalReview,
    plan: PrototypePlan,
) -> list[str]:
    """Validate cross-artifact identity, consistency, and evidence provenance."""
    errors = validate_evidence(manifest, evidence)
    for name, artifact in {
        "idea brief": idea,
        "evidence matrix": evidence,
        "critical review": review,
        "prototype plan": plan,
    }.items():
        if artifact.meta.case_id != case_id:
            errors.append(f"{name}: case ID does not match requested case")
        if artifact.meta.version != version:
            errors.append(f"{name}: version does not match requested version")
    if manifest.meta.case_id != case_id:
        errors.append("source manifest: case ID does not match requested case")
    if not plan.protocol:
        errors.append("prototype plan: protocol must contain at least one step")
    if not plan.acceptance_criteria:
        errors.append("prototype plan: acceptance criteria are required")
    for bom_idx, bom_item in enumerate(plan.bom, 1):
        if bom_item.quantity < 1:
            errors.append(f"prototype plan BOM item {bom_idx}: quantity must be at least 1")
    return errors


def validate_experiment_plan(plan: ExperimentPlan) -> list[str]:
    """Validate experiment plan constraints."""
    errors: list[str] = []
    for var in plan.independent_variables + plan.dependent_variables + plan.control_variables:
        if not var.name.strip():
            errors.append("variable name cannot be empty")
        if not var.unit.strip():
            errors.append(f"variable '{var.name}' requires a unit (use 'unitless' if none)")
    if not plan.criteria.supports.strip():
        errors.append("criteria for supporting hypothesis is required")
    if not plan.criteria.weakens.strip():
        errors.append("criteria for weakening hypothesis is required")
    if not plan.criteria.inconclusive.strip():
        errors.append("criteria for inconclusive outcome is required")
    return errors
