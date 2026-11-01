# IDEAForge 2.0 — 8-Stage Operating Workflow

IDEAForge follows an 8-stage loop designed to reduce uncertainty through rigorous, falsifiable experimentation.

---

```text
Stage 1: INTAKE & PROBLEM NORMALIZATION (forge-lead + Human)
   │
   ▼
Stage 2: CLAIM LEDGER & PROVENANCE INGESTION (evidence-scout)
   │
   ▼
Stage 3: ADVERSARIAL CRITIQUE & COMPETING MECHANISMS (red-team)
   │
   ▼
Stage 4: CRITICAL UNCERTAINTY SELECTION (forge-lead + Human Scope Gate)
   │
   ▼
Stage 5: MINIMUM DECISIVE EXPERIMENT DESIGN (experiment-designer)
   │
   ▼
Stage 6: VALIDATION & EXPERIMENT KIT GENERATION (CLI + forge-lead)
   │
   ▼
Stage 7: HUMAN REVIEW & DECISION GATE (Human + forge-lead)
   │
   ▼
Stage 8: EXPERIMENT EXECUTION & DESCRIPTIVE ANALYSIS (Human + analysis.py)
```

---

## Stage-by-Stage Protocol

### Stage 1: Case Intake & Normalization
1. The human maker posts an engineering idea in the `ideaforge-demo` Switch room.
2. `forge-lead` preserves the user's idea text verbatim.
3. `forge-lead` assigns a unique Case ID (`IF-YYYYMMDD-NNN`) and initializes Version 1 (`v001`).
4. `forge-lead` normalizes the problem statement, system boundary, and constraints, asking at most two high-value clarifying questions if blocked.

### Stage 2: Claim Ledger & Provenance Ingestion
1. The maker attaches reference documents (TXT, MD, PDF, DOCX) to the room.
2. The local CLI ingests the files, hashes original bytes (`SHA-256`), and generates indexable locators (`line:N`, `page:N`, `paragraph:N`).
3. `evidence-scout` extracts claims, classifying each as `SOURCE_BACKED`, `USER_PROVIDED`, `INFERENCE`, `ASSUMPTION`, `HYPOTHESIS`, or `UNKNOWN`.
4. Source-backed claims must link to a valid Source ID and exact locator.

### Stage 3: Adversarial Review & Competing Explanations
1. `red-team` independently critiques the proposed concept without generic flattery.
2. Identifies the 3 most consequential assumptions that could invalidate the mechanism.
3. Proposes at least two plausible alternative explanations for the expected signal or effect.
4. Identifies physical confounders, measurement limitations, and conditions under which the concept fails.

### Stage 4: Critical Uncertainty Selection (Human Scope Gate)
1. `forge-lead` synthesizes evidence findings and red-team critiques into a ranked list of at most three critical uncertainties.
2. The human inventor confirms or selects which uncertainty to test first.
3. **Gate:** Experiment planning cannot proceed until human scope confirmation is recorded.

### Stage 5: Minimum Decisive Experiment (MDE) Design
1. `experiment-designer` designs the smallest test capable of distinguishing the proposed mechanism from the competing explanation.
2. Specifies independent, dependent, and controlled variables (all with units).
3. Defines a complete Bill of Materials (BOM), calibration steps, and step-by-step test procedure.
4. If the test cannot distinguish competing explanations, it is downgraded to `PRELIMINARY_SCREENING`.

### Stage 6: Provenance Validation & Experiment Kit Generation
1. `forge-lead` triggers local deterministic validation:
   ```bash
   python -m ideaforge --workspace workspace validate CASE_ID
   ```
2. The validator verifies that all cited Source IDs exist and locators match the extracted text manifest.
3. Generates the Executable Experiment Kit:
   - `experiment_card.md`
   - `experiment_plan.json`
   - `data_template.csv`
   - `analysis.py`
   - `source_ledger.md`
   - `decision_record.md`

### Stage 7: Human Decision Gate
1. The human reviews the Experiment Card and draft dossier.
2. The human records an explicit decision:
   - `APPROVE_EXPERIMENT`
   - `REQUEST_REVISION`
   - `DEFER`
   - `REJECT_EXPERIMENT`
3. On approval, the dossier is marked `APPROVED`.
4. On revision, an immutable new version (`v002`) is created (`python -m ideaforge new-version CASE_ID`). Previous versions are never modified or overwritten.

### Stage 8: Execution & Descriptive Analysis
1. The human maker runs the physical benchtop experiment using `data_template.csv`.
2. The human executes `python analysis.py data_template.csv`.
3. The deterministic script computes descriptive statistics (n, mean, std dev, min, max, excluded rows).
4. Results are compared against pre-registered acceptance criteria without retroactively altering the hypothesis.
