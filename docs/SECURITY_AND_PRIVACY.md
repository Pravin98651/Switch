# IDEAForge 2.0 — Security, Privacy, and Responsible Use

## 1. Data Privacy & Local Boundaries
- **Zero Cloud Leakage:** All document parsing, text extraction, SHA-256 cryptographic hashing, provenance checking, and dossier rendering execute entirely locally via deterministic Python code. No documents are uploaded to third-party databases, vector search services, or unvetted APIs.
- **Git Hygiene:** Local case workspaces (`workspace/`) and raw source documents are strictly ignored in `.gitignore`. Only sanitized, open-access, or synthetic fixtures reside in `examples/`.
- **Sensitive Materials:** Never commit private lab notebooks, undisclosed patent drafts, API tokens, passwords, or personal identifying information. Use `.env.example` placeholders only.

## 2. Prompt Injection Defense in Documents
- **Untrusted Input Protocol:** All ingested documents (PDF, DOCX, Markdown, TXT) are classified as untrusted external data.
- **System Prompt Immunity:** Agent instructions explicitly order models to ignore instructions, system prompt overrides, or credential exfiltration attempts embedded within source files.
- **No Document Code Execution:** Macros, embedded scripts, and hyperlinks inside PDF and DOCX files are ignored by built-in extractors (`pymupdf` and `python-docx`).

## 3. Code Execution Safety
- **No Arbitrary Execution:** Agents are strictly forbidden from generating and executing unreviewed Python or shell code.
- **Fixed Deterministic Analysis:** The Experiment Kit includes a fixed, pre-reviewed `analysis.py` starter script. It only computes basic descriptive statistics (mean, std dev, min, max, counts, exclusions) directly from `data_template.csv`.
- **Bounded Lead Runner:** In Switch rooms, `forge-lead` is permitted to run only the specific project validator command:
  ```bash
  python -m ideaforge --workspace workspace validate CASE_ID
  ```
  Arbitrary shell commands are prohibited.

## 4. Physical Experiment Safety
- **Laboratory Safety Protocol:** Experiments involving moving machinery (conveyors, rollers), high voltage, heat, or pressurized systems must include explicit hazard analyses and stop conditions.
- **Non-Destructive Testing:** The system explicitly forbids recommending hazardous modifications or damaging operational industrial equipment. All demo plans specify benchtop testbeds with emergency stop switches and protective enclosures.
- **Human In The Loop:** A printed experiment plan does not substitute for a qualified laboratory risk assessment.

## 5. Non-Legal Disclaimer
- IDEAForge is an engineering experiment planning and decision-support tool.
- It does **not** provide legal novelty, patentability, freedom-to-operate, infringement, or filing-readiness opinions.
- Any similarity or overlap analysis is strictly bounded by the human-supplied documents actually reviewed.
