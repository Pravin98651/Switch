"""Validated, provenance-aware IDEAForge artifact contracts."""

from __future__ import annotations

from datetime import UTC, datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, model_validator


def utc_now() -> datetime:
    return datetime.now(UTC)


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class FactType(str, Enum):
    SOURCE_BACKED = "SOURCE_BACKED"
    USER_PROVIDED = "USER_PROVIDED"
    INFERENCE = "INFERENCE"
    ASSUMPTION = "ASSUMPTION"
    HYPOTHESIS = "HYPOTHESIS"
    UNKNOWN = "UNKNOWN"


class ExperimentType(str, Enum):
    MINIMUM_DECISIVE = "MINIMUM_DECISIVE"
    PRELIMINARY_SCREENING = "PRELIMINARY_SCREENING"


class HumanDecision(str, Enum):
    APPROVE_EXPERIMENT = "APPROVE_EXPERIMENT"
    REQUEST_REVISION = "REQUEST_REVISION"
    DEFER = "DEFER"
    REJECT_EXPERIMENT = "REJECT_EXPERIMENT"


class CaseStatus(str, Enum):
    DRAFT = "draft"
    APPROVED = "approved"


class ArtifactMeta(StrictModel):
    case_id: str
    version: int = Field(ge=1)
    producer: str
    created_at: datetime = Field(default_factory=utc_now)
    status: CaseStatus = CaseStatus.DRAFT
    input_hashes: list[str] = Field(default_factory=list)


class IdeaBrief(StrictModel):
    meta: ArtifactMeta
    title: str = Field(min_length=1, max_length=200)
    original_idea: str = Field(min_length=1)
    problem: str | None = None
    target_user: str | None = None
    environment: str | None = None
    mechanism: str | None = None
    outcome: str | None = None
    constraints: list[str] = Field(default_factory=list)
    known_unknowns: list[str] = Field(default_factory=list)
    system_boundary: str | None = None
    clarifying_questions: list[str] = Field(default_factory=list)
    updated_at: datetime = Field(default_factory=utc_now)


class SourceRecord(StrictModel):
    source_id: str
    original_name: str
    media_type: str
    original_sha256: str
    extracted_sha256: str | None = None
    extraction_status: str
    locators: list[str] = Field(default_factory=list)
    extracted_path: str | None = None
    page_count: int | None = None
    extraction_warnings: list[str] = Field(default_factory=list)
    ingested_at: datetime = Field(default_factory=utc_now)


class SourceManifest(StrictModel):
    meta: ArtifactMeta
    sources: list[SourceRecord] = Field(default_factory=list)


class EvidenceItem(StrictModel):
    claim_id: str | None = None
    claim: str = Field(min_length=1)
    fact_type: FactType
    source_id: str | None = None
    locator: str | None = None
    confidence: str = "low"
    confidence_rationale: str = "Not provided."
    owner: str = "unknown"
    status: str = "unreviewed"
    supporting_item_ids: list[str] = Field(default_factory=list)
    supporting_excerpt: str | None = None
    interpretation: str = ""
    limitations: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=utc_now)

    @model_validator(mode="after")
    def source_backed_needs_source(self) -> EvidenceItem:
        if self.fact_type == FactType.SOURCE_BACKED and not self.source_id:
            raise ValueError("SOURCE_BACKED evidence requires source_id")
        return self


class EvidenceMatrix(StrictModel):
    meta: ArtifactMeta
    items: list[EvidenceItem] = Field(default_factory=list)


class ClaimRecord(StrictModel):
    claim_id: str
    statement: str = Field(min_length=1)
    classification: FactType
    source_id: str | None = None
    supporting_item_ids: list[str] = Field(default_factory=list)
    locator: str | None = None
    supporting_excerpt: str | None = None
    interpretation: str = ""
    limitations: list[str] = Field(default_factory=list)
    created_by: str = "unknown"
    status: str = "unreviewed"
    confidence_rationale: str = ""
    created_at: datetime = Field(default_factory=utc_now)

    @model_validator(mode="after")
    def source_claim_has_locator(self) -> ClaimRecord:
        if self.classification == FactType.SOURCE_BACKED and not self.source_id:
            raise ValueError("SOURCE_BACKED claim requires source_id")
        return self


class UncertaintyRecord(StrictModel):
    uncertainty_id: str
    question: str = Field(min_length=1)
    why_it_matters: str
    impact_if_wrong: str
    current_evidence: list[str] = Field(default_factory=list)
    testability: str
    blocking_decision: str
    human_selected: bool = False


class CriticalReview(StrictModel):
    meta: ArtifactMeta
    failure_modes: list[str] = Field(default_factory=list)
    alternative_mechanisms: list[str] = Field(default_factory=list)
    consequential_assumptions: list[str] = Field(default_factory=list)
    confounding_variables: list[str] = Field(default_factory=list)
    measurement_limitations: list[str] = Field(default_factory=list)
    failure_conditions: list[str] = Field(default_factory=list)
    evidence_that_would_change_assessment: list[str] = Field(default_factory=list)
    practical_tests: list[str] = Field(default_factory=list)
    unresolved_questions: list[str] = Field(default_factory=list)


class BomItem(StrictModel):
    item: str
    quantity: int = Field(ge=1)
    purpose: str
    specification: str | None = None
    estimate_source: str = "ASSUMPTION"
    confidence: str = "low"


class PrototypePlan(StrictModel):
    meta: ArtifactMeta
    architecture: str
    hypothesis: str
    independent_variables: list[str] = Field(default_factory=list)
    dependent_variables: list[str] = Field(default_factory=list)
    controlled_variables: list[str] = Field(default_factory=list)
    equipment: list[str] = Field(default_factory=list)
    calibration: list[str] = Field(default_factory=list)
    protocol: list[str] = Field(default_factory=list)
    measurement_plan: str = ""
    sample_size_rationale: str = "Proposal; not evidence-backed."
    acceptance_criteria: list[str] = Field(default_factory=list)
    safety: list[str] = Field(default_factory=list)
    bom: list[BomItem] = Field(default_factory=list)


class MeasuredVariable(StrictModel):
    name: str = Field(min_length=1)
    unit: str = Field(min_length=1, description="Use 'unitless' when appropriate.")
    required: bool = True


class DecisionCriteria(StrictModel):
    supports: str = Field(min_length=1)
    weakens: str = Field(min_length=1)
    inconclusive: str = Field(min_length=1)


class ExperimentPlan(StrictModel):
    experiment_id: str
    case_id: str
    version: int = Field(ge=1)
    title: str
    experiment_type: ExperimentType
    hypothesis: str
    alternative_explanation: str
    independent_variables: list[MeasuredVariable] = Field(min_length=1)
    dependent_variables: list[MeasuredVariable] = Field(min_length=1)
    control_variables: list[MeasuredVariable] = Field(min_length=1)
    equipment: list[str] = Field(min_length=1)
    calibration_steps: list[str] = Field(min_length=1)
    procedure: list[str] = Field(min_length=1)
    data_schema: list[MeasuredVariable] = Field(min_length=1)
    analysis_method: str
    criteria: DecisionCriteria
    safety_notes: list[str] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)
    mde_rationale: str = ""
    human_status: str = "DRAFT"

    @model_validator(mode="after")
    def mde_requires_distinguishing_rationale(self) -> ExperimentPlan:
        if (
            self.experiment_type == ExperimentType.MINIMUM_DECISIVE
            and not self.mde_rationale.strip()
        ):
            self.experiment_type = ExperimentType.PRELIMINARY_SCREENING
            self.limitations.append("Downgraded because no MDE rationale was supplied.")
        return self


class DecisionRecord(StrictModel):
    decision_id: str = Field(default_factory=lambda: f"DEC-{int(datetime.now(UTC).timestamp())}")
    case_id: str | None = None
    experiment_id: str | None = None
    timestamp: datetime = Field(default_factory=utc_now)
    actor: str | None = None
    statement: str = ""
    approved: bool = False
    decision: HumanDecision | None = None
    rationale: str = ""


# Alias Decision to DecisionRecord for backward compatibility
Decision = DecisionRecord


class ValidationReport(StrictModel):
    meta: ArtifactMeta
    valid: bool
    errors: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
