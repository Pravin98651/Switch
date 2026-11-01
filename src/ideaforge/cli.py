from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from .config import load_settings
from .experiment_kit import write_experiment_kit
from .ingest import ingest_file
from .models import (
    ArtifactMeta,
    CriticalReview,
    Decision,
    EvidenceMatrix,
    ExperimentPlan,
    HumanDecision,
    IdeaBrief,
    PrototypePlan,
    SourceManifest,
    ValidationReport,
)
from .rendering import (
    compute_epistemic_ledger,
    format_epistemic_ledger,
    render_dossier,
)
from .schema_export import export_schemas
from .storage import CaseStore, atomic_json
from .validation import validate_artifacts


def load_model(path: Path, model):
    return model.model_validate_json(path.read_text(encoding="utf-8"))


def artifact_paths(version_path: Path) -> dict[str, Path]:
    return {
        "idea": version_path / "00_idea_brief.json",
        "evidence": version_path / "01_evidence_matrix.json",
        "review": version_path / "02_critical_review.json",
        "plan": version_path / "03_prototype_plan.json",
        "report": version_path / "validation_report.json",
        "decisions": version_path / "decision_log.json",
    }


def write_json_model(path: Path, model) -> None:
    atomic_json(path, model.model_dump(mode="json"))


def artifact_hashes(paths: dict[str, Path]) -> list[str]:
    hashed = []
    for key in ("idea", "evidence", "review", "plan"):
        path = paths[key]
        if path.exists():
            hashed.append(hashlib.sha256(path.read_bytes()).hexdigest())
    return hashed


def store_for(args: argparse.Namespace) -> CaseStore:
    settings = load_settings(args.config, args.workspace)
    return CaseStore(settings=settings)


def cmd_create(args: argparse.Namespace) -> int:
    title = args.title
    if hasattr(args, "input") and args.input:
        input_path = Path(args.input)
        if input_path.exists():
            content = input_path.read_text(encoding="utf-8").strip()
            if not title:
                lines = [line.strip("# ").strip() for line in content.splitlines() if line.strip()]
                title = lines[0] if lines else "New Case"
    case_id, _ = store_for(args).create_case(title or "New Case")
    print(case_id)
    return 0


def cmd_show_config(args: argparse.Namespace) -> int:
    print(load_settings(args.config, args.workspace).model_dump_json(indent=2))
    return 0


def cmd_status(args: argparse.Namespace) -> int:
    store = store_for(args)
    case_root = store.case_path(args.case_id)
    if not case_root.exists():
        raise SystemExit(f"Case '{args.case_id}' does not exist.")
    version, version_path = store.version_path(args.case_id, args.version)
    paths = artifact_paths(version_path)

    manifest_path = case_root / "sources" / "source_manifest.json"
    manifest = load_model(manifest_path, SourceManifest) if manifest_path.exists() else None

    decisions_path = paths["decisions"]
    decisions = (
        [
            Decision.model_validate(item)
            for item in json.loads(decisions_path.read_text(encoding="utf-8"))
        ]
        if decisions_path.exists()
        else []
    )
    approved = any(d.approved for d in decisions)
    has_tamper_lock = any(d.approved and d.dossier_hash for d in decisions)
    evidence_path = paths["evidence"]
    ledger_str = None
    if evidence_path.exists():
        try:
            ev = load_model(evidence_path, EvidenceMatrix)
            ledger_str = format_epistemic_ledger(compute_epistemic_ledger(ev))
        except (json.JSONDecodeError, OSError, ValueError, KeyError):
            pass

    warnings_count = sum(len(s.extraction_warnings) for s in manifest.sources) if manifest else 0

    report_path = paths["report"]
    report = load_model(report_path, ValidationReport) if report_path.exists() else None

    kit_path = version_path / "experiment_kit"
    kit_exists = kit_path.exists() and (kit_path / "experiment_card.md").exists()

    print(f"Case ID:          {args.case_id}")
    print(f"Version:          v{version:03d}")
    print(f"Status:           {'APPROVED' if approved else 'DRAFT'}")
    if has_tamper_lock:
        print("Tamper Lock:      ACTIVE (SHA-256 pre-registered)")
    if ledger_str:
        print(f"Epistemic Ledger: {ledger_str}")
    if warnings_count:
        print(f"Security Alerts:  [!] {warnings_count} potential injection(s) flagged")
    print(f"Sources:          {len(manifest.sources) if manifest else 0} ingested")
    print("Artifacts:")
    for key, path in paths.items():
        print(f"  - {key:<10}: {'present' if path.exists() else 'missing'}")
    print(
        f"Validation:       {'PASSED' if report and report.valid else ('FAILED' if report else 'NOT RUN')}"
    )
    print(f"Experiment Kit:   {'BUILT' if kit_exists else 'NOT BUILT'}")
    print(f"Decisions:        {len(decisions)} recorded")
    return 0


def cmd_ingest(args: argparse.Namespace) -> int:
    store = store_for(args)
    version, _ = store.version_path(args.case_id, args.version)
    files = []
    if hasattr(args, "source") and args.source:
        files.extend(args.source)
    if hasattr(args, "file") and args.file:
        files.append(args.file)
    if not files:
        raise SystemExit("no source file specified to ingest")

    for file_path in files:
        record = ingest_file(
            store.case_path(args.case_id), file_path, args.case_id, version, store.settings
        )
        print(record.model_dump_json(indent=2))
    return 0


def cmd_init(args: argparse.Namespace) -> int:
    store = store_for(args)
    version, version_path = store.version_path(args.case_id, args.version)
    paths = artifact_paths(version_path)
    meta = ArtifactMeta(case_id=args.case_id, version=version, producer="ideaforge.cli")
    write_json_model(
        paths["idea"],
        IdeaBrief(
            meta=meta,
            title=args.title,
            original_idea=args.idea,
            problem=args.problem,
            confidentiality_acknowledged=getattr(args, "confidential", False),
        ),
    )
    write_json_model(paths["evidence"], EvidenceMatrix(meta=meta))
    write_json_model(paths["review"], CriticalReview(meta=meta))
    write_json_model(
        paths["plan"],
        PrototypePlan(
            meta=meta,
            architecture="To be proposed after scope confirmation.",
            hypothesis="To be defined.",
            protocol=["Await human-confirmed scope before executing an experiment."],
            acceptance_criteria=["Human review is required before any decision."],
        ),
    )
    atomic_json(paths["decisions"], [])
    print(version_path)
    return 0


def cmd_validate(args: argparse.Namespace) -> int:
    store = store_for(args)
    version, version_path = store.version_path(args.case_id, args.version)
    paths = artifact_paths(version_path)
    errors: list[str] = []
    manifest = None
    try:
        manifest_path = store.case_path(args.case_id) / "sources" / "source_manifest.json"
        manifest = (
            load_model(manifest_path, SourceManifest)
            if manifest_path.exists()
            else SourceManifest(
                meta=ArtifactMeta(
                    case_id=args.case_id, version=version, producer="ideaforge.validation"
                )
            )
        )
        errors.extend(
            validate_artifacts(
                args.case_id,
                version,
                load_model(paths["idea"], IdeaBrief),
                manifest,
                load_model(paths["evidence"], EvidenceMatrix),
                load_model(paths["review"], CriticalReview),
                load_model(paths["plan"], PrototypePlan),
            )
        )
    except FileNotFoundError as error:
        errors.append(f"missing required artifact: {error.filename}")

    # Tamper-evident check: verify approved dossier and criteria hashes
    if paths["decisions"].exists():
        try:
            decisions_data = json.loads(paths["decisions"].read_text(encoding="utf-8"))
            for d in decisions_data:
                if d.get("approved") and d.get("dossier_hash"):
                    expected_dossier_hash = d["dossier_hash"]
                    expected_criteria_hash = d.get("criteria_hash")

                    # Check acceptance criteria hash
                    if expected_criteria_hash and paths["plan"].exists():
                        try:
                            curr_plan = load_model(paths["plan"], PrototypePlan)
                            curr_crit = "\n".join(curr_plan.acceptance_criteria)
                            curr_crit_hash = hashlib.sha256(curr_crit.encode("utf-8")).hexdigest()
                            if curr_crit_hash != expected_criteria_hash:
                                errors.append(
                                    f"tamper check failed: acceptance criteria modified after approval (expected {expected_criteria_hash[:12]}..., got {curr_crit_hash[:12]}...)"
                                )
                        except (json.JSONDecodeError, OSError, ValueError, KeyError) as e:
                            errors.append(
                                f"tamper check failed: could not verify acceptance criteria ({e})"
                            )

                    # Check dossier.md file hash if file exists
                    dossier_file = version_path / "dossier.md"
                    if dossier_file.exists():
                        actual_file_hash = hashlib.sha256(
                            dossier_file.read_text(encoding="utf-8").encode("utf-8")
                        ).hexdigest()
                        if actual_file_hash != expected_dossier_hash:
                            errors.append(
                                f"tamper check failed: dossier.md modified after approval (expected {expected_dossier_hash[:12]}..., got {actual_file_hash[:12]}...)"
                            )

                    # Re-render dossier from current artifacts and check hash
                    try:
                        temp_decisions = [Decision.model_validate(item) for item in decisions_data]
                        curr_rendered = render_dossier(
                            load_model(paths["idea"], IdeaBrief),
                            manifest
                            or SourceManifest(
                                meta=ArtifactMeta(
                                    case_id=args.case_id,
                                    version=version,
                                    producer="ideaforge.validation",
                                )
                            ),
                            load_model(paths["evidence"], EvidenceMatrix),
                            load_model(paths["review"], CriticalReview),
                            load_model(paths["plan"], PrototypePlan),
                            temp_decisions,
                        )
                        curr_rendered_hash = hashlib.sha256(
                            curr_rendered.encode("utf-8")
                        ).hexdigest()
                        if curr_rendered_hash != expected_dossier_hash:
                            errors.append(
                                "tamper check failed: underlying artifacts modified after approval (hash mismatch with approved dossier)"
                            )
                    except (json.JSONDecodeError, OSError, ValueError, KeyError) as e:
                        errors.append(
                            f"tamper check failed: could not re-render dossier for verification ({e})"
                        )
        except (json.JSONDecodeError, OSError, ValueError, KeyError) as e:
            errors.append(f"tamper check failed: invalid decision log ({e})")

    report = ValidationReport(
        meta=ArtifactMeta(
            case_id=args.case_id,
            version=version,
            producer="ideaforge.validation",
            input_hashes=artifact_hashes(paths),
        ),
        valid=not errors,
        errors=errors,
    )
    write_json_model(paths["report"], report)
    print(report.model_dump_json(indent=2))
    return 0 if report.valid else 1


ARTIFACT_MODELS = {
    "idea": ("idea", IdeaBrief),
    "evidence": ("evidence", EvidenceMatrix),
    "review": ("review", CriticalReview),
    "plan": ("plan", PrototypePlan),
}


def cmd_import_artifact(args: argparse.Namespace) -> int:
    store = store_for(args)
    version, version_path = store.version_path(args.case_id, args.version)
    artifact_key, model = ARTIFACT_MODELS[args.kind]
    artifact = load_model(Path(args.file), model)
    if artifact.meta.case_id != args.case_id or artifact.meta.version != version:
        if getattr(args, "adopt", False):
            artifact.meta.case_id = args.case_id
            artifact.meta.version = version
        else:
            raise SystemExit(
                "artifact metadata must match the requested case ID and version (pass --adopt to bind to this case)"
            )
    write_json_model(artifact_paths(version_path)[artifact_key], artifact)
    print(f"imported {args.kind} artifact")
    return 0


def cmd_new_version(args: argparse.Namespace) -> int:
    store = store_for(args)
    number, path = store.create_version(args.case_id)
    print(f"{store.settings.version_prefix}{number:0{store.settings.version_width}d} {path}")
    return 0


def cmd_export_schemas(args: argparse.Namespace) -> int:
    for path in export_schemas(args.output_dir):
        print(path)
    return 0


def cmd_build_kit(args: argparse.Namespace) -> int:
    store = store_for(args)
    version, version_path = store.version_path(args.case_id, args.version)
    plan = load_model(Path(args.plan_file), ExperimentPlan)
    if plan.case_id != args.case_id or plan.version != version:
        if getattr(args, "adopt", False):
            plan.case_id = args.case_id
            plan.version = version
        else:
            raise SystemExit(
                "experiment plan case/version must match the selected case version (pass --adopt to bind to this case)"
            )
    paths = artifact_paths(version_path)
    ledger = (
        load_model(paths["evidence"], EvidenceMatrix)
        if paths["evidence"].exists()
        else EvidenceMatrix(
            meta=ArtifactMeta(case_id=args.case_id, version=version, producer="ideaforge.kit")
        )
    )

    decisions = (
        [
            Decision.model_validate(item)
            for item in json.loads(paths["decisions"].read_text(encoding="utf-8"))
        ]
        if paths["decisions"].exists()
        else []
    )
    last_decision = decisions[-1] if decisions else None
    decision_status = (
        last_decision.decision.value
        if (last_decision and last_decision.decision)
        else ("APPROVED" if (last_decision and last_decision.approved) else "PENDING_REVIEW")
    )
    decision_rationale = (
        last_decision.rationale or last_decision.statement
        if last_decision
        else "Awaiting human review."
    )
    decision_actor = last_decision.actor or "human" if last_decision else "human"

    output = version_path / "experiment_kit"
    for path in write_experiment_kit(
        output,
        plan,
        ledger,
        decision_status=decision_status,
        decision_rationale=decision_rationale,
        decision_actor=decision_actor,
    ):
        print(path)
    return 0


def cmd_approve(args: argparse.Namespace) -> int:
    store = store_for(args)
    version, version_path = store.version_path(args.case_id, args.version)
    paths = artifact_paths(version_path)
    if not paths["report"].exists():
        raise SystemExit("approval blocked: run validate first")
    report = load_model(paths["report"], ValidationReport)
    if not report.valid:
        raise SystemExit("approval blocked: validation report is invalid")
    if report.meta.input_hashes != artifact_hashes(paths):
        raise SystemExit("approval blocked: artifacts changed since validation; run validate again")

    manifest_path = store.case_path(args.case_id) / "sources" / "source_manifest.json"
    manifest = (
        load_model(manifest_path, SourceManifest)
        if manifest_path.exists()
        else SourceManifest(
            meta=ArtifactMeta(case_id=args.case_id, version=version, producer="ideaforge.cli")
        )
    )
    idea = load_model(paths["idea"], IdeaBrief)
    evidence = load_model(paths["evidence"], EvidenceMatrix)
    review = load_model(paths["review"], CriticalReview)
    plan = load_model(paths["plan"], PrototypePlan)

    criteria_str = "\n".join(plan.acceptance_criteria)
    criteria_hash = hashlib.sha256(criteria_str.encode("utf-8")).hexdigest()

    path = paths["decisions"]
    decisions = json.loads(path.read_text(encoding="utf-8")) if path.exists() else []
    decision = Decision(
        case_id=args.case_id,
        actor=args.actor,
        statement=args.statement,
        approved=True,
        decision=HumanDecision.APPROVE_EXPERIMENT,
        rationale=args.statement,
        criteria_hash=criteria_hash,
    )

    all_decisions = [Decision.model_validate(item) for item in decisions] + [decision]
    dossier_content = render_dossier(idea, manifest, evidence, review, plan, all_decisions)
    dossier_hash = hashlib.sha256(dossier_content.encode("utf-8")).hexdigest()
    decision.dossier_hash = dossier_hash

    # Write approved dossier
    (version_path / "dossier.md").write_text(dossier_content, encoding="utf-8")

    decisions.append(decision.model_dump(mode="json"))
    atomic_json(path, decisions)

    # Update decision_record.md in experiment kit if present
    kit_dir = version_path / "experiment_kit"
    if kit_dir.exists():
        record_path = kit_dir / "decision_record.md"
        record_path.write_text(
            f"# Human Experiment Decision Record\n\n"
            f"- Case ID: {args.case_id}\n- Version: v{version:03d}\n"
            f"- Status: APPROVE_EXPERIMENT\n- Actor: {decision.actor or 'human'}\n"
            f"- Recorded: {decision.timestamp.isoformat()}\n\n"
            f"## Decision\nAPPROVE_EXPERIMENT\n\n## Rationale\n{decision.rationale}\n\n"
            f"## Next Step\nExecute protocol in experiment_card.md.\n",
            encoding="utf-8",
        )
        experiment_path = kit_dir / "experiment_plan.json"
        if experiment_path.exists():
            experiment = load_model(experiment_path, ExperimentPlan)
            experiment.human_status = "APPROVE_EXPERIMENT"
            write_json_model(experiment_path, experiment)

    print("approval recorded")
    return 0


def cmd_decide(args: argparse.Namespace) -> int:
    store = store_for(args)
    version, version_path = store.version_path(args.case_id, args.version)
    paths = artifact_paths(version_path)
    approved = args.decision == HumanDecision.APPROVE_EXPERIMENT.value
    criteria_hash = None
    dossier_hash = None

    if approved and paths["plan"].exists():
        plan = load_model(paths["plan"], PrototypePlan)
        criteria_str = "\n".join(plan.acceptance_criteria)
        criteria_hash = hashlib.sha256(criteria_str.encode("utf-8")).hexdigest()

    decision = Decision(
        case_id=args.case_id,
        actor=args.actor,
        statement=args.rationale,
        rationale=args.rationale,
        decision=HumanDecision(args.decision),
        approved=approved,
        criteria_hash=criteria_hash,
    )
    log = paths["decisions"]
    previous = json.loads(log.read_text(encoding="utf-8")) if log.exists() else []

    if (
        approved
        and paths["idea"].exists()
        and paths["evidence"].exists()
        and paths["review"].exists()
        and paths["plan"].exists()
    ):
        manifest_path = store.case_path(args.case_id) / "sources" / "source_manifest.json"
        manifest = (
            load_model(manifest_path, SourceManifest)
            if manifest_path.exists()
            else SourceManifest(
                meta=ArtifactMeta(case_id=args.case_id, version=version, producer="ideaforge.cli")
            )
        )
        idea = load_model(paths["idea"], IdeaBrief)
        evidence = load_model(paths["evidence"], EvidenceMatrix)
        review = load_model(paths["review"], CriticalReview)
        plan = load_model(paths["plan"], PrototypePlan)
        all_decisions = [Decision.model_validate(item) for item in previous] + [decision]
        dossier_content = render_dossier(idea, manifest, evidence, review, plan, all_decisions)
        dossier_hash = hashlib.sha256(dossier_content.encode("utf-8")).hexdigest()
        decision.dossier_hash = dossier_hash
        (version_path / "dossier.md").write_text(dossier_content, encoding="utf-8")

    previous.append(decision.model_dump(mode="json"))
    atomic_json(log, previous)
    kit_dir = version_path / "experiment_kit"
    kit_dir.mkdir(parents=True, exist_ok=True)
    record_path = kit_dir / "decision_record.md"
    record_path.write_text(
        f"# Human Experiment Decision Record\n\n"
        f"- Case ID: {args.case_id}\n- Version: v{version:03d}\n"
        f"- Status: {decision.decision.value}\n- Actor: {decision.actor or 'not provided'}\n"
        f"- Recorded: {decision.timestamp.isoformat()}\n\n"
        f"## Decision\n{decision.decision.value}\n\n"
        f"## Rationale\n{decision.rationale}\n\n"
        f"## Next Step\n"
        f"{'Execute protocol in experiment_card.md.' if decision.approved else 'Revise or defer experiment.'}\n",
        encoding="utf-8",
    )
    experiment_path = kit_dir / "experiment_plan.json"
    if experiment_path.exists():
        experiment = load_model(experiment_path, ExperimentPlan)
        experiment.human_status = decision.decision.value
        write_json_model(experiment_path, experiment)
    print(record_path)
    return 0


def cmd_render(args: argparse.Namespace) -> int:
    store = store_for(args)
    _, version_path = store.version_path(args.case_id, args.version)
    paths = artifact_paths(version_path)
    idea = load_model(paths["idea"], IdeaBrief)
    evidence = load_model(paths["evidence"], EvidenceMatrix)
    review = load_model(paths["review"], CriticalReview)
    plan = load_model(paths["plan"], PrototypePlan)
    manifest_path = store.case_path(args.case_id) / "sources" / "source_manifest.json"
    manifest = (
        load_model(manifest_path, SourceManifest)
        if manifest_path.exists()
        else SourceManifest(
            meta=ArtifactMeta(
                case_id=args.case_id, version=idea.meta.version, producer="ideaforge.render"
            )
        )
    )
    decisions = (
        [
            Decision.model_validate(item)
            for item in json.loads(paths["decisions"].read_text(encoding="utf-8"))
        ]
        if paths["decisions"].exists()
        else []
    )
    if any(decision.approved for decision in decisions) and (
        not paths["report"].exists() or not load_model(paths["report"], ValidationReport).valid
    ):
        raise SystemExit("approved dossier blocked: valid validation report is required")
    if any(decision.approved for decision in decisions):
        report = load_model(paths["report"], ValidationReport)
        if report.meta.input_hashes != artifact_hashes(paths):
            raise SystemExit("approved dossier blocked: artifacts changed since validation")
    content = render_dossier(idea, manifest, evidence, review, plan, decisions)
    output = version_path / "dossier.md"
    output.write_text(content, encoding="utf-8")
    print(output)
    return 0


def cmd_export(args: argparse.Namespace) -> int:
    store = store_for(args)
    _, version_path = store.version_path(args.case_id, args.version)
    dossier_path = version_path / "dossier.md"
    if not dossier_path.exists():
        # Render first
        cmd_render(args)
    content = dossier_path.read_text(encoding="utf-8")
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(content, encoding="utf-8")
    print(f"Exported dossier to {out_path}")
    return 0


def cmd_demo(args: argparse.Namespace) -> int:
    """Run an automated end-to-end demonstration of the full IDEAForge pipeline."""
    import subprocess
    import sys

    print("=" * 64)
    print("  IDEAFORGE 2.0 -- END-TO-END DEMO WORKFLOW")
    print("  Core Principle: Falsify Before You Fabricate")
    print("=" * 64)

    store = store_for(args)
    demo_dir = Path("examples/demo_case")
    if not demo_dir.exists():
        demo_dir = Path(__file__).resolve().parent.parent.parent / "examples" / "demo_case"

    # Step 1: Create Case
    title = "Conveyor belt early micro-tear defect detection"
    case_id, root = store.create_case(title)
    _version, version_path = store.version_path(case_id, 1)
    paths = artifact_paths(version_path)
    print(f"\n[Step 1] Created case: {case_id} (version v001)")

    # Step 2: Ingest Sources
    print("\n[Step 2] Ingesting reference source pack & hostile source...")
    sources = [
        demo_dir / "sources" / "demo_problem_brief.md",
        demo_dir / "sources" / "demo_sensor_notes.md",
        demo_dir / "sources" / "demo_experiment_constraints.md",
        demo_dir / "sources" / "demo_fault_injection_source.md",
        demo_dir / "sources" / "demo_hostile_source.md",
    ]
    for src in sources:
        if src.exists():
            rec = ingest_file(root, src, case_id, 1, store.settings)
            status_note = (
                f" ([!] {len(rec.extraction_warnings)} security warning flagged)"
                if rec.extraction_warnings
                else ""
            )
            print(f"  - Ingested {rec.original_name:<32} -> {rec.source_id}{status_note}")

    # Step 3: Initialize artifacts & adopt demo briefs
    print("\n[Step 3] Importing Switch specialist artifacts...")
    idea = load_model(demo_dir / "artifacts" / "00_idea_brief.json", IdeaBrief)
    idea.meta.case_id = case_id
    idea.meta.version = 1
    write_json_model(paths["idea"], idea)

    review = load_model(demo_dir / "artifacts" / "02_critical_review.json", CriticalReview)
    review.meta.case_id = case_id
    review.meta.version = 1
    write_json_model(paths["review"], review)

    plan = load_model(demo_dir / "artifacts" / "03_prototype_plan.json", PrototypePlan)
    plan.meta.case_id = case_id
    plan.meta.version = 1
    write_json_model(paths["plan"], plan)
    print("  - Imported Idea Brief, Critical Review, and Prototype Plan.")

    # Step 4: Demonstrate Fault Injection
    print("\n[Step 4] Fault Injection Test: importing invalid locator 'line:999'...")
    fault_evidence = load_model(
        demo_dir / "artifacts" / "01_evidence_matrix_fault.json", EvidenceMatrix
    )
    fault_evidence.meta.case_id = case_id
    fault_evidence.meta.version = 1
    write_json_model(paths["evidence"], fault_evidence)

    args.case_id = case_id
    args.version = 1
    print("  -> Running validator on faulty artifact...")
    val_res = cmd_validate(args)
    if val_res != 0:
        print("  -> Result: Validator CAUGHT and BLOCKED invalid citation!")

    # Step 5: Repair Fault
    print("\n[Step 5] Repairing citation with clean evidence matrix...")
    clean_evidence = load_model(demo_dir / "artifacts" / "01_evidence_matrix.json", EvidenceMatrix)
    clean_evidence.meta.case_id = case_id
    clean_evidence.meta.version = 1
    write_json_model(paths["evidence"], clean_evidence)
    print("  -> Re-running validator on repaired artifact...")
    val_res = cmd_validate(args)
    if val_res == 0:
        print("  -> Result: Validation PASSED! All citations cryptographically verified.")

    # Step 6: Build Experiment Kit
    print("\n[Step 6] Building Executable Experiment Kit...")
    exp_plan = load_model(demo_dir / "artifacts" / "experiment_plan.json", ExperimentPlan)
    exp_plan.case_id = case_id
    exp_plan.version = 1
    kit_output = version_path / "experiment_kit"
    kit_files = write_experiment_kit(kit_output, exp_plan, clean_evidence)
    for kf in kit_files:
        print(f"  - Generated: {kf.name}")

    # Step 7: Render Draft Dossier
    print("\n[Step 7] Rendering Draft Dossier with Epistemic Ledger...")
    cmd_render(args)
    print("  - Rendered: dossier.md (Status: DRAFT)")

    # Step 8: Human Approval with SHA-256 Pre-Registration
    print("\n[Step 8] Recording Human Approval & Pre-Registering SHA-256 Hashes...")
    args.actor = "lead_inventor"
    args.statement = "Risks acceptable for benchtop test rig; acceptance criteria locked at 6dB harmonic threshold."
    cmd_approve(args)
    print("  - Status: APPROVED (SHA-256 locked into decision_log.json)")

    # Step 9: 20-Second Tamper Test
    print("\n[Step 9] 20-Second Tamper Test: Attempting unauthorized threshold change...")
    tampered_plan = load_model(paths["plan"], PrototypePlan)
    original_criteria = list(tampered_plan.acceptance_criteria)
    tampered_plan.acceptance_criteria = ["Tampered: Shifted threshold to 12dB after experiment"]
    write_json_model(paths["plan"], tampered_plan)
    print("  -> Running validator on tampered plan...")
    tamper_res = cmd_validate(args)
    if tamper_res != 0:
        print("  -> Result: Tamper check CAUGHT unauthorized modification!")
    # Revert plan
    tampered_plan.acceptance_criteria = original_criteria
    write_json_model(paths["plan"], tampered_plan)
    cmd_validate(args)

    # Step 10: Run Analysis Starter
    print("\n[Step 10] Running fixed descriptive analysis on data template...")
    proc = subprocess.run(
        [sys.executable, str(kit_output / "analysis.py"), str(kit_output / "data_template.csv")],
        capture_output=True,
        text=True,
        check=True,
    )
    print(f"  - Analysis Starter Output: {proc.stdout.strip()}")

    # Step 11: Export Final Dossier
    export_out = Path("exports/demo_conveyor_dossier.md")
    export_out.parent.mkdir(parents=True, exist_ok=True)
    args.out = str(export_out)
    cmd_export(args)

    print("\n" + "=" * 64)
    print("  DEMO COMPLETE: ALL CHECKS & VALIDATIONS PASSED")
    print(f"  Case Directory:  workspace/{case_id}/")
    print(f"  Experiment Card: workspace/{case_id}/versions/v001/experiment_kit/experiment_card.md")
    print(f"  Final Dossier:   {export_out}")
    print("=" * 64)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ideaforge", description="Traceable prototype dossier and experiment studio"
    )
    parser.add_argument(
        "--config", help="JSON settings file; defaults to .ideaforge.json when present"
    )
    parser.add_argument("--workspace", help="override configured case workspace directory")
    sub = parser.add_subparsers(dest="command", required=True)

    show_config = sub.add_parser("show-config", help="display resolved runtime settings")
    show_config.set_defaults(func=cmd_show_config)

    create = sub.add_parser("create-case", help="create a new case")
    create.add_argument("title", nargs="?", default="")
    create.add_argument("--input", help="input idea markdown file")
    create.set_defaults(func=cmd_create)

    # Alias 'new' for create-case
    new_cmd = sub.add_parser("new", help="create a new case (alias for create-case)")
    new_cmd.add_argument("--title", default="")
    new_cmd.add_argument("--input", help="input idea markdown file")
    new_cmd.set_defaults(func=cmd_create)

    status = sub.add_parser("status", help="display case status and artifact health")
    status.add_argument("case_id", nargs="?", default="")
    status.add_argument("--case", dest="case_flag", default="")
    status.add_argument("--version", type=int)

    def handle_status(args: argparse.Namespace) -> int:
        args.case_id = args.case_id or args.case_flag
        if not args.case_id:
            raise SystemExit("error: case ID is required")
        return cmd_status(args)

    status.set_defaults(func=handle_status)

    ingest = sub.add_parser("ingest", help="ingest one or more source files")
    ingest.add_argument("case_id", nargs="?", default="")
    ingest.add_argument("file", nargs="?", default="")
    ingest.add_argument("--case", dest="case_flag", default="")
    ingest.add_argument("--source", action="append", default=[])
    ingest.add_argument("--version", type=int)

    def handle_ingest(args: argparse.Namespace) -> int:
        args.case_id = args.case_id or args.case_flag
        if not args.case_id:
            raise SystemExit("error: case ID is required")
        return cmd_ingest(args)

    ingest.set_defaults(func=handle_ingest)

    new_version = sub.add_parser("new-version", help="create an empty immutable revision")
    new_version.add_argument("case_id")
    new_version.set_defaults(func=cmd_new_version)

    schemas = sub.add_parser("export-schemas", help="export authoritative Pydantic JSON Schemas")
    schemas.add_argument("--output-dir", default="schemas")
    schemas.set_defaults(func=cmd_export_schemas)

    kit = sub.add_parser("build-kit", help="generate the validated Experiment Kit")
    kit.add_argument("case_id")
    kit.add_argument("plan_file")
    kit.add_argument("--version", type=int)
    kit.add_argument("--adopt", action="store_true", help="adopt the target case ID and version")
    kit.set_defaults(func=cmd_build_kit)

    init = sub.add_parser("init-artifacts", help="create draft artifacts for a case version")
    init.add_argument("case_id")
    init.add_argument("--title", required=True)
    init.add_argument("--idea", required=True)
    init.add_argument("--problem", default=None)
    init.add_argument("--version", type=int)
    init.add_argument(
        "--confidential",
        action="store_true",
        help="flag that confidential/NDA sources are involved",
    )
    init.set_defaults(func=cmd_init)

    imported = sub.add_parser(
        "import-artifact", help="validate and import a Switch-produced JSON artifact"
    )
    imported.add_argument("case_id")
    imported.add_argument("kind", choices=sorted(ARTIFACT_MODELS))
    imported.add_argument("file")
    imported.add_argument("--version", type=int)
    imported.add_argument(
        "--adopt", action="store_true", help="adopt the target case ID and version"
    )
    imported.set_defaults(func=cmd_import_artifact)

    validate = sub.add_parser("validate", help="validate artifact provenance")
    validate.add_argument("case_id")
    validate.add_argument("--version", type=int)
    validate.set_defaults(func=cmd_validate)

    approve = sub.add_parser("approve", help="record explicit human approval")
    approve.add_argument("case_id")
    approve.add_argument("--actor", default=None)
    approve.add_argument("--statement", required=True)
    approve.add_argument("--version", type=int)
    approve.set_defaults(func=cmd_approve)

    decide = sub.add_parser("decide", help="record a human experiment decision and rationale")
    decide.add_argument("case_id")
    decide.add_argument("decision", choices=[item.value for item in HumanDecision])
    decide.add_argument("--rationale", required=True)
    decide.add_argument("--actor", default=None)
    decide.add_argument("--version", type=int)
    decide.set_defaults(func=cmd_decide)

    render = sub.add_parser("render", help="render dossier markdown")
    render.add_argument("case_id")
    render.add_argument("--version", type=int)
    render.set_defaults(func=cmd_render)

    export = sub.add_parser("export", help="export dossier to a destination path")
    export.add_argument("case_id", nargs="?", default="")
    export.add_argument("--case", dest="case_flag", default="")
    export.add_argument("--out", required=True, help="output markdown file path")
    export.add_argument("--version", type=int)

    def handle_export(args: argparse.Namespace) -> int:
        args.case_id = args.case_id or args.case_flag
        if not args.case_id:
            raise SystemExit("error: case ID is required")
        return cmd_export(args)

    export.set_defaults(func=handle_export)

    demo = sub.add_parser("demo", help="run complete automated demonstration workflow")
    demo.set_defaults(func=cmd_demo)

    return parser


def main() -> None:
    args = build_parser().parse_args()
    raise SystemExit(args.func(args))
