#!/usr/bin/env python3
"""Bootstrap PRD requirement-to-implementation mapping report."""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


PRD_REQUIREMENT_PATTERN = re.compile(r"^(FR-[A-Z0-9-]+|NFR-[0-9]+)$", re.IGNORECASE)
PRD_PRIORITY_PATTERN = re.compile(r"\b(P[0-2])\b", re.IGNORECASE)
DEFAULT_OUTPUT_REL_PATH = "reports/prd-implementation.json"


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def normalize_markdown_cell(cell: str) -> str:
    return cell.strip().strip("`").strip()


def parse_markdown_table_row(line: str) -> list[str] | None:
    stripped = line.strip()
    if not stripped.startswith("|"):
        return None
    cells = [part.strip() for part in stripped.strip("|").split("|")]
    if not cells:
        return None
    if all(re.fullmatch(r":?-{3,}:?", cell.replace(" ", "")) for cell in cells):
        return None
    return cells


def parse_priority(value: str) -> str:
    normalized = normalize_markdown_cell(value).upper()
    match = PRD_PRIORITY_PATTERN.search(normalized)
    if match:
        return match.group(1).upper()
    return ""


def priority_rank(priority: str) -> int:
    normalized = priority.upper().strip()
    if normalized == "P0":
        return 0
    if normalized == "P1":
        return 1
    if normalized == "P2":
        return 2
    return 9


def extract_prd_requirements(prd_path: Path) -> list[dict[str, str]]:
    content = prd_path.read_text(encoding="utf-8-sig")
    requirements_by_id: dict[str, dict[str, str]] = {}

    for line in content.splitlines():
        row = parse_markdown_table_row(line)
        if not row:
            continue
        requirement_id = normalize_markdown_cell(row[0]).upper()
        if not PRD_REQUIREMENT_PATTERN.fullmatch(requirement_id):
            continue

        if requirement_id.startswith("NFR-"):
            priority = "P0"
        else:
            priority = parse_priority(row[2]) if len(row) > 2 else ""
            if not priority:
                priority = "P1"

        existing = requirements_by_id.get(requirement_id)
        if not existing:
            requirements_by_id[requirement_id] = {
                "id": requirement_id,
                "priority": priority,
            }
            continue

        if priority_rank(priority) < priority_rank(existing["priority"]):
            existing["priority"] = priority

    return [
        requirements_by_id[key]
        for key in sorted(requirements_by_id.keys(), key=lambda item: item.upper())
    ]


def normalize_str_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    items: list[str] = []
    for item in value:
        if isinstance(item, str):
            normalized = item.strip()
            if normalized:
                items.append(normalized)
    return items


def load_existing_entries(path: Path) -> dict[str, dict[str, Any]]:
    if not path.exists():
        return {}

    try:
        payload = json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception:
        return {}

    if not isinstance(payload, dict):
        return {}

    raw_requirements = payload.get("requirements")
    if not isinstance(raw_requirements, list):
        return {}

    entries: dict[str, dict[str, Any]] = {}
    for item in raw_requirements:
        if not isinstance(item, dict):
            continue
        requirement_id = str(item.get("id", "")).strip().upper()
        if not PRD_REQUIREMENT_PATTERN.fullmatch(requirement_id):
            continue
        entries[requirement_id] = item
    return entries


def resolve_output_path(project_dir: Path, raw_path: str | None) -> Path:
    if not raw_path:
        return (project_dir / DEFAULT_OUTPUT_REL_PATH).resolve()
    candidate = Path(raw_path)
    if candidate.is_absolute():
        return candidate.resolve()
    return (project_dir / candidate).resolve()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-dir", required=True)
    parser.add_argument("--prd-path", required=True)
    parser.add_argument("--output-path", required=False)
    args = parser.parse_args()

    project_dir = Path(args.project_dir).resolve()
    prd_path = Path(args.prd_path).resolve()
    output_path = resolve_output_path(project_dir, args.output_path)

    if not project_dir.exists() or not project_dir.is_dir():
        print(f"[FAIL] Project directory does not exist: {project_dir}")
        return 1
    if not prd_path.exists() or not prd_path.is_file():
        print(f"[FAIL] PRD file does not exist: {prd_path}")
        return 1

    requirements = extract_prd_requirements(prd_path)
    if not requirements:
        print("[FAIL] No FR-* or NFR-* requirement IDs were found in the PRD.")
        return 1

    existing_entries = load_existing_entries(output_path)
    merged_requirements: list[dict[str, Any]] = []
    for requirement in requirements:
        requirement_id = requirement["id"]
        existing = existing_entries.get(requirement_id, {})

        status = str(existing.get("status", "not-started")).strip().lower()
        if not status:
            status = "not-started"

        merged_requirements.append(
            {
                "id": requirement_id,
                "priority": requirement["priority"],
                "status": status,
                "code": normalize_str_list(existing.get("code")),
                "tests": normalize_str_list(existing.get("tests")),
                "notes": str(existing.get("notes", "")).strip(),
            }
        )

    payload = {
        "schemaVersion": 1,
        "generatedAt": utc_now_iso(),
        "generatedFromPrd": str(prd_path),
        "requirements": merged_requirements,
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    p0_count = sum(1 for item in requirements if item["priority"] == "P0")
    print(f"[OK] Wrote PRD implementation report: {output_path}")
    print(
        f"[OK] Requirements mapped: total={len(requirements)} p0={p0_count}."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
