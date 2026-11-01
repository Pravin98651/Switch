"""Lightweight zero-dependency IDEAForge Web Studio server and REST API."""

from __future__ import annotations

import argparse
import hashlib
import http.server
import json
import urllib.parse
from pathlib import Path
from typing import Any

from .config import load_settings
from .models import (
    ArtifactMeta,
    CriticalReview,
    Decision,
    EvidenceMatrix,
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


def artifact_hashes(paths: dict[str, Path]) -> list[str]:
    hashed = []
    for key in ("idea", "evidence", "review", "plan"):
        path = paths[key]
        if path.exists():
            hashed.append(hashlib.sha256(path.read_bytes()).hexdigest())
    return hashed


class StudioAPI:
    """Core studio actions powering the web interface."""

    def __init__(self, store: CaseStore):
        self.store = store

    def list_cases(self) -> list[dict[str, Any]]:
        if not self.store.workspace.exists():
            return []
        cases = []
        for p in sorted(self.store.workspace.iterdir(), reverse=True):
            if not p.is_dir():
                continue
            case_file = p / "case.json"
            if not case_file.exists():
                continue
            try:
                data = json.loads(case_file.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                continue

            versions_dir = p / "versions"
            version_count = len(list(versions_dir.glob("v*"))) if versions_dir.exists() else 0

            # Check latest version status
            latest_status = "draft"
            has_tamper_lock = False
            if version_count > 0:
                latest_ver_path = versions_dir / f"v{version_count:03d}"
                dec_path = latest_ver_path / "decision_log.json"
                if dec_path.exists():
                    try:
                        decs = json.loads(dec_path.read_text(encoding="utf-8"))
                        if any(d.get("approved") for d in decs):
                            latest_status = "approved"
                        if any(d.get("approved") and d.get("dossier_hash") for d in decs):
                            has_tamper_lock = True
                    except (json.JSONDecodeError, OSError):
                        pass

            data["version_count"] = version_count
            data["status"] = latest_status
            data["has_tamper_lock"] = has_tamper_lock
            cases.append(data)
        return cases

    def get_case(self, case_id: str, version: int | None = None) -> dict[str, Any]:
        case_root = self.store.case_path(case_id)
        if not case_root.exists():
            raise FileNotFoundError(f"Case '{case_id}' does not exist")

        case_meta = {}
        if (case_root / "case.json").exists():
            case_meta = json.loads((case_root / "case.json").read_text(encoding="utf-8"))

        ver_num, version_path = self.store.version_path(case_id, version)
        paths = artifact_paths(version_path)

        # Artifacts
        idea_data = (
            json.loads(paths["idea"].read_text(encoding="utf-8"))
            if paths["idea"].exists()
            else None
        )
        evidence_data = (
            json.loads(paths["evidence"].read_text(encoding="utf-8"))
            if paths["evidence"].exists()
            else None
        )
        review_data = (
            json.loads(paths["review"].read_text(encoding="utf-8"))
            if paths["review"].exists()
            else None
        )
        plan_data = (
            json.loads(paths["plan"].read_text(encoding="utf-8"))
            if paths["plan"].exists()
            else None
        )
        report_data = (
            json.loads(paths["report"].read_text(encoding="utf-8"))
            if paths["report"].exists()
            else None
        )
        decisions_data = (
            json.loads(paths["decisions"].read_text(encoding="utf-8"))
            if paths["decisions"].exists()
            else []
        )

        # Sources
        manifest_path = case_root / "sources" / "source_manifest.json"
        manifest_data = (
            json.loads(manifest_path.read_text(encoding="utf-8"))
            if manifest_path.exists()
            else {"sources": []}
        )

        # Epistemic ledger
        ledger_counts = {}
        ledger_summary = "No evidence recorded"
        if paths["evidence"].exists():
            try:
                ev_model = load_model(paths["evidence"], EvidenceMatrix)
                ledger_counts = compute_epistemic_ledger(ev_model)
                ledger_summary = format_epistemic_ledger(ledger_counts)
            except (json.JSONDecodeError, OSError, ValueError, KeyError):
                ledger_summary = "Error reading evidence matrix"

        # Kit files
        kit_dir = version_path / "experiment_kit"
        card_content = ""
        decision_record_content = ""
        exp_plan_data = None
        if kit_dir.exists():
            card_path = kit_dir / "experiment_card.md"
            if card_path.exists():
                card_content = card_path.read_text(encoding="utf-8")
            dec_rec_path = kit_dir / "decision_record.md"
            if dec_rec_path.exists():
                decision_record_content = dec_rec_path.read_text(encoding="utf-8")
            plan_json = kit_dir / "experiment_plan.json"
            if plan_json.exists():
                exp_plan_data = json.loads(plan_json.read_text(encoding="utf-8"))

        # Dossier
        dossier_content = ""
        dossier_path = version_path / "dossier.md"
        if dossier_path.exists():
            dossier_content = dossier_path.read_text(encoding="utf-8")

        approved = any(d.get("approved") for d in decisions_data)
        has_tamper_lock = any(d.get("approved") and d.get("dossier_hash") for d in decisions_data)

        return {
            "case_id": case_id,
            "version": ver_num,
            "case_meta": case_meta,
            "status": "APPROVED" if approved else "DRAFT",
            "has_tamper_lock": has_tamper_lock,
            "epistemic_ledger": {
                "counts": ledger_counts,
                "summary": ledger_summary,
            },
            "artifacts": {
                "idea": idea_data,
                "evidence": evidence_data,
                "review": review_data,
                "plan": plan_data,
                "report": report_data,
                "decisions": decisions_data,
            },
            "sources": manifest_data.get("sources", []),
            "kit": {
                "card": card_content,
                "decision_record": decision_record_content,
                "plan": exp_plan_data,
            },
            "dossier": dossier_content,
        }

    def validate_case(self, case_id: str, version: int | None = None) -> dict[str, Any]:
        ver_num, version_path = self.store.version_path(case_id, version)
        paths = artifact_paths(version_path)
        errors: list[str] = []
        manifest = None

        try:
            manifest_path = self.store.case_path(case_id) / "sources" / "source_manifest.json"
            manifest = (
                load_model(manifest_path, SourceManifest)
                if manifest_path.exists()
                else SourceManifest(
                    meta=ArtifactMeta(
                        case_id=case_id, version=ver_num, producer="ideaforge.validation"
                    )
                )
            )
            errors.extend(
                validate_artifacts(
                    case_id,
                    ver_num,
                    load_model(paths["idea"], IdeaBrief),
                    manifest,
                    load_model(paths["evidence"], EvidenceMatrix),
                    load_model(paths["review"], CriticalReview),
                    load_model(paths["plan"], PrototypePlan),
                )
            )
        except FileNotFoundError as error:
            errors.append(f"missing required artifact: {error.filename}")

        # Tamper check
        if paths["decisions"].exists():
            try:
                decisions_data = json.loads(paths["decisions"].read_text(encoding="utf-8"))
                for d in decisions_data:
                    if d.get("approved") and d.get("dossier_hash"):
                        expected_dossier_hash = d["dossier_hash"]
                        expected_criteria_hash = d.get("criteria_hash")

                        if expected_criteria_hash and paths["plan"].exists():
                            try:
                                curr_plan = load_model(paths["plan"], PrototypePlan)
                                curr_crit = "\n".join(curr_plan.acceptance_criteria)
                                curr_crit_hash = hashlib.sha256(
                                    curr_crit.encode("utf-8")
                                ).hexdigest()
                                if curr_crit_hash != expected_criteria_hash:
                                    errors.append(
                                        f"tamper check failed: acceptance criteria modified after approval (expected {expected_criteria_hash[:12]}..., got {curr_crit_hash[:12]}...)"
                                    )
                            except (json.JSONDecodeError, OSError, ValueError, KeyError) as e:
                                errors.append(f"tamper check failed: criteria error ({e})")

                        dossier_file = version_path / "dossier.md"
                        if dossier_file.exists():
                            actual_file_hash = hashlib.sha256(
                                dossier_file.read_text(encoding="utf-8").encode("utf-8")
                            ).hexdigest()
                            if actual_file_hash != expected_dossier_hash:
                                errors.append(
                                    f"tamper check failed: dossier.md modified after approval (expected {expected_dossier_hash[:12]}..., got {actual_file_hash[:12]}...)"
                                )

                        try:
                            temp_decisions = [
                                Decision.model_validate(item) for item in decisions_data
                            ]
                            curr_rendered = render_dossier(
                                load_model(paths["idea"], IdeaBrief),
                                manifest
                                or SourceManifest(
                                    meta=ArtifactMeta(
                                        case_id=case_id,
                                        version=ver_num,
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
                            errors.append(f"tamper check failed: re-render error ({e})")
            except (json.JSONDecodeError, OSError, ValueError, KeyError) as e:
                errors.append(f"tamper check failed: invalid decision log ({e})")

        report = ValidationReport(
            meta=ArtifactMeta(
                case_id=case_id,
                version=ver_num,
                producer="ideaforge.validation",
                input_hashes=artifact_hashes(paths),
            ),
            valid=not errors,
            errors=errors,
        )
        atomic_json(paths["report"], report.model_dump(mode="json"))
        return report.model_dump(mode="json")

    def approve_case(
        self,
        case_id: str,
        actor: str = "lead_inventor",
        statement: str = "Risks acceptable for benchtop run.",
        version: int | None = None,
    ) -> dict[str, Any]:
        # Validate first
        val = self.validate_case(case_id, version)
        if not val["valid"]:
            raise ValueError(f"Approval blocked: validation errors: {', '.join(val['errors'])}")

        ver_num, version_path = self.store.version_path(case_id, version)
        paths = artifact_paths(version_path)

        manifest_path = self.store.case_path(case_id) / "sources" / "source_manifest.json"
        manifest = (
            load_model(manifest_path, SourceManifest)
            if manifest_path.exists()
            else SourceManifest(
                meta=ArtifactMeta(case_id=case_id, version=ver_num, producer="ideaforge.cli")
            )
        )
        idea = load_model(paths["idea"], IdeaBrief)
        evidence = load_model(paths["evidence"], EvidenceMatrix)
        review = load_model(paths["review"], CriticalReview)
        plan = load_model(paths["plan"], PrototypePlan)

        criteria_str = "\n".join(plan.acceptance_criteria)
        criteria_hash = hashlib.sha256(criteria_str.encode("utf-8")).hexdigest()

        decisions_path = paths["decisions"]
        decisions = (
            json.loads(decisions_path.read_text(encoding="utf-8"))
            if decisions_path.exists()
            else []
        )
        decision = Decision(
            case_id=case_id,
            actor=actor,
            statement=statement,
            approved=True,
            decision=HumanDecision.APPROVE_EXPERIMENT,
            rationale=statement,
            criteria_hash=criteria_hash,
        )

        all_decisions = [Decision.model_validate(item) for item in decisions] + [decision]
        dossier_content = render_dossier(idea, manifest, evidence, review, plan, all_decisions)
        dossier_hash = hashlib.sha256(dossier_content.encode("utf-8")).hexdigest()
        decision.dossier_hash = dossier_hash

        with (version_path / "dossier.md").open("w", encoding="utf-8", newline="\n") as f:
            f.write(dossier_content)

        decisions.append(decision.model_dump(mode="json"))
        atomic_json(decisions_path, decisions)

        # Update kit if present
        kit_dir = version_path / "experiment_kit"
        if kit_dir.exists():
            (kit_dir / "decision_record.md").write_text(
                f"# Human Experiment Decision Record\n\n- Case ID: {case_id}\n- Version: v{ver_num:03d}\n- Status: APPROVE_EXPERIMENT\n- Actor: {actor}\n- Dossier Hash: {dossier_hash}\n\n## Decision\nAPPROVE_EXPERIMENT\n\n## Rationale\n{statement}\n",
                encoding="utf-8",
            )
        return decision.model_dump(mode="json")

    def tamper_case(self, case_id: str, action: str, version: int | None = None) -> dict[str, Any]:
        """Simulate tampering or restore prototype plan."""
        _ver_num, version_path = self.store.version_path(case_id, version)
        paths = artifact_paths(version_path)
        if not paths["plan"].exists():
            raise FileNotFoundError("Prototype plan does not exist")

        plan_data = json.loads(paths["plan"].read_text(encoding="utf-8"))
        backup_path = version_path / "03_prototype_plan.json.orig"

        if action == "tamper":
            if not backup_path.exists():
                backup_path.write_text(json.dumps(plan_data), encoding="utf-8")
            plan_data["acceptance_criteria"] = [
                "Tampered: Shifted threshold from 6dB to 12dB after experiment run without authorization"
            ]
            atomic_json(paths["plan"], plan_data)
            return {
                "action": "tampered",
                "message": "Modified acceptance criteria to simulate post-approval tampering",
            }
        elif action == "restore":
            if backup_path.exists():
                orig_data = json.loads(backup_path.read_text(encoding="utf-8"))
                atomic_json(paths["plan"], orig_data)
            else:
                plan_data["acceptance_criteria"] = [
                    "Acoustic burst amplitude in defect condition exceeds baseline by >=6 dB.",
                    "Burst periodicity matches T = 1.2m / V (1.20s at 1.0 m/s, 0.60s at 2.0 m/s).",
                ]
                atomic_json(paths["plan"], plan_data)
            return {"action": "restored", "message": "Restored original authorized prototype plan"}
        else:
            raise ValueError(f"Unknown tamper action: {action}")


class StudioHandler(http.server.BaseHTTPRequestHandler):
    """HTTP Request Handler dispatching web interface and JSON API."""

    api: StudioAPI
    static_dir: Path

    def _send_json(self, data: Any, status: int = 200) -> None:
        raw = json.dumps(data, indent=2, default=str).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.end_headers()
        self.wfile.write(raw)

    def _send_html(self, html: str) -> None:
        raw = html.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def do_OPTIONS(self) -> None:
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.end_headers()

    def do_GET(self) -> None:
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        query = urllib.parse.parse_qs(parsed.query)

        if path in ("", "/"):
            # Serve index.html
            html_file = self.static_dir / "index.html"
            if html_file.exists():
                self._send_html(html_file.read_text(encoding="utf-8"))
            else:
                self._send_html("<h1>IDEAForge Web Studio: index.html not found</h1>")
            return

        if path == "/api/cases":
            self._send_json(self.api.list_cases())
            return

        if path.startswith("/api/cases/"):
            parts = path.strip("/").split("/")
            if len(parts) >= 3:
                case_id = parts[2]
                ver = int(query["version"][0]) if "version" in query else None
                try:
                    self._send_json(self.api.get_case(case_id, ver))
                except (
                    json.JSONDecodeError,
                    OSError,
                    ValueError,
                    KeyError,
                    FileNotFoundError,
                ) as e:
                    self._send_json({"error": str(e)}, status=404)
                return

        self._send_json({"error": "Not Found"}, status=404)

    def do_POST(self) -> None:
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        content_length = int(self.headers.get("Content-Length", 0))
        body_raw = self.rfile.read(content_length).decode("utf-8") if content_length > 0 else "{}"
        body = json.loads(body_raw) if body_raw.strip() else {}

        if path.startswith("/api/cases/") and path.endswith("/validate"):
            parts = path.strip("/").split("/")
            case_id = parts[2]
            try:
                res = self.api.validate_case(case_id)
                self._send_json(res)
            except (json.JSONDecodeError, OSError, ValueError, KeyError) as e:
                self._send_json({"error": str(e)}, status=400)
            return

        if path.startswith("/api/cases/") and path.endswith("/approve"):
            parts = path.strip("/").split("/")
            case_id = parts[2]
            actor = body.get("actor", "lead_inventor")
            statement = body.get("statement", "Approved via IDEAForge Web Studio")
            try:
                res = self.api.approve_case(case_id, actor=actor, statement=statement)
                self._send_json(res)
            except (json.JSONDecodeError, OSError, ValueError, KeyError) as e:
                self._send_json({"error": str(e)}, status=400)
            return

        if path.startswith("/api/cases/") and path.endswith("/tamper"):
            parts = path.strip("/").split("/")
            case_id = parts[2]
            action = body.get("action", "tamper")
            try:
                res = self.api.tamper_case(case_id, action=action)
                self._send_json(res)
            except (json.JSONDecodeError, OSError, ValueError, KeyError) as e:
                self._send_json({"error": str(e)}, status=400)
            return

        if path == "/api/demo":
            # Run demo case
            from .cli import cmd_demo

            demo_args = argparse.Namespace(
                config=None, workspace=str(self.api.store.workspace), func=cmd_demo
            )
            try:
                cmd_demo(demo_args)
                cases = self.api.list_cases()
                latest_case = cases[0]["case_id"] if cases else None
                self._send_json({"success": True, "case_id": latest_case})
            except (json.JSONDecodeError, OSError, ValueError, KeyError, RuntimeError) as e:
                self._send_json({"error": str(e)}, status=500)
            return

        self._send_json({"error": "Unknown POST route"}, status=404)


def run_server(
    host: str = "127.0.0.1", port: int = 8765, workspace: str | Path | None = None
) -> None:
    settings = load_settings(None, workspace)
    store = CaseStore(settings=settings)
    api = StudioAPI(store)

    static_dir = Path(__file__).resolve().parent / "web"
    static_dir.mkdir(parents=True, exist_ok=True)

    StudioHandler.api = api
    StudioHandler.static_dir = static_dir

    server_address = (host, port)
    httpd = http.server.HTTPServer(server_address, StudioHandler)
    print("============================================================")
    print("  IDEAFORGE 2.0 -- WEB STUDIO FRONTEND RUNNING")
    print(f"  URL:       http://{host}:{port}")
    print(f"  Workspace: {store.workspace}")
    print("  Press Ctrl+C to stop the server")
    print("============================================================")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down IDEAForge Web Studio server...")
        httpd.server_close()
