# Conveyor belt early micro-tear defect detection

- **Case ID:** IF-20261101-001
- **Version:** v001
- **Status:** APPROVED
- **Epistemic Ledger:** 2 source-backed, 0 inferences, 0 assumptions, 0 unknowns, 1 hypotheses
- **Confidentiality:** Standard (non-confidential / public sources)
- **Generated:** 2026-11-02T00:00:00+00:00

---

## 1. Executive summary

IDEAForge is a human-led invention experiment studio: **Falsify Before You Fabricate**.
The primary actionable deliverable of this workflow is the one-page **Experiment Card** (`experiment_card.md`), located in the Experiment Kit.
This comprehensive dossier serves as the authoritative **technical verification appendix**, consolidating the user's idea, ingested source evidence, deterministic epistemic ledger, independent red-team critique, prototype plan, and minimal decisive experiment specification.
*Notice: This document provides technical exploration and experiment planning only. It does not provide legal conclusions regarding patentability, novelty, freedom to operate, or regulatory compliance.*

## 2. User's original idea (verbatim)

> Explore whether a combination of vibration and acoustic measurements can help identify an early mechanical defect in a conveyor-belt test setup before visible tear occurs.

## 3. Normalized problem statement

Early mechanical degradation and micro-tears in moving conveyor belts are visually imperceptible until catastrophic tearing occurs.

## 4. Target user, operating environment, and system boundary

- **Target user:** Industrial maintenance engineers and maker testbed operators.
- **Operating environment:** Benchtop conveyor test rig with acoustic motor noise and roller vibration.
- **System boundary:** Benchtop conveyor rig, accelerometer, contact acoustic sensor, and data logging DAQ.

## 5. Proposed technical mechanism and intended outcome

- **Proposed mechanism:** Localized micro-defects generate high-frequency acoustic emission bursts (>20 kHz) and transient vibration spikes when passing over rollers.
- **Intended outcome:** A reproducible detection threshold that distinguishes defect-induced signals from normal roller speed variations.

## 6. Constraints and known unknowns

### Constraints
- Benchtop apparatus only (1.2m loop)
- Non-destructive artificial defect only
- Maximum speed 2.5 m/s
- Low-cost sensors and DAQ

### Known unknowns
- Whether acoustic burst amplitude is overwhelmed by motor bearing noise
- Whether vibration spikes vary primarily with roller RPM rather than defect presence

## 7. Assumption register

Every assertion lacking a verified source ID and locator is classified as `ASSUMPTION` or `INFERENCE` until empirically tested:
- Prioritize testing assumptions that would falsify the concept if incorrect.
- Never treat an inference or assumption as established fact.

## 8. Evidence matrix (Pillar A — Claim Ledger)

| ID | Type | Claim | Source ID | Locator | Confidence |
| --- | --- | --- | --- | --- | --- |
| CLM-001 | SOURCE_BACKED | Acoustic emission sensor frequency band covers 20 kHz to 100 kHz for ultrasonic contact detection. | SRC-DA8D5C538812 | line:7 | high |
| CLM-002 | SOURCE_BACKED | Accelerometer stud torque must be calibrated to 2.5 Nm (+/- 0.2 Nm). | SRC-A9FF21CAB49C | line:3 | high |
| CLM-003 | HYPOTHESIS | Defect-induced stress concentration produces transient acoustic burst on every roller pass. | — | — | medium |

## 9. Related work and overlap analysis

Review is strictly bounded by user-supplied and room-attached documents. No exhaustive web or prior-art patent search is claimed or implied.

- Can the experiment isolate belt defect bursts from drive roller bearing harmonics without narrow bandpass filtering?
- What minimum defect dimension generates a detectable signal above the motor noise floor?

## 10. Red-team critique and adversarial review (Pillar B)

### Most Consequential Assumptions Challenged
- Assumption 1: Artificial surface defect generates a distinct acoustic burst distinguishable from motor bearing hum.
- Assumption 2: Belt tension remains constant across speed variations.
- Assumption 3: Accelerometer mounting housing provides rigid mechanical coupling up to 10 kHz.

### Competing Explanations & Alternative Mechanisms
- Vibration amplitude increase is driven strictly by roller eccentricity and motor RPM rather than belt defect.
- Acoustic emissions are caused by belt slip on drive roller under varying tension, not defect micro-cracking.

### Confounding Variables
- Belt operating speed (0.5 m/s vs 2.0 m/s alters passing frequency and background noise).
- Ambient room acoustic noise and benchtop structural resonance.
- Sensor contact pressure and couplant dry-out over time.

### Measurement Limitations
- DAQ sampling rate must sustain 200 kS/s to prevent aliasing of 100 kHz signals.
- Accelerometers mounted on external bearing blocks suffer mechanical low-pass filtering through the housing.

### Failure Modes & Conditions Under Which Concept Fails
- Acoustic burst signal is completely masked by drive motor PWM electrical noise and bearing friction.
- Sensor mounting compliance dampens ultrasonic frequencies above 20 kHz.
- False alarms triggered by normal belt seam or splice pass rather than a defect.
- Belt speeds below 0.3 m/s generate insufficient strain energy to trigger acoustic emissions.
- Operation in dusty or contaminated environments dampens acoustic contact.

### Evidence That Would Change Assessment
- A controlled 2x2 comparison (Baseline vs Defect at 1.0 m/s and 2.0 m/s) where periodic bursts synchronize with belt circulation period only when the defect is installed.

### Practical Diagnostic Tests
- Run benchtop conveyor at 1.0 m/s and 2.0 m/s without defect; verify baseline noise floor.
- Install artificial defect clip; measure whether acoustic burst amplitude exceeds baseline by >6 dB with periodicity T = 1.2m / V.

## 11. Proposed prototype architecture

Benchtop conveyor testbed with 1.2 m synthetic belt loop, brushless DC motor, piezo accelerometer on idler bearing housing, and ultrasonic acoustic sensor clamped to belt surface guide.

## 12. Bill of materials (BOM)

| Item | Qty | Purpose | Specification | Estimate Source | Confidence |
| --- | --- | --- | --- | --- | --- |
| Ultrasonic Contact Acoustic Sensor (20-100 kHz) | 1 | Detect high-frequency localized acoustic emissions from defect passing | Resonant frequency ~40 kHz, integral preamplifier | Laboratory stock | high |
| Piezoelectric Accelerometer | 1 | Measure structural idler roller bearing vibration | 100 mV/g, 10-10000 Hz | Laboratory stock | high |
| Benchtop Conveyor Loop Assembly | 1 | Provide controlled speed mechanical belt transport | 1.2 m loop, 24V brushless motor, PWM controller | Existing testbed | high |
| 2-Channel USB DAQ | 1 | Synchronous high-speed digitizing of acoustic and vibration channels | >=250 kS/s, 16-bit resolution | Laboratory stock | high |

## 13. Experimental hypothesis & Minimum Decisive Experiment (Pillar C)

- **Primary hypothesis:** An artificial surface defect produces periodic ultrasonic bursts (>25 kHz) synchronized with belt circulation (T = L / V), distinguishable from roller speed-dependent baseline noise.
- **Objective:** The smallest useful experiment to meaningfully distinguish the proposed mechanism from plausible alternative explanations.

## 14. Variables

- **Independent variable(s) (what changes):** Defect presence (baseline vs 1 mm artificial notch), Belt speed (1.0 m/s vs 2.0 m/s)
- **Dependent variable(s) (what is measured):** Peak ultrasonic acoustic amplitude (mV), Burst periodicity (seconds), Vibration RMS acceleration (m/s^2)
- **Controlled variable(s) (what stays constant):** Belt tension (calibrated to 150 N), Sensor mounting torque (2.5 Nm), Acoustic sensor clamp force (5 N with silicone couplant)

## 15. Equipment, calibration, and test protocol

### Equipment required
- 1.2 m benchtop conveyor rig with variable speed DC drive
- High-frequency contact acoustic emission sensor (20-100 kHz)
- Piezoelectric accelerometer (100 mV/g, 10-10000 Hz)
- 2-channel USB DAQ (minimum 250 kS/s sampling rate)
- Removable artificial notch test fixture (1 mm notch)

### Calibration checks
- Zero sensors at standstill (record stationary noise floor).
- Calibrate accelerometer mounting torque to 2.5 Nm using torque wrench.
- Verify acoustic sensor couplant contact pressure with 5 N clamp gauge.

### Step-by-step protocol
- 1. Power on DAQ and initiate background noise logging for 10 seconds at 0 m/s.
- 2. Run baseline condition without defect at 1.0 m/s for 30 seconds; log channels.
- 3. Run baseline condition without defect at 2.0 m/s for 30 seconds; log channels.
- 4. Stop motor, install 1 mm artificial defect clip at marker position on belt.
- 5. Run defect condition at 1.0 m/s for 30 seconds; log channels.
- 6. Run defect condition at 2.0 m/s for 30 seconds; log channels.
- 7. Export raw data to data_template.csv and execute analysis.py.

## 16. Measurement, sample size, and acceptance criteria

- **Measurement plan:** Record time-series at 250 kS/s. Extract peak acoustic amplitude and burst repetition frequency. Calculate descriptive statistics (mean, std dev, min, max) for each trial condition.
- **Sample-size rationale:** 5 continuous belt cycles per condition (30 seconds per run at 1-2 m/s provides 25-50 cycles), sufficient for descriptive signal-to-noise ratio assessment.

### Acceptance criteria (Decision rules)
- Supports hypothesis if: Periodic acoustic burst amplitude exceeds baseline mean by >=6 dB and burst period matches T = 1.2m / V across both 1.0 m/s and 2.0 m/s.
- Weakens hypothesis if: Acoustic amplitude does not exceed baseline noise floor, or amplitude scales only with speed regardless of defect presence.
- Inconclusive if: Signal-to-noise ratio is below 6 dB or sensor mounting slips during run.

## 17. Safety, ethics, and limitations

### Safety measures
- Benchtop safety shield must be closed during belt operation.
- Emergency stop button within immediate operator reach.
- Keep hands and loose clothing clear of rotating rollers and nip points.

### Limitations
- Does not test long-term durability.
- Laboratory benchtop data cannot be directly extrapolated to industrial duty cycles without further testing.

## 18. Human decisions and approval log (Pillar E)

- **2026-11-01T19:58:41.346128+00:00** — Actor: `lead_inventor` | Decision: `APPROVE_EXPERIMENT` | Statement: Risks acceptable for benchtop test rig; acceptance criteria locked at 6dB harmonic threshold.

## 19. Next recommended experiment

Execute the Experiment Kit (`experiment_card.md`) using `data_template.csv` and `analysis.py`.
Inspect outcomes against pre-registered acceptance criteria. If revision is necessary, create a new version (`python -m ideaforge new-version IF-20261101-001`).

## 20. Sources and references

| Source ID | File | Media Type | SHA-256 | Status |
| --- | --- | --- | --- | --- |
| SRC-9C654DA2C768 | demo_problem_brief.md | text/markdown | `9c654da2c768...` | success |
| SRC-DA8D5C538812 | demo_sensor_notes.md | text/markdown | `da8d5c538812...` | success |
| SRC-3FD09DD13C67 | demo_experiment_constraints.md | text/markdown | `3fd09dd13c67...` | success |
| SRC-A9FF21CAB49C | demo_fault_injection_source.md | text/markdown | `a9ff21cab49c...` | success |
| SRC-D97825AB4806 | demo_hostile_source.md | text/markdown | `d97825ab4806...` | success |

## 21. Appendix: machine-readable artifacts & kit files

- `00_idea_brief.json`
- `01_evidence_matrix.json`
- `02_critical_review.json`
- `03_prototype_plan.json`
- `validation_report.json`
- `decision_log.json`
- `experiment_kit/experiment_card.md`
- `experiment_kit/experiment_plan.json`
- `experiment_kit/data_template.csv`
- `experiment_kit/analysis.py`
- `experiment_kit/source_ledger.md`
- `experiment_kit/decision_record.md`
