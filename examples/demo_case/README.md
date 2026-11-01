# IDEAForge Demo Case: Conveyor Belt Early Defect Detection

This directory contains the public/synthetic reference source pack, pre-validated structured artifacts, and step-by-step commands to reproduce the entire IDEAForge 2.0 workflow offline or inside a Switch room.

## Directory Structure
- `idea_input.md`: The user's original idea prompt verbatim.
- `sources/`: 4 public/synthetic markdown reference documents.
  - `demo_problem_brief.md`
  - `demo_sensor_notes.md`
  - `demo_experiment_constraints.md`
  - `demo_fault_injection_source.md` (contains reference lines for fault injection)
- `artifacts/`: Authoritative structured JSON artifacts matching the schema.
  - `00_idea_brief.json`
  - `01_evidence_matrix.json` (clean valid evidence)
  - `01_evidence_matrix_fault.json` (deliberate fault injection with invalid `line:999` locator)
  - `02_critical_review.json`
  - `03_prototype_plan.json`
  - `experiment_plan.json` (Minimum Decisive Experiment plan)
- `expected_workflow.md`: Turn-by-turn Switch room transcript.

## CLI Walkthrough (Offline Deterministic Reproduction)

```powershell
# 1. Activate venv
.\.venv\Scripts\Activate.ps1

# 2. Create case
python -m ideaforge --workspace workspace create-case "Conveyor belt early micro-tear defect detection"
# Note the returned CASE_ID (e.g. IF-20261102-001)

# 3. Ingest sources
python -m ideaforge --workspace workspace ingest CASE_ID examples\demo_case\sources\demo_problem_brief.md
python -m ideaforge --workspace workspace ingest CASE_ID examples\demo_case\sources\demo_sensor_notes.md
python -m ideaforge --workspace workspace ingest CASE_ID examples\demo_case\sources\demo_experiment_constraints.md
python -m ideaforge --workspace workspace ingest CASE_ID examples\demo_case\sources\demo_fault_injection_source.md

# 4. Initialize and import artifacts
python -m ideaforge --workspace workspace init-artifacts CASE_ID --title "Conveyor Defect Detection" --idea "Explore vibration and acoustic signals..."
python -m ideaforge --workspace workspace import-artifact CASE_ID idea examples\demo_case\artifacts\00_idea_brief.json --adopt
python -m ideaforge --workspace workspace import-artifact CASE_ID review examples\demo_case\artifacts\02_critical_review.json --adopt
python -m ideaforge --workspace workspace import-artifact CASE_ID plan examples\demo_case\artifacts\03_prototype_plan.json --adopt

# 5. Fault Injection Demonstration
# Import the fault-injected evidence with invalid locator 'line:999'
python -m ideaforge --workspace workspace import-artifact CASE_ID evidence examples\demo_case\artifacts\01_evidence_matrix_fault.json --adopt
# Run validation: exits with code 1 and reports invalid locator!
python -m ideaforge --workspace workspace validate CASE_ID

# 6. Repair the fault
# Import the clean evidence matrix with valid locator 'line:3'
python -m ideaforge --workspace workspace import-artifact CASE_ID evidence examples\demo_case\artifacts\01_evidence_matrix.json --adopt
# Run validation: passes with code 0!
python -m ideaforge --workspace workspace validate CASE_ID

# 7. Build the Experiment Kit
python -m ideaforge --workspace workspace build-kit CASE_ID examples\demo_case\artifacts\experiment_plan.json --adopt

# 8. Render draft dossier
python -m ideaforge --workspace workspace render CASE_ID

# 9. Record Human Decision
python -m ideaforge --workspace workspace decide CASE_ID APPROVE_EXPERIMENT --rationale "Risks acceptable for benchtop test rig."

# 10. Render and export approved dossier
python -m ideaforge --workspace workspace render CASE_ID
python -m ideaforge --workspace workspace export CASE_ID --out exports\dossier.md

# 11. Run fixed analysis starter
cd workspace\CASE_ID\versions\v001\experiment_kit
python analysis.py data_template.csv
```
