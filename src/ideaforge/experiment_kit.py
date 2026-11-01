"""Deterministic Experiment Kit renderer and fixed CSV analysis starter."""

from __future__ import annotations

import csv
import json
import re
from pathlib import Path

from .models import EvidenceMatrix, ExperimentPlan
from .rendering import compute_epistemic_ledger, format_epistemic_ledger

FIXED_ANALYSIS = '''"""Exploratory descriptive analysis; this file does not infer causality."""
from __future__ import annotations

import argparse
import csv
import math
from pathlib import Path


def analyze(path: Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(f"Data file not found: {path}")
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        if not reader.fieldnames:
            raise ValueError("CSV needs a header row")
        fieldnames = list(reader.fieldnames)
        rows = list(reader)
    if not rows:
        return {
            "label": "EXPLORATORY_ONLY",
            "rows": 0,
            "numeric": {},
            "excluded_rows": 0,
            "exclusion_note": "No rows to analyze.",
            "causal_claim": False,
        }
    numeric = {}
    excluded = set()
    for column in fieldnames:
        values = []
        for index, row in enumerate(rows):
            raw = (row.get(column) or "").strip()
            if not raw:
                excluded.add(index)
                continue
            try:
                value = float(raw)
            except ValueError:
                continue
            if not math.isfinite(value):
                excluded.add(index)
                continue
            values.append(value)
        if values:
            n = len(values)
            mean = sum(values) / n
            variance = sum((x - mean) ** 2 for x in values) / (n - 1) if n > 1 else 0.0
            std_dev = math.sqrt(variance)
            numeric[column] = {
                "n": n,
                "mean": round(mean, 4),
                "std_dev": round(std_dev, 4),
                "min": round(min(values), 4),
                "max": round(max(values), 4),
            }
    return {
        "label": "EXPLORATORY_ONLY",
        "rows": len(rows),
        "numeric": numeric,
        "excluded_rows": len(excluded),
        "exclusion_note": "Rows with blank or non-finite numeric values are counted once.",
        "causal_claim": False,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fixed exploratory descriptive analysis")
    parser.add_argument("csv_file", nargs="?", default="data_template.csv")
    args = parser.parse_args()
    result = analyze(Path(args.csv_file))
    print(result)
'''


def _slug(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_-]+", "_", value).strip("_") or "experiment"


def render_card(plan: ExperimentPlan, epistemic_summary: str = "") -> str:
    list_items = lambda items: (
        "\n".join(f"{i}. {value}" for i, value in enumerate(items, 1))
        if items
        else "- None recorded."
    )
    ledger_line = (
        f"- **Epistemic Ledger:** `{epistemic_summary}`\n"
        if epistemic_summary
        else "- **Epistemic Ledger:** `Computed from Evidence Matrix`\n"
    )

    var_rows = []
    for item in plan.independent_variables:
        var_rows.append(f"| Independent (What changes) | `{item.name}` | `{item.unit}` |")
    for item in plan.dependent_variables:
        var_rows.append(f"| Dependent (What is measured) | `{item.name}` | `{item.unit}` |")
    for item in plan.control_variables:
        var_rows.append(f"| Control (What stays constant) | `{item.name}` | `{item.unit}` |")
    vars_table = "\n".join(var_rows)

    return f"""# Experiment Card -- {plan.title}

> **PRIMARY DELIVERABLE -- MINIMUM DECISIVE EXPERIMENT**  
> *Execute this protocol on the test bench. The full 20+ section dossier (`dossier.md`) serves as the comprehensive technical validation appendix.*

- **Case ID:** {plan.case_id}
- **Experiment ID:** {plan.experiment_id}
- **Version:** v{plan.version:03d}
- **Status:** `{plan.human_status}`
- **Experiment Type:** `{plan.experiment_type.value}`
{ledger_line}
---

## 1. Core Question & Distinction
**What specific uncertainty does this test address?**  
Distinguishes the proposed physical mechanism from plausible alternative explanations before building full hardware.

- **Proposed Hypothesis:**  
  > {plan.hypothesis}
- **Competing Alternative Explanation:**  
  > {plan.alternative_explanation}
{"- **MDE Rationale:** " + plan.mde_rationale if plan.mde_rationale else ""}

---

## 2. Variables & Instrumentation
| Category | Variable Name | Unit |
|:---|:---|:---|
{vars_table}

---

## 3. Equipment & Bill of Materials
{list_items(plan.equipment)}

---

## 4. Setup, Calibration & Protocol
### Calibration Steps
{list_items(plan.calibration_steps)}

### Step-by-Step Procedure
{list_items(plan.procedure)}

---

## 5. Decision Rules (Go / No-Go Criteria)
| Outcome | Empirical Result | Next Action |
|:---|:---|:---|
| **SUPPORTS** | {plan.criteria.supports} | Proceed to integrated prototype |
| **WEAKENS / REJECTS** | {plan.criteria.weakens} | Falsify mechanism; revise or abort |
| **INCONCLUSIVE** | {plan.criteria.inconclusive} | Recalibrate instruments or increase SNR |

---

## 6. Data Collection & Fixed Analysis
- **CSV Data Template:** `data_template.csv`
- **Analysis Method:** {plan.analysis_method}
- **Analysis Starter:** `python analysis.py data_template.csv` *(fixed descriptive statistics; no model-generated arbitrary code)*

---

## 7. Safety Notes & Known Limitations
### Safety Requirements
{list_items(plan.safety_notes or ["No safety review recorded; competent human review required."])}

### Known Limitations
{list_items(plan.limitations)}

### Consequential Assumptions
{list_items(plan.assumptions)}

---

## 8. Human Decision
- **Status:** `{plan.human_status}`  
- **Registered Decision Options:** `APPROVE_EXPERIMENT` | `REQUEST_REVISION` | `DEFER` | `REJECT_EXPERIMENT`  
*(All approvals are pre-registered with SHA-256 cryptographic hashes preventing post-decision tampering.)*
"""


def render_source_ledger_markdown(ledger: EvidenceMatrix) -> str:
    lines = [
        f"# Source Ledger — {ledger.meta.case_id} v{ledger.meta.version:03d}",
        "",
        "Every claim is classified by evidence provenance.",
        "",
        "| ID | Type | Claim | Source ID | Locator | Confidence | Status |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    if not ledger.items:
        lines.append("| — | — | No ledger items recorded | — | — | — | — |")
    else:
        for idx, item in enumerate(ledger.items, 1):
            claim_id = item.claim_id or f"CLM-{idx:03d}"
            lines.append(
                f"| {claim_id} | {item.fact_type.value} | {item.claim} | {item.source_id or '—'} | {item.locator or '—'} | {item.confidence} | {item.status} |"
            )
    return "\n".join(lines) + "\n"


def render_decision_record_markdown(
    case_id: str,
    version: int,
    status: str = "PENDING_REVIEW",
    actor: str = "human",
    rationale: str = "Awaiting human review.",
) -> str:
    return f"""# Human Experiment Decision Record

- Case ID: {case_id}
- Version: v{version:03d}
- Status: {status}
- Actor: {actor}

## Decision
{status}

## Rationale
{rationale}

## Next Step
If approved, execute the protocol in `experiment_card.md` using `data_template.csv` and `analysis.py`.
If revision requested, create a new version with `python -m ideaforge new-version {case_id}`.
"""


def write_experiment_kit(
    output_dir: str | Path,
    plan: ExperimentPlan,
    ledger: EvidenceMatrix,
    decision_status: str = "PENDING_REVIEW",
    decision_rationale: str = "Awaiting human review.",
    decision_actor: str = "human",
    epistemic_summary: str = "",
) -> list[Path]:
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    if not epistemic_summary and ledger and ledger.items:
        epistemic_summary = format_epistemic_ledger(compute_epistemic_ledger(ledger))
    columns = [
        "run_id (unitless)",
        "trial_number (unitless)",
        "timestamp (ISO-8601)",
        "condition (text)",
    ]
    columns.extend(f"{_slug(item.name)} ({item.unit})" for item in plan.data_schema)
    columns.append("notes (text)")

    files = {
        "experiment_plan.json": plan.model_dump(mode="json"),
        "source_ledger.json": ledger.model_dump(mode="json"),
    }
    paths = []
    for name, data in files.items():
        path = output / name
        path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        paths.append(path)

    card = output / "experiment_card.md"
    card.write_text(render_card(plan, epistemic_summary=epistemic_summary), encoding="utf-8")
    paths.append(card)

    template = output / "data_template.csv"
    with template.open("w", encoding="utf-8", newline="") as stream:
        csv.writer(stream).writerow(columns)
    paths.append(template)

    analysis = output / "analysis.py"
    analysis.write_text(FIXED_ANALYSIS, encoding="utf-8")
    paths.append(analysis)

    ledger_md = output / "source_ledger.md"
    ledger_md.write_text(render_source_ledger_markdown(ledger), encoding="utf-8")
    paths.append(ledger_md)

    decision_md = output / "decision_record.md"
    decision_md.write_text(
        render_decision_record_markdown(
            plan.case_id, plan.version, decision_status, decision_actor, decision_rationale
        ),
        encoding="utf-8",
    )
    paths.append(decision_md)

    return paths
