# IDEAForge 2.0 — Hackathon Submission Checklist

> **Track:** Track 02 — Best Personal or Creative Workflow (Flip the Switch Hackathon)

---

## 1. Track 02 & Switch Core Acceptance Criteria
- [x] A human can submit an engineering idea in a real Switch room (`ideaforge-demo`).
- [x] At least one real AI agent participates through Switch (supports all 4 specialist roles).
- [x] The room shows actual visible task delegation, handoffs, and collaborative discussion.
- [x] Evidence Scout ingests supplied sources and records valid locators (`line:N`, `page:N`) or marks them unavailable.
- [x] The Claim Ledger taxonomy distinguishes `SOURCE_BACKED`, `USER_PROVIDED`, `INFERENCE`, `ASSUMPTION`, `HYPOTHESIS`, and `UNKNOWN`.
- [x] Red Team identifies at least one specific confounder and plausible alternative explanation for the demo case.
- [x] Human confirmation gate prevents premature prototype planning until the critical uncertainty is confirmed.
- [x] Experiment Designer creates a structured test with independent, dependent, and controlled variables (all with physical units).
- [x] Decision rules explicitly distinguish support, rejection, and inconclusive outcomes.
- [x] If the test cannot distinguish the mechanism from alternatives, it is automatically downgraded to preliminary screening.
- [x] Executable Experiment Kit generated: `experiment_card.md`, `experiment_plan.json`, `data_template.csv`, fixed `analysis.py`, `source_ledger.md`, `decision_record.md`.
- [x] The analysis starter runs deterministically without executing model-generated code.
- [x] Human decision gate (`APPROVE_EXPERIMENT`, `REQUEST_REVISION`, `DEFER`, `REJECT_EXPERIMENT`) is recorded and persisted.
- [x] Revisions create an immutable new version (`v002`) rather than overwriting approved output.
- [x] Deliberate fault injection demonstrated and cleanly caught by the local validator.
- [x] README explains how Switch is used and provides reproducible steps.

---

## 2. Engineering & Repository Verification
- [x] Python test suite passes (`python -m pytest`).
- [x] Linting passes without errors (`python -m ruff check src tests`).
- [x] Code formatting verified (`python -m ruff format --check src tests`).
- [x] Clean installation tested from `pyproject.toml`.
- [x] Zero secrets, tokens, or private disclosures in repository or commit history.
- [x] Local `workspace/` and temporary artifacts excluded in `.gitignore`.

---

## 3. Presentation & Demo Deliverables
- [x] 3-Minute Demo Video recorded following `docs/DEMO_SCRIPT.md`.
- [x] Real Switch room screenshots captured from Mattermost.
- [x] Authentic failure case (deliberate locator fault injection) shown and repaired.
- [x] No fabricated benchmark metrics or claims of legal novelty/patentability.
