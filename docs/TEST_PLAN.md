# IDEAForge 2.0 — Comprehensive Test Plan

## 1. Automated Unit & Integration Tests
Run via pytest:
```powershell
.\.venv\Scripts\Activate.ps1
python -m pytest
```

### Test Suite Matrix (`tests/test_core.py`)
1. `test_cases_are_versioned`: Validates unique case ID formatting (`IF-...`) and immutable incremental version directory structure (`v001`, `v002`).
2. `test_source_backed_evidence_requires_source`: Ensures `SOURCE_BACKED` claims without a `source_id` throw a validation error.
3. `test_fact_types`: Verifies all 6 fact classifications (`SOURCE_BACKED`, `USER_PROVIDED`, `INFERENCE`, `ASSUMPTION`, `HYPOTHESIS`, `UNKNOWN`).
4. `test_text_ingestion_and_provenance`: Tests line-by-line indexing of Markdown/TXT files and validator catching invalid locator (`line:99`).
5. `test_pdf_and_docx_ingestion`: Tests PyMuPDF page-aware extraction (`page:1`) and python-docx paragraph extraction (`paragraph:2`).
6. `test_validation_reports_cross_artifact_mismatches`: Tests detection of case ID and version discrepancies across artifacts.
7. `test_duplicate_source_rejection`: Cryptographic SHA-256 collision detection rejects identical duplicate file uploads.
8. `test_file_size_limit`: Enforces max source byte threshold rejection.
9. `test_experiment_kit_and_screening_downgrade`: Verifies that an MDE lacking distinguishing rationale is automatically downgraded to `PRELIMINARY_SCREENING`, and tests execution of `analysis.py` against `data_template.csv`.
10. `test_mde_retains_type_with_rationale`: Confirms `MINIMUM_DECISIVE` is preserved when valid rationale is provided.
11. `test_decision_record`: Validates human decision recording model.
12. `test_cli_status_and_export`: Tests full end-to-end CLI workflow (`create-case`, `init-artifacts`, `status`, `render`, `export`).

---

## 2. Linting & Formatting Verification
```powershell
python -m ruff check src tests
python -m ruff format --check src tests
```

---

## 3. CLI Functional Test Sequence
Run the full demo workflow via CLI commands to ensure offline determinism:
```powershell
# 1. Config inspection
python -m ideaforge show-config

# 2. Case creation
python -m ideaforge --workspace workspace create-case "Conveyor Test"

# 3. Source ingestion
python -m ideaforge --workspace workspace ingest CASE_ID examples\demo_case\sources\demo_problem_brief.md

# 4. Artifact initialization & validation
python -m ideaforge --workspace workspace init-artifacts CASE_ID --title "Conveyor" --idea "Vibration test"
python -m ideaforge --workspace workspace validate CASE_ID

# 5. Kit building
python -m ideaforge --workspace workspace build-kit CASE_ID examples\demo_case\artifacts\experiment_plan.json

# 6. Analysis execution
python workspace\CASE_ID\versions\v001\experiment_kit\analysis.py workspace\CASE_ID\versions\v001\experiment_kit\data_template.csv
```

---

## 4. Manual Switch Console & Room Verification
- [ ] Local Switch server starts and reports healthy in Docker.
- [ ] Codex provider authenticated and signed in.
- [ ] Room `ideaforge-demo` created with all 4 agents.
- [ ] Mention `@forge-lead` $\to$ receives prompt response and intake.
- [ ] Lead visibly mentions `@evidence-scout` and `@red-team`.
- [ ] Specialists reply into the same room with distinct perspectives.
- [ ] Lead runs validator from working directory and displays output.
- [ ] Fault injection test: validator rejects bad locator, specialist repairs it, validator passes.
- [ ] Human confirms scope and approves final plan.
