# IDEAForge 2.0 — Implementation Plan & Milestones

> **Theme:** Falsify Before You Fabricate  
> **Target:** Track 02 — Best Personal or Creative Workflow (Flip the Switch Hackathon)

---

## Verified Platform & Environment
- **Workspace:** `C:\Projects\Switch`
- **Operating System:** Windows 11 / PowerShell
- **Python:** Python 3.14.3 (with isolated `.venv` containing `pydantic`, `click`/`argparse`, `pymupdf`, `python-docx`, `pytest`, `ruff`)
- **Docker CLI:** 28.1.1
- **Codex CLI:** 0.166.0-alpha.5.1
- **Switch Console & Mattermost:** Local Docker-backed Switch server with bundled Mattermost

---

## Milestone Breakdown

### Milestone 0: Environment Inspection & Architectural Plan
- [x] Inspect directory, platform, Python environment, Docker, and Switch Console.
- [x] Read official Switch documentation (quickstart, rooms, agent protocol, shared context).
- [x] Formulate architecture decisions in `docs/DECISIONS.md`.
- [x] Define human-in-the-loop experiment studio workflow in `docs/WORKFLOW.md`.

### Milestone 1: Domain Models (Pydantic v2 Contracts)
- [x] Implement `FactType` (`SOURCE_BACKED`, `USER_PROVIDED`, `INFERENCE`, `ASSUMPTION`, `HYPOTHESIS`, `UNKNOWN`).
- [x] Implement `IdeaBrief`, `SourceRecord`, `SourceManifest`, `EvidenceItem`, `EvidenceMatrix`.
- [x] Implement `ClaimRecord` and `UncertaintyRecord`.
- [x] Implement `CriticalReview` with consequential assumptions, alternative mechanisms, confounders, and failure modes.
- [x] Implement `PrototypePlan`, `BomItem`, `MeasuredVariable`, and `DecisionCriteria`.
- [x] Implement `ExperimentPlan` with automated downgrade to `PRELIMINARY_SCREENING` if MDE rationale is absent.
- [x] Implement `DecisionRecord` and `HumanDecision` enum (`APPROVE_EXPERIMENT`, `REQUEST_REVISION`, `DEFER`, `REJECT_EXPERIMENT`).
- [x] Export authoritative JSON schemas to `schemas/`.

### Milestone 2: Case Store & Multi-Format Ingestion
- [x] Versioned filesystem storage under `workspace/<CASE_ID>/versions/v<NNN>/`.
- [x] SHA-256 cryptographic hashing of original and extracted bytes.
- [x] Duplicate source detection by hash.
- [x] TXT and Markdown extraction with 1-based line locators (`line:N`).
- [x] PDF extraction via PyMuPDF with 1-based page locators (`page:N`).
- [x] DOCX extraction via python-docx with paragraph locators (`paragraph:N`).
- [x] Enforce configurable max file size limits and reject zero-byte files.

### Milestone 3: Claim Ledger & Provenance Validation
- [x] Cross-artifact case ID and version verification.
- [x] Enforce `SOURCE_BACKED` claims require valid `source_id`.
- [x] Validate that cited locators exist in the ingested source manifest.
- [x] Fail validation if source extraction failed or locator is missing.

### Milestone 4: Experiment Schema & MDE Validator
- [x] Validate variables have physical units.
- [x] Require non-empty control variables and explicit decision rules (supports / weakens / inconclusive).
- [x] MDE distinguishing rationale validation.

### Milestone 5: Executable Experiment Kit Renderer
- [x] Generate `experiment_card.md` (one-page human-readable brief).
- [x] Generate `experiment_plan.json` (typed plan).
- [x] Generate `data_template.csv` with standardized headers and units.
- [x] Generate `analysis.py` (fixed descriptive statistics script; no arbitrary LLM code execution; no causal claims).
- [x] Generate `source_ledger.json` and `source_ledger.md`.
- [x] Generate `decision_record.md`.
- [x] Deterministic Markdown dossier renderer (`rendering.py`) with all 20+ sections.

### Milestone 6: Switch Room & Multi-Agent Role Configuration
- [x] Room instructions in `switch/ROOM_INSTRUCTIONS.md`.
- [x] `forge-lead` prompt (`switch/agents/forge_lead.md`).
- [x] `evidence-scout` prompt (`switch/agents/evidence_scout.md`).
- [x] `red-team` prompt (`switch/agents/red_team.md`).
- [x] `experiment-designer` / `prototype-planner` prompt (`switch/agents/experiment_designer.md`).
- [x] Verified Switch Console manual setup instructions in `docs/SWITCH_SETUP.md`.

### Milestone 7: End-to-End Demo Case
- [x] Sanitized conveyor belt early defect detection scenario (`examples/demo_case/`).
- [x] 4 reference sources (`demo_problem_brief.md`, `demo_sensor_notes.md`, `demo_experiment_constraints.md`, `demo_fault_injection_source.md`).
- [x] Validated JSON artifacts for all 4 stages.
- [x] Staged deliberate fault injection artifact (`01_evidence_matrix_fault.json`) and repair verification.
- [x] End-to-end room workflow walkthrough in `examples/demo_case/expected_workflow.md`.

### Milestone 8: Hardening & Test Verification
- [x] Unit and integration tests in `tests/test_core.py`.
- [x] CLI commands (`create-case`, `ingest`, `init-artifacts`, `import-artifact`, `validate`, `build-kit`, `decide`, `approve`, `render`, `export`, `status`).
- [x] Code formatting and linting pass via `ruff check` and `ruff format`.

### Milestone 9: Documentation & Presentation
- [x] Public `README.md` updated with v2 positioning, architecture, and quickstart.
- [x] Product specification in `SPEC.md`.
- [x] 3-minute demo script in `docs/DEMO_SCRIPT.md`.
- [x] Architecture document in `docs/ARCHITECTURE.md`.
- [x] Security and privacy boundaries in `docs/SECURITY_AND_PRIVACY.md`.

### Milestone 10: Submission Readiness
- [x] Clean clone reproduction check.
- [x] Track 02 submission checklist verified in `docs/SUBMISSION_CHECKLIST.md`.
