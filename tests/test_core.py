import subprocess
import sys
from pathlib import Path

import pytest

from ideaforge.config import Settings
from ideaforge.experiment_kit import write_experiment_kit
from ideaforge.ingest import ingest_file
from ideaforge.models import (
    ArtifactMeta,
    CriticalReview,
    DecisionRecord,
    EvidenceItem,
    EvidenceMatrix,
    ExperimentPlan,
    ExperimentType,
    FactType,
    HumanDecision,
    IdeaBrief,
    MeasuredVariable,
    PrototypePlan,
    SourceManifest,
)
from ideaforge.storage import CaseStore
from ideaforge.validation import validate_artifacts, validate_evidence


def test_cases_are_versioned(tmp_path: Path):
    store = CaseStore(tmp_path)
    case_id, root = store.create_case("test")
    assert case_id.startswith("IF-")
    assert (root / "versions" / "v001").is_dir()
    number, _ = store.create_version(case_id)
    assert number == 2


def test_source_backed_evidence_requires_source():
    with pytest.raises(ValueError):
        EvidenceItem(claim="x", fact_type=FactType.SOURCE_BACKED)


def test_fact_types():
    assert FactType.HYPOTHESIS.value == "HYPOTHESIS"
    item = EvidenceItem(claim="Defect shifts acoustic peak", fact_type=FactType.HYPOTHESIS)
    assert item.fact_type == FactType.HYPOTHESIS


def test_text_ingestion_and_provenance(tmp_path: Path):
    source = tmp_path / "source.md"
    source.write_text("first\nsecond\n", encoding="utf-8")
    store = CaseStore(tmp_path / "workspace")
    case_id, root = store.create_case("test")
    record = ingest_file(root, source, case_id, 1)
    assert "line:2" in record.locators
    manifest = SourceManifest.model_validate_json(
        (root / "sources" / "source_manifest.json").read_text()
    )
    evidence = EvidenceMatrix(
        meta=ArtifactMeta(case_id=case_id, version=1, producer="test"),
        items=[
            EvidenceItem(
                claim="claim",
                fact_type=FactType.SOURCE_BACKED,
                source_id=record.source_id,
                locator="line:2",
            )
        ],
    )
    assert not validate_evidence(manifest, evidence)
    bad_evidence = EvidenceMatrix(
        meta=ArtifactMeta(case_id=case_id, version=1, producer="test"),
        items=[
            EvidenceItem(
                claim="claim",
                fact_type=FactType.SOURCE_BACKED,
                source_id=record.source_id,
                locator="line:99",
            )
        ],
    )
    assert validate_evidence(manifest, bad_evidence)


def test_pdf_and_docx_ingestion(tmp_path: Path):
    import pymupdf
    from docx import Document

    pdf_path = tmp_path / "sample.pdf"
    doc = pymupdf.open()
    page = doc.new_page()
    page.insert_text((50, 50), "PDF Evidence Content")
    doc.save(str(pdf_path))
    doc.close()

    docx_path = tmp_path / "sample.docx"
    d = Document()
    d.add_heading("Section 1", level=1)
    d.add_paragraph("DOCX Evidence Content")
    d.save(str(docx_path))

    store = CaseStore(tmp_path / "workspace")
    case_id, root = store.create_case("test")
    r1 = ingest_file(root, pdf_path, case_id, 1)
    assert "page:1" in r1.locators
    r2 = ingest_file(root, docx_path, case_id, 1)
    assert "paragraph:2" in r2.locators


def test_validation_reports_cross_artifact_mismatches():
    meta = ArtifactMeta(case_id="IF-20261101-001", version=1, producer="test")
    idea = IdeaBrief(
        meta=meta,
        title="Title",
        original_idea="Original Idea",
        problem="Problem",
    )
    manifest = SourceManifest(meta=meta)
    evidence = EvidenceMatrix(meta=meta)
    review = CriticalReview(meta=meta)
    plan = PrototypePlan(
        meta=meta,
        architecture="Arch",
        hypothesis="Hypothesis",
        protocol=["Step 1"],
        acceptance_criteria=["Criterion 1"],
    )
    assert not validate_artifacts("IF-20261101-001", 1, idea, manifest, evidence, review, plan)
    plan.meta.version = 2
    errors = validate_artifacts("IF-20261101-001", 1, idea, manifest, evidence, review, plan)
    assert any("version" in err for err in errors)


def test_duplicate_source_rejection(tmp_path: Path):
    store = CaseStore(tmp_path / "workspace")
    case_id, root = store.create_case("test")
    source = tmp_path / "dup.txt"
    source.write_text("duplicate-bytes", encoding="utf-8")
    ingest_file(root, source, case_id, 1)
    with pytest.raises(ValueError, match="duplicate source hash"):
        ingest_file(root, source, case_id, 1)


def test_file_size_limit(tmp_path: Path):
    settings = Settings(max_source_bytes=10)
    store = CaseStore(tmp_path / "workspace", settings=settings)
    case_id, root = store.create_case("test")
    source = tmp_path / "large.txt"
    source.write_text("too-large-content-exceeds-limit", encoding="utf-8")
    with pytest.raises(ValueError, match="configured"):
        ingest_file(root, source, case_id, 1, settings)


def test_experiment_kit_and_screening_downgrade(tmp_path: Path):
    plan = ExperimentPlan(
        experiment_id="EXP-1",
        case_id="IF-20261101-001",
        version=1,
        title="Signal screening",
        experiment_type=ExperimentType.MINIMUM_DECISIVE,
        hypothesis="The signal changes between conditions.",
        alternative_explanation="Sensor placement changes the signal.",
        independent_variables=[MeasuredVariable(name="condition", unit="unitless")],
        dependent_variables=[MeasuredVariable(name="amplitude", unit="V")],
        control_variables=[MeasuredVariable(name="sensor placement", unit="mm")],
        equipment=["sensor"],
        calibration_steps=["Check against baseline"],
        procedure=["Record baseline", "Record changed condition"],
        data_schema=[MeasuredVariable(name="amplitude", unit="V")],
        analysis_method="Compare descriptive means.",
        criteria={
            "supports": "Difference repeats",
            "weakens": "No difference",
            "inconclusive": "Unstable readings",
        },
    )
    assert plan.experiment_type == ExperimentType.PRELIMINARY_SCREENING
    ledger = EvidenceMatrix(meta=ArtifactMeta(case_id=plan.case_id, version=1, producer="test"))
    output = tmp_path / "kit"
    paths = write_experiment_kit(output, plan, ledger)
    assert {path.name for path in paths} == {
        "experiment_plan.json",
        "source_ledger.json",
        "experiment_card.md",
        "data_template.csv",
        "analysis.py",
        "source_ledger.md",
        "decision_record.md",
    }
    assert "PRELIMINARY_SCREENING" in (output / "experiment_card.md").read_text()
    result = subprocess.run(
        [sys.executable, str(output / "analysis.py"), str(output / "data_template.csv")],
        check=True,
        capture_output=True,
        text=True,
    )
    assert "'rows': 0" in result.stdout


def test_mde_retains_type_with_rationale():
    plan = ExperimentPlan(
        experiment_id="EXP-2",
        case_id="IF-20261101-002",
        version=1,
        title="Conveyor vibration vs roller speed",
        experiment_type=ExperimentType.MINIMUM_DECISIVE,
        hypothesis="Defect generates harmonic frequency peak independent of belt speed.",
        alternative_explanation="Vibration amplitude is solely a function of roller RPM.",
        mde_rationale="Tests two speeds with and without defect; harmonic peak persists only for defect.",
        independent_variables=[
            MeasuredVariable(name="defect_present", unit="boolean"),
            MeasuredVariable(name="belt_speed", unit="m/s"),
        ],
        dependent_variables=[MeasuredVariable(name="harmonic_peak_hz", unit="Hz")],
        control_variables=[MeasuredVariable(name="sensor_mounting_torque", unit="Nm")],
        equipment=["accelerometer", "benchtop conveyor"],
        calibration_steps=["Zero sensor at standstill"],
        procedure=[
            "Run at 1 m/s baseline",
            "Run at 2 m/s baseline",
            "Run at 1 m/s defect",
            "Run at 2 m/s defect",
        ],
        data_schema=[MeasuredVariable(name="harmonic_peak_hz", unit="Hz")],
        analysis_method="Compare harmonic frequency across speeds and defect states.",
        criteria={
            "supports": "Harmonic peak present only with defect across both speeds",
            "weakens": "Peak shifts proportionally with speed without defect",
            "inconclusive": "SNR below 6dB",
        },
    )
    assert plan.experiment_type == ExperimentType.MINIMUM_DECISIVE


def test_decision_record():
    decision = DecisionRecord(
        case_id="IF-20261101-001",
        decision=HumanDecision.APPROVE_EXPERIMENT,
        rationale="Risks are acceptable for benchtop test.",
        actor="lead_investigator",
        approved=True,
    )
    assert decision.decision == HumanDecision.APPROVE_EXPERIMENT
    assert decision.approved is True


def test_cli_status_and_export(tmp_path: Path):
    from ideaforge.cli import build_parser

    parser = build_parser()
    # Create case
    ws = tmp_path / "workspace"
    args = parser.parse_args(["--workspace", str(ws), "create-case", "CLI Test Case"])
    assert args.func(args) == 0

    # Get case ID from created dir
    case_dir = next(ws.iterdir())
    case_id = case_dir.name

    # Init artifacts
    init_args = parser.parse_args(
        [
            "--workspace",
            str(ws),
            "init-artifacts",
            case_id,
            "--title",
            "Test Title",
            "--idea",
            "Original Idea Statement",
        ]
    )
    assert init_args.func(init_args) == 0

    # Check status
    status_args = parser.parse_args(["--workspace", str(ws), "status", case_id])
    assert status_args.func(status_args) == 0

    # Render
    render_args = parser.parse_args(["--workspace", str(ws), "render", case_id])
    assert render_args.func(render_args) == 0

    # Export
    out_file = tmp_path / "exported" / "dossier.md"
    export_args = parser.parse_args(
        ["--workspace", str(ws), "export", case_id, "--out", str(out_file)]
    )
    assert export_args.func(export_args) == 0
    assert out_file.exists()
    assert "Original Idea Statement" in out_file.read_text(encoding="utf-8")


def test_cli_adopt_flag(tmp_path: Path):
    from ideaforge.cli import build_parser

    parser = build_parser()
    ws = tmp_path / "workspace"
    parser.parse_args(["--workspace", str(ws), "create-case", "Adopt Case"]).func(
        parser.parse_args(["--workspace", str(ws), "create-case", "Adopt Case"])
    )
    case_dir = next(ws.iterdir())
    case_id = case_dir.name

    # Write an artifact with a mismatched case ID
    foreign_artifact = tmp_path / "foreign_idea.json"
    foreign_artifact.write_text(
        '{"meta": {"case_id": "IF-OTHER-999", "version": 1, "producer": "ext"}, "title": "T", "original_idea": "I"}',
        encoding="utf-8",
    )

    # Import without --adopt fails
    with pytest.raises(SystemExit, match="--adopt"):
        args = parser.parse_args(
            ["--workspace", str(ws), "import-artifact", case_id, "idea", str(foreign_artifact)]
        )
        args.func(args)

    # Import with --adopt succeeds
    args_adopt = parser.parse_args(
        [
            "--workspace",
            str(ws),
            "import-artifact",
            case_id,
            "idea",
            str(foreign_artifact),
            "--adopt",
        ]
    )
    assert args_adopt.func(args_adopt) == 0
