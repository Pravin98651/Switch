# IDEAForge 2.0 — Architectural Decision Records (ADRs)

## ADR-001: File-Backed, Append-Only Versioned Storage
- **Status:** Accepted
- **Context:** An experiment planning studio needs transparent, reproducible artifact persistence without requiring heavy database dependencies.
- **Decision:** Cases are stored under `workspace/<CASE_ID>/versions/v<NNN>/` using pure JSON and Markdown files. Source documents are stored unchanged under `workspace/<CASE_ID>/sources/original/`, with extracted representations and cryptographic SHA-256 digests in `source_manifest.json`.
- **Consequences:** Highly portable, human-inspectable, git-friendly, zero external database setup required.

## ADR-002: Authoritative Pydantic v2 Contracts & Schema Export
- **Status:** Accepted
- **Context:** Multiple specialist agents and CLI tools exchange structured findings. Hand-maintained JSON schemas risk schema drift.
- **Decision:** Python Pydantic models in `models.py` (`extra="forbid"`) serve as the single source of truth. JSON Schema files in `schemas/` are automatically generated via `python -m ideaforge export-schemas`.
- **Consequences:** Guaranteed type safety, strict enum checking, and programmatic export for external validators.

## ADR-003: Switch Console as Primary Collaboration Surface
- **Status:** Accepted
- **Context:** Hackathon Track 02 requires real human-agent collaboration through Switch.
- **Decision:** Switch Room (`ideaforge-demo` over local Mattermost) is the primary interactive surface where the human, lead, and specialists converse and make visible handoffs. IDEAForge Python CLI acts as an offline deterministic ingestion, provenance validation, and rendering engine.
- **Consequences:** Preserves genuine human collaboration without replacing Switch with a hidden private Python orchestration loop.

## ADR-004: Explicit Human Decision Gate (Pillar E)
- **Status:** Accepted
- **Context:** An AI tool must not autonomously approve experimental protocols or claim an invention is validated.
- **Decision:** The dossier and Experiment Kit remain strictly `DRAFT` until the human records an explicit decision (`APPROVE_EXPERIMENT`, `REQUEST_REVISION`, `DEFER`, `REJECT_EXPERIMENT`).
- **Consequences:** Ensures human accountability; prevents unverified execution or accidental fabrication.

## ADR-005: Strict Cryptographic Provenance & Claim Taxonomy (Pillar A)
- **Status:** Accepted
- **Context:** LLMs frequently hallucinate citations, page numbers, and research papers.
- **Decision:** All assertions must be categorized as `SOURCE_BACKED`, `USER_PROVIDED`, `INFERENCE`, `ASSUMPTION`, `HYPOTHESIS`, or `UNKNOWN`. Every `SOURCE_BACKED` claim must cite a valid `source_id` and an exact locator (`line:N`, `page:N`, `paragraph:N`) verified against the ingested text manifest.
- **Consequences:** Hallucinated citations are rejected by the validator with actionable line/page errors.

## ADR-006: Primary Deliverable is an Executable Experiment Kit (Pillar D)
- **Status:** Accepted
- **Context:** Long narrative AI reports are rarely actionable for hardware makers and inventors.
- **Decision:** The primary tangible deliverable is a self-contained Experiment Kit containing:
  1. `experiment_card.md` (one-page brief)
  2. `experiment_plan.json` (typed contract)
  3. `data_template.csv` (headers and units)
  4. `analysis.py` (fixed deterministic analysis starter)
  5. `source_ledger.json` and `source_ledger.md` (provenance ledger)
  6. `decision_record.md` (human decision audit trail)
- **Consequences:** Makers can immediately perform the test on a benchtop rig and process observations without writing code from scratch.

## ADR-007: Minimum Decisive Experiment & Automated Downgrade (Pillar C)
- **Status:** Accepted
- **Context:** Tests that cannot distinguish between competing explanations provide false confidence.
- **Decision:** If an `ExperimentPlan` is labelled `MINIMUM_DECISIVE` but lacks an explicit `mde_rationale` explaining how it distinguishes the proposed mechanism from competing explanations, the model validator automatically downgrades its type to `PRELIMINARY_SCREENING` and logs the limitation.
- **Consequences:** Forces scientific rigor and honesty; prevents ambiguous tests from being marketed as decisive.

## ADR-008: Zero Arbitrary Code Execution (Safety)
- **Status:** Accepted
- **Context:** Executing arbitrary LLM-generated code poses severe security and reliability hazards.
- **Decision:** `analysis.py` is a fixed, reviewed, deterministic Python script that computes standard descriptive statistics (mean, std dev, min, max, row count, exclusions) from `data_template.csv`. It explicitly disclaims causal conclusions. No model-generated code is executed.
- **Consequences:** Safe, predictable, offline execution without sandbox escaping risks.

## ADR-009: Staged Deliberate Fault Injection in Verification Protocol
- **Status:** Accepted
- **Context:** Demonstrating validation requires proving that errors are caught, not just that happy paths pass.
- **Decision:** The verification demo incorporates an explicit, declared fault injection (submitting an invalid locator `line:999`), showing the CLI validator reject it in the room, and then repairing it to `line:3`.
- **Consequences:** Transparent demonstration of system boundaries; honest testing.
