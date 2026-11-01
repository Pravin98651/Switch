from __future__ import annotations

import hashlib
import re
import shutil
from pathlib import Path

from .config import Settings
from .models import ArtifactMeta, SourceManifest, SourceRecord
from .storage import atomic_json

TEXT_EXTENSIONS = {".txt", ".md"}

INJECTION_PATTERNS = [
    re.compile(r"ignore\s+(all\s+)?previous\s+instructions", re.IGNORECASE),
    re.compile(r"override\s+(all\s+)?safety\s+guidelines", re.IGNORECASE),
    re.compile(r"you\s+are\s+now\s+operating\s+in\s+unrestricted\s+mode", re.IGNORECASE),
    re.compile(r"disregard\s+(all\s+)?prior\s+instructions", re.IGNORECASE),
    re.compile(r"approve\s+this\s+idea\s+immediately", re.IGNORECASE),
]


def detect_prompt_injections(text: str) -> list[str]:
    warnings = []
    for line_num, line in enumerate(text.splitlines(), 1):
        for pattern in INJECTION_PATTERNS:
            if pattern.search(line):
                clean_snippet = line.strip()[:60]
                warnings.append(
                    f"line:{line_num} Potential prompt injection detected: '{clean_snippet}'"
                )
    return warnings


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _text_extract(path: Path) -> tuple[str, list[str]]:
    text = path.read_text(encoding="utf-8")
    return text, [f"line:{number}" for number, _ in enumerate(text.splitlines(), 1)]


def _pdf_extract(path: Path) -> tuple[str, list[str]]:
    try:
        import pymupdf
    except ImportError as exc:
        raise RuntimeError("PDF ingestion needs PyMuPDF; install ideaforge[documents]") from exc
    document = pymupdf.open(path)
    parts = []
    locators = []
    for number, page in enumerate(document, 1):
        parts.append(f"\n\n--- page:{number} ---\n{page.get_text()}")
        locators.append(f"page:{number}")
    return "".join(parts).strip(), locators


def _docx_extract(path: Path) -> tuple[str, list[str]]:
    try:
        from docx import Document
    except ImportError as exc:
        raise RuntimeError(
            "DOCX ingestion needs python-docx; install ideaforge[documents]"
        ) from exc
    document = Document(path)
    parts, locators = [], []
    for number, paragraph in enumerate(document.paragraphs, 1):
        parts.append(f"[paragraph:{number}] {paragraph.text}")
        locators.append(f"paragraph:{number}")
    for table_number, table in enumerate(document.tables, 1):
        for row_number, row in enumerate(table.rows, 1):
            parts.append(
                f"[table:{table_number};row:{row_number}] " + " | ".join(c.text for c in row.cells)
            )
            locators.append(f"table:{table_number};row:{row_number}")
    return "\n".join(parts), locators


def ingest_file(
    case_root: Path,
    source: str | Path,
    case_id: str,
    version: int,
    settings: Settings | None = None,
) -> SourceRecord:
    settings = settings or Settings()
    input_path = Path(source)
    if not input_path.is_file():
        raise FileNotFoundError(input_path)
    if input_path.stat().st_size == 0:
        raise ValueError("zero-byte sources are not allowed")
    if input_path.stat().st_size > settings.max_source_bytes:
        raise ValueError(f"source exceeds configured {settings.max_source_bytes}-byte limit")
    extension = input_path.suffix.lower()
    if extension not in settings.allowed_extensions:
        raise ValueError(f"unsupported configured file type: {extension or '(none)'}")
    original_hash = sha256(input_path)
    manifest_path = case_root / "sources" / "source_manifest.json"
    if manifest_path.exists():
        prior = SourceManifest.model_validate_json(manifest_path.read_text(encoding="utf-8"))
        if any(item.original_sha256 == original_hash for item in prior.sources):
            raise ValueError("duplicate source hash")
    if extension in TEXT_EXTENSIONS:
        text, locators, media_type = (
            *_text_extract(input_path),
            settings.allowed_extensions[extension],
        )
    elif extension == ".pdf":
        text, locators, media_type = (
            *_pdf_extract(input_path),
            settings.allowed_extensions[extension],
        )
    elif extension == ".docx":
        text, locators, media_type = (
            *_docx_extract(input_path),
            settings.allowed_extensions[extension],
        )
    else:
        raise ValueError(f"unsupported file type: {extension or '(none)'}")
    saved_original = case_root / "sources" / "original" / f"{original_hash[:12]}_{input_path.name}"
    shutil.copy2(input_path, saved_original)
    extracted = case_root / "sources" / "extracted" / f"{original_hash}.txt"
    extracted.write_text(text, encoding="utf-8")
    warnings = detect_prompt_injections(text)
    record = SourceRecord(
        source_id=f"SRC-{original_hash[:12].upper()}",
        original_name=input_path.name,
        media_type=media_type,
        original_sha256=original_hash,
        extracted_sha256=sha256(extracted),
        extraction_status="success",
        locators=locators,
        extracted_path=str(extracted.relative_to(case_root)),
        extraction_warnings=warnings,
    )
    items = prior.sources if manifest_path.exists() else []
    manifest = SourceManifest(
        meta=ArtifactMeta(case_id=case_id, version=version, producer="ideaforge.ingest"),
        sources=[*items, record],
    )
    atomic_json(manifest_path, manifest.model_dump(mode="json"))
    return record
