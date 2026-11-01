from __future__ import annotations

from .models import (
    CriticalReview,
    Decision,
    EvidenceMatrix,
    IdeaBrief,
    PrototypePlan,
    SourceManifest,
)


def bullets(values: list[str]) -> str:
    return "\n".join(f"- {value}" for value in values) if values else "- None recorded."


def render_dossier(
    idea: IdeaBrief,
    manifest: SourceManifest,
    evidence: EvidenceMatrix,
    review: CriticalReview,
    plan: PrototypePlan,
    decisions: list[Decision],
) -> str:
    approved = any(decision.approved for decision in decisions)
    status = "APPROVED" if approved else "DRAFT — human approval required"
    source_rows = (
        "\n".join(
            f"| {item.source_id} | {item.original_name} | {item.media_type} | `{item.original_sha256[:12]}...` | {item.extraction_status} |"
            for item in manifest.sources
        )
        or "| — | No sources ingested | — | — | — |"
    )
    evidence_rows = (
        "\n".join(
            f"| {item.claim_id or '—'} | {item.fact_type.value} | {item.claim} | {item.source_id or '—'} | {item.locator or '—'} | {item.confidence} |"
            for item in evidence.items
        )
        or "| — | — | No evidence recorded | — | — | — |"
    )
    bom_rows = (
        "\n".join(
            f"| {item.item} | {item.quantity} | {item.purpose} | {item.specification or 'Standard'} | {item.estimate_source} | {item.confidence} |"
            for item in plan.bom
        )
        or "| — | — | — | — | — | — |"
    )
    decision_rows = (
        "\n".join(
            f"- **{item.timestamp.isoformat()}** — Actor: `{item.actor or 'human'}` | Decision: `{item.decision.value if item.decision else ('APPROVED' if item.approved else 'RECORDED')}` | Statement: {item.statement or item.rationale}"
            for item in decisions
        )
        or "- No human decisions recorded. (Status remains DRAFT pending explicit human decision)"
    )

    return f"""# {idea.title}

- **Case ID:** {idea.meta.case_id}
- **Version:** v{idea.meta.version:03d}
- **Status:** {status}
- **Generated:** {idea.meta.created_at.isoformat()}

---

## 1. Executive summary

IDEAForge is a human-led invention experiment studio: **Falsify Before You Fabricate**.
This dossier consolidates the user's idea, ingested source evidence, independent red-team critique, prototype plan, and minimal decisive experiment specification.
*Notice: This document provides technical exploration and experiment planning only. It does not provide legal conclusions regarding patentability, novelty, freedom to operate, or regulatory compliance.*

## 2. User's original idea (verbatim)

> {idea.original_idea}

## 3. Normalized problem statement

{idea.problem or "Not provided (UNKNOWN)."}

## 4. Target user, operating environment, and system boundary

- **Target user:** {idea.target_user or "Unspecified maker / engineering team."}
- **Operating environment:** {idea.environment or "Benchtop / laboratory conditions."}
- **System boundary:** {idea.system_boundary or "Scoped strictly to benchtop experimental apparatus and immediate sensor instrumentation."}

## 5. Proposed technical mechanism and intended outcome

- **Proposed mechanism:** {idea.mechanism or "Not formally stated."}
- **Intended outcome:** {idea.outcome or "Distinguish physical mechanism through reproducible measurement."}

## 6. Constraints and known unknowns

### Constraints
{bullets(idea.constraints)}

### Known unknowns
{bullets(idea.known_unknowns)}

## 7. Assumption register

Every assertion lacking a verified source ID and locator is classified as `ASSUMPTION` or `INFERENCE` until empirically tested:
- Prioritize testing assumptions that would falsify the concept if incorrect.
- Never treat an inference or assumption as established fact.

## 8. Evidence matrix (Pillar A — Claim Ledger)

| ID | Type | Claim | Source ID | Locator | Confidence |
| --- | --- | --- | --- | --- | --- |
{evidence_rows}

## 9. Related work and overlap analysis

Review is strictly bounded by user-supplied and room-attached documents. No exhaustive web or prior-art patent search is claimed or implied.

{bullets(review.unresolved_questions)}

## 10. Red-team critique and adversarial review (Pillar B)

### Most Consequential Assumptions Challenged
{bullets(review.consequential_assumptions or ["Assumptions not explicitly isolated."])}

### Competing Explanations & Alternative Mechanisms
{bullets(review.alternative_mechanisms or ["No alternative mechanisms proposed."])}

### Confounding Variables
{bullets(review.confounding_variables or ["Operating speed, ambient vibrations, and sensor mounting variability."])}

### Measurement Limitations
{bullets(review.measurement_limitations or ["Sensor dynamic range, sampling rate, and noise floor."])}

### Failure Modes & Conditions Under Which Concept Fails
{bullets(review.failure_modes or ["Signal obscured by structural noise."])}
{bullets(review.failure_conditions)}

### Evidence That Would Change Assessment
{bullets(review.evidence_that_would_change_assessment or ["Controlled baseline vs defect tests showing statistically distinct spectral signatures."])}

### Practical Diagnostic Tests
{bullets(review.practical_tests)}

## 11. Proposed prototype architecture

{plan.architecture}

## 12. Bill of materials (BOM)

| Item | Qty | Purpose | Specification | Estimate Source | Confidence |
| --- | --- | --- | --- | --- | --- |
{bom_rows}

## 13. Experimental hypothesis & Minimum Decisive Experiment (Pillar C)

- **Primary hypothesis:** {plan.hypothesis}
- **Objective:** The smallest useful experiment to meaningfully distinguish the proposed mechanism from plausible alternative explanations.

## 14. Variables

- **Independent variable(s) (what changes):** {", ".join(plan.independent_variables) or "Controlled test conditions"}
- **Dependent variable(s) (what is measured):** {", ".join(plan.dependent_variables) or "Sensor amplitude / frequency response"}
- **Controlled variable(s) (what stays constant):** {", ".join(plan.controlled_variables) or "Belt speed, load, sensor mounting location"}

## 15. Equipment, calibration, and test protocol

### Equipment required
{bullets(plan.equipment)}

### Calibration checks
{bullets(plan.calibration)}

### Step-by-step protocol
{bullets(plan.protocol)}

## 16. Measurement, sample size, and acceptance criteria

- **Measurement plan:** {plan.measurement_plan or "Record raw time-series and compute descriptive statistics."}
- **Sample-size rationale:** {plan.sample_size_rationale}

### Acceptance criteria (Decision rules)
{bullets(plan.acceptance_criteria)}

## 17. Safety, ethics, and limitations

### Safety measures
{bullets(plan.safety or ["Follow electrical and mechanical workshop safety procedures."])}

### Limitations
- Does not test long-term durability.
- Laboratory benchtop data cannot be directly extrapolated to industrial duty cycles without further testing.

## 18. Human decisions and approval log (Pillar E)

{decision_rows}

## 19. Next recommended experiment

Execute the Experiment Kit (`experiment_card.md`) using `data_template.csv` and `analysis.py`.
Inspect outcomes against pre-registered acceptance criteria. If revision is necessary, create a new version (`python -m ideaforge new-version {idea.meta.case_id}`).

## 20. Sources and references

| Source ID | File | Media Type | SHA-256 | Status |
| --- | --- | --- | --- | --- |
{source_rows}

## 21. Appendix: machine-readable artifacts & kit files

- `00_idea_brief.json`
- `01_evidence_matrix.json`
- `02_critical_review.json`
- `03_prototype_plan.json`
- `validation_report.json`
- `decision_log.json`
- `experiment_kit/experiment_card.md`
- `experiment_kit/experiment_plan.json`
- `experiment_kit/data_template.csv`
- `experiment_kit/analysis.py`
- `experiment_kit/source_ledger.md`
- `experiment_kit/decision_record.md`
"""
