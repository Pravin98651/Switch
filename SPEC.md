# IDEAForge 2.0 — Product Specification

> **Positioning:** Falsify Before You Fabricate  
> **Track:** Track 02 — Best Personal or Creative Workflow (Flip the Switch Hackathon)

---

## 1. Product Mission & Philosophy

Do not build IDEAForge as a generic multi-agent research assistant that accepts an idea and dumps a 50-page unverified report.

Build IDEAForge as a **human-led invention experiment studio**. Its core purpose is to take one rough engineering idea and help the user decide what the next meaningful, falsifiable experiment should be.

The product moves through this concrete transformation:
```text
idea → critical uncertainty → falsifiable test → executable experiment kit → human decision
```

---

## 2. The Five Product Pillars

### Pillar A — Claim Ledger
Every substantive statement in a case must be classified as one of:
- `SOURCE_BACKED`: Directly supported by an ingested source with a verifiable locator.
- `USER_PROVIDED`: Supplied directly by the human inventor.
- `INFERENCE`: Derived logically from established facts; reasoning must be explained.
- `ASSUMPTION`: Temporarily accepted for planning but unverified.
- `HYPOTHESIS`: The proposition that the proposed experiment is designed to test.
- `UNKNOWN`: Information not established by available evidence.

Never allow an assumption or inference to be presented as an established fact.

### Pillar B — Adversarial Review
The Red Team must not merely provide polite suggestions. It must actively attempt to disprove the proposed mechanism by identifying:
1. The 3 most consequential assumptions.
2. At least two plausible alternative explanations for the observed signal.
3. Physical confounding variables.
4. Measurement limitations.
5. Operating conditions under which the concept fails.
6. What empirical evidence would change its assessment.
7. Practical diagnostic tests for each uncertainty.

### Pillar C — Minimum Decisive Experiment (MDE)
The signature feature. The test engineer must design the smallest experiment that can meaningfully distinguish the proposed mechanism from at least one plausible alternative explanation.
- If the proposed measurements cannot distinguish the competing explanation, it is automatically downgraded to `PRELIMINARY_SCREENING` with explicit limitations noted.

### Pillar D — Executable Experiment Kit
The primary deliverable is a practical, executable package:
1. `experiment_card.md` — One-page human-readable experiment brief.
2. `experiment_plan.json` — Validated structured contract.
3. `data_template.csv` — Column headers with physical units for observations.
4. `analysis.py` — Fixed, deterministic starter analysis script (descriptive statistics only; no arbitrary LLM execution; no causal claims).
5. `source_ledger.json` & `source_ledger.md` — Cryptographic provenance and claim classifications.
6. `decision_record.md` — Human decision, rationale, timestamp, and next steps.
7. `dossier.md` — Consolidated audit dossier.

### Pillar E — Human Decision Gate
The human inventor decides among:
- `APPROVE_EXPERIMENT`
- `REQUEST_REVISION`
- `DEFER`
- `REJECT_EXPERIMENT`

The system records the decision and rationale. The dossier remains `DRAFT` until explicit approval is logged. Revisions create an immutable new version (`v002`).

---

## 3. Demo Scenario

**Conveyor belt early micro-tear defect detection using vibration and acoustic sensing.**
- Explores whether acoustic emission bursts (>20 kHz) can detect early mechanical defects before visual failure.
- Competes against alternative explanation: vibration amplitude scaling solely with roller RPM and motor harmonics.
- Experiment designs a 2x2 matrix (Baseline vs Defect at 1.0 m/s and 2.0 m/s) to isolate loop-period burst synchronization.

---

## 4. Explicit Out of Scope
- Legal opinions on patentability, novelty, freedom to operate, or filing readiness.
- Autonomous purchasing or external supply-chain orders.
- Unrestricted hardware control or direct machinery modification.
- Indiscriminate web crawling or vector RAG scraping.
