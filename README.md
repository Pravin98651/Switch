# IDEAForge 2.0 — Human-Led Invention Experiment Studio

> **Falsify Before You Fabricate.**  
> *IDEAForge is a lab team in a Switch room: AI specialist agents that read supplied sources, challenge each other's assumptions, and cite only what can be cryptographically checked—while the human inventor controls the scope and makes the final decision.*

---

## 🏆 Hackathon Track Fit
- **Primary Track:** **Track 02 — Best Personal or Creative Workflow** (Flip the Switch Hackathon)
- **Why Track 02:** Turning an invention concept into a testable prototype is a deeply personal creative engineering journey. Rather than acting as a generic chatbot that produces ungrounded text, IDEAForge structures the maker's notebook, attacks risky assumptions with adversarial review, and produces an executable **Experiment Kit** to de-risk the idea before hardware fabrication.

---

## 💡 The Five Product Pillars

| Pillar | Principle | Implementation |
|---|---|---|
| **A. Claim Ledger** | Strict provenance taxonomy | Claims are tagged `SOURCE_BACKED`, `USER_PROVIDED`, `INFERENCE`, `ASSUMPTION`, `HYPOTHESIS`, or `UNKNOWN`. Source-backed claims require verified locators (`line:N`, `page:N`). |
| **B. Adversarial Review** | Active falsification | Red Team identifies top 3 consequential assumptions, at least 2 alternative explanations, confounders, and failure conditions. |
| **C. Minimum Decisive Experiment** | Decisive over descriptive | Designs the smallest test that distinguishes the proposed mechanism from competing alternatives. Lacking rationale triggers an automated downgrade to `PRELIMINARY_SCREENING`. |
| **D. Executable Experiment Kit** | Practical bench outputs | Generates `experiment_card.md`, typed `experiment_plan.json`, unit-labelled `data_template.csv`, fixed `analysis.py` (descriptive statistics only; no causal claims), `source_ledger.md`, and `decision_record.md`. |
| **E. Human Decision Gate** | Human in the loop | The dossier remains `DRAFT` until the inventor explicitly records `APPROVE_EXPERIMENT`, `REQUEST_REVISION`, `DEFER`, or `REJECT_EXPERIMENT`. Revisions create immutable new versions. |

---

## 🤖 The Multi-Agent Studio in Switch

All collaboration occurs visibly in the `ideaforge-demo` Switch room (backed by Mattermost):

```text
[Human Inventor] ──► Starts case with rough idea & reference docs
       │
       ▼
[@forge-lead] ──────► Preserves idea verbatim, normalizes problem, asks <=2 questions
       │
       ├────────────► Visible @mention handoff to @evidence-scout (Source citations & overlap)
       ├────────────► Visible @mention handoff to @red-team (Failure modes & competing mechanisms)
       │
       ▼
[Human Scope Gate] ─► Maker selects/confirms the single critical uncertainty
       │
       ▼
[@experiment-designer] ► Designs the Minimum Decisive Experiment (2x2 comparison test)
       │
       ▼
[CLI Validator] ────► forge-lead runs local deterministic validator; catches any invalid citations
       │
       ▼
[Human Approval] ───► Maker reviews Experiment Card; approves experiment or requests revision
```

---

## 🚀 Quick Start

### 1. Prerequisites
- Python 3.11+
- Git
- Docker (for Switch local server & bundled Mattermost)
- Switch Console ([Download latest release](https://github.com/sandbox-quantum/switch/releases/latest))
- Codex CLI (`codex login`)

### 2. Installation
```powershell
# Clone and enter directory
cd C:\Projects\Switch

# Create and activate virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install package in editable mode with document parsing & dev tools
python -m pip install -e ".[documents,dev]"

# Verify CLI
python -m ideaforge --help
```

---

## 🔬 End-to-End Demo: Conveyor Belt Early Defect Detection

This scenario investigates whether high-frequency acoustic emissions (>20 kHz) and vibration signals can detect an early conveyor belt micro-tear before visible failure, distinguishing it from roller speed-dependent harmonics.

```powershell
# 1. Create a new case
python -m ideaforge --workspace workspace create-case "Conveyor belt early micro-tear defect detection"
# Outputs: CASE_ID (e.g. IF-20261102-001)

# 2. Ingest reference source pack
python -m ideaforge --workspace workspace ingest CASE_ID examples\demo_case\sources\demo_problem_brief.md
python -m ideaforge --workspace workspace ingest CASE_ID examples\demo_case\sources\demo_sensor_notes.md
python -m ideaforge --workspace workspace ingest CASE_ID examples\demo_case\sources\demo_experiment_constraints.md
python -m ideaforge --workspace workspace ingest CASE_ID examples\demo_case\sources\demo_fault_injection_source.md

# 3. Import specialist JSON artifacts from Switch room
python -m ideaforge --workspace workspace init-artifacts CASE_ID --title "Conveyor Defect Detection" --idea "Explore vibration and acoustic signals..."
python -m ideaforge --workspace workspace import-artifact CASE_ID idea examples\demo_case\artifacts\00_idea_brief.json --adopt
python -m ideaforge --workspace workspace import-artifact CASE_ID review examples\demo_case\artifacts\02_critical_review.json --adopt
python -m ideaforge --workspace workspace import-artifact CASE_ID plan examples\demo_case\artifacts\03_prototype_plan.json --adopt

# 4. Deliberate Fault Injection Demonstration
# Import evidence containing an intentionally invalid locator 'line:999'
python -m ideaforge --workspace workspace import-artifact CASE_ID evidence examples\demo_case\artifacts\01_evidence_matrix_fault.json --adopt
# Validator catches and rejects it with exit code 1!
python -m ideaforge --workspace workspace validate CASE_ID

# 5. Repair the Fault
python -m ideaforge --workspace workspace import-artifact CASE_ID evidence examples\demo_case\artifacts\01_evidence_matrix.json --adopt
# Validator passes with exit code 0!
python -m ideaforge --workspace workspace validate CASE_ID

# 6. Build the Executable Experiment Kit
python -m ideaforge --workspace workspace build-kit CASE_ID examples\demo_case\artifacts\experiment_plan.json --adopt

# 7. Render and record human approval
python -m ideaforge --workspace workspace render CASE_ID
python -m ideaforge --workspace workspace decide CASE_ID APPROVE_EXPERIMENT --rationale "Risks acceptable for benchtop test rig."
python -m ideaforge --workspace workspace render CASE_ID

# 8. Export the approved dossier
python -m ideaforge --workspace workspace export CASE_ID --out exports\conveyor_dossier.md

# 9. Execute fixed descriptive analysis starter
cd workspace\CASE_ID\versions\v001\experiment_kit
python analysis.py data_template.csv
```

---

## 🛠️ CLI Reference

- `python -m ideaforge create-case <TITLE>`: Creates a new append-only case directory.
- `python -m ideaforge ingest <CASE_ID> <FILE>`: Extracts text, hashes bytes (`SHA-256`), and registers line/page locators.
- `python -m ideaforge status <CASE_ID>`: Displays case status, ingested sources count, artifact health, and decision state.
- `python -m ideaforge validate <CASE_ID>`: Verifies artifact metadata, citation provenance, locators, and model schemas.
- `python -m ideaforge build-kit <CASE_ID> <PLAN_JSON>`: Generates the 6 Experiment Kit deliverables in `experiment_kit/`.
- `python -m ideaforge decide <CASE_ID> <DECISION>`: Records human decision (`APPROVE_EXPERIMENT`, `REQUEST_REVISION`, `DEFER`, `REJECT_EXPERIMENT`).
- `python -m ideaforge render <CASE_ID>`: Renders the complete 20+ section Markdown dossier (`dossier.md`).
- `python -m ideaforge export <CASE_ID> --out <PATH>`: Exports the validated dossier to a designated destination path.
- `python -m ideaforge new-version <CASE_ID>`: Increments version counter, creating an immutable new revision (`v002`).
- `python -m ideaforge export-schemas`: Refreshes checked-in JSON Schema files from Pydantic models.

---

## 🧪 Testing & Verification

Run the comprehensive test suite and code quality checks:
```powershell
# Run 12 automated unit and integration tests
python -m pytest

# Code quality and style checks
python -m ruff check src tests
python -m ruff format --check src tests
```

---

## 🔒 Security, Privacy, and Responsible Use
- **Zero Document Leakage:** Document parsing, text extraction, hashing, and rendering run entirely offline on your local computer.
- **No Arbitrary Code Execution:** The starter script `analysis.py` contains fixed, deterministic descriptive statistics code only. No model-generated code is ever executed.
- **Physical Safety:** Experiment plans require safety hazard reviews, emergency stop controls, and benchtop boundaries.
- **Non-Legal Notice:** IDEAForge provides technical experiment planning only. It does not provide legal opinions on patentability, novelty, infringement, or filing readiness.
