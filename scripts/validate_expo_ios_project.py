#!/usr/bin/env python3
"""Validate Expo iOS project contracts for expo-ios-app-builder."""

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

PLACEHOLDER_SCAN_EXTENSIONS: tuple[str, ...] = (".ts", ".tsx", ".js", ".jsx")
PLACEHOLDER_SCAN_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"\bplaceholder(s)?\b", re.IGNORECASE),
    re.compile(r"\bstarter\b", re.IGNORECASE),
    re.compile(r"baseline scaffold", re.IGNORECASE),
    re.compile(r"\bcoming soon\b", re.IGNORECASE),
    re.compile(r"\bmock data\b", re.IGNORECASE),
    re.compile(r"\btodo\b", re.IGNORECASE),
)

BASELINE_TEST_FILES: frozenset[str] = frozenset(
    {
        "__tests__/app-shell.test.tsx",
        "__tests__/auth-oauth.test.ts",
        "__tests__/notification-deeplink.test.ts",
        "__tests__/async-resource.test.ts",
    }
)

IMPLEMENTED_STATUSES: frozenset[str] = frozenset(
    {"implemented", "complete", "completed", "done", "pass"}
)

DEFAULT_PRD_IMPLEMENTATION_REPORT_REL_PATH = "reports/prd-implementation.json"


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception as exc:  # pragma: no cover - defensive parse guard
        raise ValueError(f"Failed to parse JSON at {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError(f"JSON root must be an object at {path}")
    return data


def has_plugin(plugins: Any, plugin_name: str) -> bool:
    if not isinstance(plugins, list):
        return False
    for plugin in plugins:
        if isinstance(plugin, str) and plugin == plugin_name:
            return True
        if isinstance(plugin, list) and plugin and plugin[0] == plugin_name:
            return True
    return False


def has_router_plugin(plugins: Any) -> bool:
    return has_plugin(plugins, "expo-router")


def check_app_json(app_json_path: Path) -> list[str]:
    errors: list[str] = []
    data = load_json(app_json_path)
    expo = data.get("expo")
    if not isinstance(expo, dict):
        errors.append("app.json is missing top-level expo object.")
        return errors

    ios = expo.get("ios")
    if not isinstance(ios, dict) or not ios.get("bundleIdentifier"):
        errors.append("app.json is missing expo.ios.bundleIdentifier.")
    ios_config = ios.get("config") if isinstance(ios, dict) else None
    uses_non_exempt = (
        ios_config.get("usesNonExemptEncryption")
        if isinstance(ios_config, dict)
        else None
    )
    if not isinstance(uses_non_exempt, bool):
        errors.append(
            "app.json is missing expo.ios.config.usesNonExemptEncryption boolean."
        )

    if not has_router_plugin(expo.get("plugins", [])):
        errors.append("app.json is missing expo-router in expo.plugins.")
    if expo.get("userInterfaceStyle") != "automatic":
        errors.append('app.json must set expo.userInterfaceStyle to "automatic".')

    return errors


def check_app_config_ts(app_config_path: Path) -> list[str]:
    errors: list[str] = []
    content = app_config_path.read_text(encoding="utf-8-sig")
    if not re.search(r"bundleIdentifier\s*:\s*['\"][^'\"]+['\"]", content):
        errors.append("app.config.ts is missing ios.bundleIdentifier.")
    if not re.search(r"usesNonExemptEncryption\s*:\s*(true|false)", content):
        errors.append("app.config.ts is missing ios.config.usesNonExemptEncryption.")
    if not re.search(r"userInterfaceStyle\s*:\s*['\"]automatic['\"]", content):
        errors.append('app.config.ts must set userInterfaceStyle to "automatic".')
    if "expo-router" not in content:
        errors.append("app.config.ts is missing expo-router plugin reference.")
    return errors


def check_eas_json(eas_path: Path) -> list[str]:
    errors: list[str] = []
    data = load_json(eas_path)
    build = data.get("build")
    if not isinstance(build, dict):
        return ["eas.json is missing build section."]

    if "preview" not in build:
        errors.append("eas.json is missing build.preview profile.")
    if "production" not in build:
        errors.append("eas.json is missing build.production profile.")
    return errors


def check_gitignore_expo_rules(project_dir: Path) -> list[str]:
    errors: list[str] = []
    gitignore_path = project_dir / ".gitignore"
    if not gitignore_path.exists():
        return [".gitignore is missing."]

    content = gitignore_path.read_text(encoding="utf-8-sig")
    if not re.search(r"(?m)^\.expo/\s*$", content):
        errors.append(".gitignore is missing .expo/ ignore rule.")
    if not re.search(r"(?m)^\.expo-shared/\s*$", content):
        errors.append(".gitignore is missing .expo-shared/ ignore rule.")
    return errors


def is_placeholder_test_script(script: str) -> bool:
    normalized = script.strip().lower()
    placeholder_patterns = (
        "no tests configured yet",
        "echo",
        "placeholder",
        "todo",
    )
    return any(pattern in normalized for pattern in placeholder_patterns)


def add_check(
    checks: list[dict[str, Any]],
    check_id: str,
    name: str,
    blocking: str,
    result: str,
    reason: str = "",
) -> None:
    checks.append(
        {
            "id": check_id,
            "name": name,
            "blocking": blocking,
            "result": result,
            "reason": reason,
        }
    )


def compute_infra_status(checks: list[dict[str, Any]]) -> str:
    has_blocker_fail = any(
        check["blocking"] == "Blocker" and check["result"] == "fail" for check in checks
    )
    return "fail" if has_blocker_fail else "pass"


def compute_feature_status(module_checks: list[dict[str, Any]]) -> str:
    if not module_checks:
        return "pass"
    failed = [check for check in module_checks if check["result"] == "fail"]
    if failed:
        return "fail"
    return "pass"


def compute_status(
    infra_status: str, feature_status: str, checks: list[dict[str, Any]]
) -> str:
    if infra_status == "fail":
        return "fail"
    if feature_status == "fail":
        return "fail"
    conditional_failed = any(
        check["blocking"] == "Conditional" and check["result"] == "fail" for check in checks
    )
    if conditional_failed:
        return "partial"
    if feature_status == "partial":
        return "partial"
    return "pass"


def print_check_result(check: dict[str, Any]) -> None:
    prefix = {
        "pass": "[OK]",
        "fail": "[FAIL]",
        "skipped": "[SKIP]",
    }.get(check["result"], "[INFO]")

    if check.get("reason"):
        print(
            f"{prefix} {check['id']} {check['name']} ({check['blocking']}): {check['reason']}"
        )
    else:
        print(f"{prefix} {check['id']} {check['name']} ({check['blocking']})")


def check_required_files(project_dir: Path, rel_paths: list[str]) -> list[str]:
    missing: list[str] = []
    for rel_path in rel_paths:
        if not (project_dir / rel_path).exists():
            missing.append(rel_path)
    return missing


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


def resolve_project_path(project_dir: Path, raw_path: str) -> tuple[Path | None, str]:
    candidate = Path(raw_path)
    resolved = candidate if candidate.is_absolute() else (project_dir / candidate)
    resolved = resolved.resolve()
    try:
        relative = resolved.relative_to(project_dir)
    except ValueError:
        return None, ""
    return resolved, relative.as_posix()


def normalize_requirement_id(value: Any) -> str:
    if not isinstance(value, str):
        return ""
    requirement_id = value.strip().upper()
    if PRD_REQUIREMENT_PATTERN.fullmatch(requirement_id):
        return requirement_id
    return ""


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


def scan_placeholder_markers(project_dir: Path, limit: int = 20) -> list[str]:
    findings: list[str] = []
    roots = [project_dir / "app", project_dir / "src", project_dir / "__tests__"]
    for root in roots:
        if not root.exists() or not root.is_dir():
            continue
        for file_path in root.rglob("*"):
            if (
                not file_path.is_file()
                or file_path.suffix.lower() not in PLACEHOLDER_SCAN_EXTENSIONS
            ):
                continue

            try:
                content = file_path.read_text(encoding="utf-8-sig")
            except UnicodeDecodeError:
                continue

            for line_number, line in enumerate(content.splitlines(), start=1):
                for pattern in PLACEHOLDER_SCAN_PATTERNS:
                    if not pattern.search(line):
                        continue
                    relative_path = file_path.relative_to(project_dir).as_posix()
                    findings.append(
                        f"{relative_path}:{line_number}: {line.strip()[:140]}"
                    )
                    break
                if len(findings) >= limit:
                    return findings
    return findings


def load_prd_implementation_report(path: Path) -> dict[str, Any]:
    report = load_json(path)
    requirements = report.get("requirements")
    if not isinstance(requirements, list):
        raise ValueError(
            f"{path} is missing 'requirements' array for PRD implementation mapping."
        )
    return report


REQUIRED_HUMAN_INPUT_FIELDS: tuple[tuple[str, str], ...] = (
    ("APP_NAME", "product-owner"),
    ("IOS_BUNDLE_ID", "mobile-lead"),
    ("ASC_APP_ID", "release-manager"),
    ("ASC_SKU", "product-owner"),
    ("PRIMARY_LANGUAGE", "product-owner"),
    ("APPLE_DEV_MEMBERSHIP_ACTIVE", "release-manager"),
    ("APP_STORE_CONNECT_ROLE_OK", "release-manager"),
    ("EXPO_EAS_ACCESS_OK", "mobile-lead"),
    ("GITHUB_REPO_READY", "mobile-lead"),
    ("RELEASE_BRANCH", "mobile-lead"),
    ("GITHUB_SECRET_EXPO_TOKEN", "release-manager"),
    ("ASC_API_KEY_CONFIGURED", "release-manager"),
    ("SUPPORT_URL", "product-owner"),
    ("PRIVACY_POLICY_URL", "legal"),
)

YES_NO_HUMAN_INPUT_FIELDS: tuple[str, ...] = (
    "APPLE_DEV_MEMBERSHIP_ACTIVE",
    "APP_STORE_CONNECT_ROLE_OK",
    "EXPO_EAS_ACCESS_OK",
    "GITHUB_REPO_READY",
    "ASC_API_KEY_CONFIGURED",
    "SCREENSHOTS_READY",
    "TESTFLIGHT_INTERNAL_TESTERS_READY",
    "REVIEW_NOTES_READY",
)


def strip_optional_quotes(value: str) -> str:
    normalized = value.strip()
    if len(normalized) >= 2:
        if normalized[0] == normalized[-1] and normalized[0] in ("'", '"'):
            return normalized[1:-1].strip()
    return normalized


def parse_human_inputs_markdown(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    content = path.read_text(encoding="utf-8-sig")
    for line in content.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        match = re.match(r"^([A-Z0-9_]+)\s*=\s*(.*)$", stripped)
        if not match:
            continue
        key = match.group(1)
        raw_value = match.group(2)
        values[key] = strip_optional_quotes(raw_value)
    return values


def extract_app_identity(project_dir: Path, use_app_config_ts: bool) -> dict[str, str]:
    identity: dict[str, str] = {
        "bundleIdentifier": "",
        "version": "",
        "buildNumber": "",
    }

    app_json_path = project_dir / "app.json"
    app_config_path = project_dir / "app.config.ts"

    if not use_app_config_ts and app_json_path.exists():
        try:
            data = load_json(app_json_path)
        except ValueError:
            return identity
        expo = data.get("expo", {})
        if isinstance(expo, dict):
            ios = expo.get("ios", {})
            if isinstance(ios, dict):
                bundle = ios.get("bundleIdentifier")
                build_number = ios.get("buildNumber")
                if isinstance(bundle, str):
                    identity["bundleIdentifier"] = bundle.strip()
                if isinstance(build_number, str):
                    identity["buildNumber"] = build_number.strip()
            version = expo.get("version")
            if isinstance(version, str):
                identity["version"] = version.strip()
        return identity

    if not app_config_path.exists():
        return identity

    content = app_config_path.read_text(encoding="utf-8-sig")
    bundle_match = re.search(r"bundleIdentifier\s*:\s*['\"]([^'\"]+)['\"]", content)
    version_match = re.search(r"\bversion\s*:\s*['\"]([^'\"]+)['\"]", content)
    build_number_match = re.search(r"buildNumber\s*:\s*['\"]([^'\"]+)['\"]", content)

    if bundle_match:
        identity["bundleIdentifier"] = bundle_match.group(1).strip()
    if version_match:
        identity["version"] = version_match.group(1).strip()
    if build_number_match:
        identity["buildNumber"] = build_number_match.group(1).strip()

    return identity


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-dir", required=True)
    parser.add_argument(
        "--prd-path",
        required=True,
        help="Path to completed PRD used as implementation contract.",
    )
    parser.add_argument(
        "--implementation-report-path",
        required=False,
        help=(
            "Optional path to PRD implementation report JSON. "
            "Defaults to <project-dir>/reports/prd-implementation.json."
        ),
    )
    parser.add_argument(
        "--report-path",
        required=False,
        help="Optional path to write machine-readable validation report JSON.",
    )
    args = parser.parse_args()

    started_at = utc_now_iso()
    project_dir = Path(args.project_dir).resolve()
    checks: list[dict[str, Any]] = []
    module_checks: list[dict[str, Any]] = []
    warnings: list[str] = []
    unresolved_human_dependencies: list[dict[str, str]] = []
    prd_requirement_ids: list[str] = []
    p0_requirement_ids: list[str] = []
    missing_requirement_mappings: list[str] = []
    p0_implementation_failures: list[str] = []
    placeholder_findings: list[str] = []

    if not project_dir.exists() or not project_dir.is_dir():
        add_check(
            checks,
            "VC-000",
            "Project Directory Exists",
            "Blocker",
            "fail",
            f"Project directory does not exist: {project_dir}",
        )
    else:
        add_check(checks, "VC-000", "Project Directory Exists", "Blocker", "pass")

    package_json_path = project_dir / "package.json"
    pkg: dict[str, Any] | None = None
    if checks[-1]["result"] == "pass":
        if package_json_path.exists():
            add_check(checks, "VC-001", "package.json Exists", "Blocker", "pass")
            try:
                pkg = load_json(package_json_path)
                add_check(checks, "VC-002", "package.json Parse", "Blocker", "pass")
            except ValueError as exc:
                add_check(
                    checks,
                    "VC-002",
                    "package.json Parse",
                    "Blocker",
                    "fail",
                    str(exc),
                )
        else:
            add_check(
                checks,
                "VC-001",
                "package.json Exists",
                "Blocker",
                "fail",
                "package.json not found.",
            )

    if isinstance(pkg, dict):
        scripts = pkg.get("scripts", {})
        for check_id, script_name in (
            ("VC-003", "lint"),
            ("VC-004", "typecheck"),
            ("VC-005", "test"),
        ):
            if isinstance(scripts, dict) and script_name in scripts:
                add_check(
                    checks,
                    check_id,
                    f"package.json scripts.{script_name}",
                    "Blocker",
                    "pass",
                )
            else:
                add_check(
                    checks,
                    check_id,
                    f"package.json scripts.{script_name}",
                    "Blocker",
                    "fail",
                    f"scripts.{script_name} is missing",
                )

        test_script = ""
        if isinstance(scripts, dict):
            raw_test = scripts.get("test")
            if isinstance(raw_test, str):
                test_script = raw_test
        if test_script and not is_placeholder_test_script(test_script):
            add_check(
                checks,
                "VC-014",
                "Non-placeholder Test Script",
                "Blocker",
                "pass",
            )
        else:
            reason = (
                "scripts.test is missing or appears to be placeholder/no-op"
                if not test_script
                else f"scripts.test appears to be placeholder/no-op: {test_script}"
            )
            add_check(
                checks,
                "VC-014",
                "Non-placeholder Test Script",
                "Blocker",
                "fail",
                reason,
            )

        main_entry = pkg.get("main")
        if main_entry == "expo-router/entry":
            add_check(
                checks,
                "VC-006",
                "package.json main Entry",
                "Blocker",
                "pass",
            )
        else:
            add_check(
                checks,
                "VC-006",
                "package.json main Entry",
                "Blocker",
                "fail",
                "package.json main must be expo-router/entry",
            )

        deps: dict[str, Any] = {}
        if isinstance(pkg.get("dependencies"), dict):
            deps.update(pkg["dependencies"])
        if isinstance(pkg.get("devDependencies"), dict):
            deps.update(pkg["devDependencies"])

        if "expo-router" in deps:
            add_check(
                checks,
                "VC-007",
                "expo-router Dependency",
                "Blocker",
                "pass",
            )
        else:
            add_check(
                checks,
                "VC-007",
                "expo-router Dependency",
                "Blocker",
                "fail",
                "expo-router dependency is missing",
            )

        if (project_dir / "tsconfig.json").exists():
            add_check(
                checks,
                "VC-008",
                "tsconfig.json Exists",
                "Blocker",
                "pass",
            )
        else:
            add_check(
                checks,
                "VC-008",
                "tsconfig.json Exists",
                "Blocker",
                "fail",
                "tsconfig.json is missing",
            )

        if "typescript" in deps:
            add_check(
                checks,
                "VC-009",
                "TypeScript Dependency",
                "Blocker",
                "pass",
            )
        else:
            add_check(
                checks,
                "VC-009",
                "TypeScript Dependency",
                "Blocker",
                "fail",
                "typescript dependency is missing",
            )

        app_json_path = project_dir / "app.json"
        app_config_ts_path = project_dir / "app.config.ts"
        app_errors: list[str] = []
        if app_json_path.exists():
            try:
                app_errors = check_app_json(app_json_path)
            except ValueError as exc:
                app_errors = [str(exc)]
        elif app_config_ts_path.exists():
            app_errors = check_app_config_ts(app_config_ts_path)
        else:
            app_errors = ["Neither app.json nor app.config.ts was found."]

        if app_errors:
            add_check(
                checks,
                "VC-010",
                "App Config Contract",
                "Blocker",
                "fail",
                " | ".join(app_errors),
            )
        else:
            add_check(
                checks,
                "VC-010",
                "App Config Contract",
                "Blocker",
                "pass",
            )

        eas_path = project_dir / "eas.json"
        if eas_path.exists():
            try:
                eas_errors = check_eas_json(eas_path)
            except ValueError as exc:
                eas_errors = [str(exc)]
        else:
            eas_errors = ["eas.json is missing."]

        if eas_errors:
            add_check(
                checks,
                "VC-011",
                "EAS Profile Contract",
                "Blocker",
                "fail",
                " | ".join(eas_errors),
            )
        else:
            add_check(
                checks,
                "VC-011",
                "EAS Profile Contract",
                "Blocker",
                "pass",
            )

        gitignore_errors = check_gitignore_expo_rules(project_dir)
        if gitignore_errors:
            add_check(
                checks,
                "VC-012",
                "Expo Ignore Policy",
                "Blocker",
                "fail",
                " | ".join(gitignore_errors),
            )
        else:
            add_check(
                checks,
                "VC-012",
                "Expo Ignore Policy",
                "Blocker",
                "pass",
            )

        workflow_path = project_dir / ".github" / "workflows" / "eas-ios.yml"
        if workflow_path.exists():
            add_check(
                checks,
                "VC-013",
                "CI Workflow Presence",
                "Conditional",
                "pass",
            )
        else:
            add_check(
                checks,
                "VC-013",
                "CI Workflow Presence",
                "Conditional",
                "skipped",
                "CI workflow not found yet (expected before setup_ci_eas.ps1).",
            )
            warnings.append(
                "CI workflow missing; run setup_ci_eas.ps1 to complete pipeline setup."
            )

        smoke_test_path = project_dir / "__tests__" / "app-shell.test.tsx"
        if smoke_test_path.exists():
            add_check(
                checks,
                "VC-016",
                "Smoke Test File Presence",
                "Blocker",
                "pass",
            )
        else:
            add_check(
                checks,
                "VC-016",
                "Smoke Test File Presence",
                "Blocker",
                "fail",
                "__tests__/app-shell.test.tsx is missing.",
            )

        theme_file_path = project_dir / "src" / "ui" / "theme.ts"
        if theme_file_path.exists():
            add_check(
                checks,
                "VC-024",
                "Theme Token File Presence",
                "Blocker",
                "pass",
            )
        else:
            add_check(
                checks,
                "VC-024",
                "Theme Token File Presence",
                "Blocker",
                "fail",
                "src/ui/theme.ts is missing.",
            )

        metadata_path = project_dir / "skill.modules.json"
        modules: dict[str, bool] = {}
        release_branch = "main"
        use_app_config_ts = False
        with_deployment_layer = False
        if metadata_path.exists():
            try:
                metadata = load_json(metadata_path)
                release_branch_raw = metadata.get("releaseBranch", "main")
                if isinstance(release_branch_raw, str) and release_branch_raw.strip():
                    release_branch = release_branch_raw.strip()
                raw_modules = metadata.get("modules", {})
                if isinstance(raw_modules, dict):
                    modules = {k: bool(v) for k, v in raw_modules.items()}
                with_deployment_layer = bool(modules.get("withDeploymentLayer", False))
                add_check(
                    checks,
                    "VC-015",
                    "skill.modules.json Parse",
                    "Blocker",
                    "pass",
                )
                use_app_config_ts = bool(modules.get("useAppConfigTs", False))
                if use_app_config_ts:
                    if (project_dir / "app.config.ts").exists():
                        add_check(
                            checks,
                            "VC-018",
                            "app.config.ts Mode Contract",
                            "Blocker",
                            "pass",
                        )
                    else:
                        add_check(
                            checks,
                            "VC-018",
                            "app.config.ts Mode Contract",
                            "Blocker",
                            "fail",
                            "useAppConfigTs is enabled but app.config.ts is missing.",
                        )
                else:
                    if (project_dir / "app.json").exists():
                        add_check(
                            checks,
                            "VC-018",
                            "app.json Mode Contract",
                            "Blocker",
                            "pass",
                        )
                    else:
                        add_check(
                            checks,
                            "VC-018",
                            "app.json Mode Contract",
                            "Blocker",
                            "fail",
                            "useAppConfigTs is disabled but app.json is missing.",
                        )
            except ValueError as exc:
                add_check(
                    checks,
                    "VC-015",
                    "skill.modules.json Parse",
                    "Blocker",
                    "fail",
                    str(exc),
                )
        else:
                add_check(
                    checks,
                    "VC-015",
                    "skill.modules.json Parse",
                    "Blocker",
                    "fail",
                    "skill.modules.json is missing.",
                )

        if bool(modules.get("withPush", False)):
            if use_app_config_ts:
                push_config_path = project_dir / "app.config.ts"
                if not push_config_path.exists():
                    add_check(
                        checks,
                        "VC-019",
                        "Push Plugin Contract",
                        "Blocker",
                        "fail",
                        "withPush is enabled but app.config.ts is missing.",
                    )
                else:
                    config_content = push_config_path.read_text(encoding="utf-8-sig")
                    if "expo-notifications" in config_content:
                        add_check(
                            checks,
                            "VC-019",
                            "Push Plugin Contract",
                            "Blocker",
                            "pass",
                        )
                    else:
                        add_check(
                            checks,
                            "VC-019",
                            "Push Plugin Contract",
                            "Blocker",
                            "fail",
                            "withPush is enabled but app.config.ts is missing expo-notifications plugin.",
                        )
            else:
                if not app_json_path.exists():
                    add_check(
                        checks,
                        "VC-019",
                        "Push Plugin Contract",
                        "Blocker",
                        "fail",
                        "withPush is enabled but app.json is missing.",
                    )
                else:
                    try:
                        app_json = load_json(app_json_path)
                        expo_cfg = app_json.get("expo", {})
                        plugins = expo_cfg.get("plugins", []) if isinstance(expo_cfg, dict) else []
                        has_push_plugin = has_plugin(plugins, "expo-notifications")
                    except ValueError as exc:
                        add_check(
                            checks,
                            "VC-019",
                            "Push Plugin Contract",
                            "Blocker",
                            "fail",
                            str(exc),
                        )
                    else:
                        if has_push_plugin:
                            add_check(
                                checks,
                                "VC-019",
                                "Push Plugin Contract",
                                "Blocker",
                                "pass",
                            )
                        else:
                            add_check(
                                checks,
                                "VC-019",
                                "Push Plugin Contract",
                                "Blocker",
                                "fail",
                                "withPush is enabled but app.json is missing expo-notifications plugin.",
                            )

        if workflow_path.exists():
            workflow_content = workflow_path.read_text(encoding="utf-8-sig")
            expected_ref = f"refs/heads/{release_branch}"
            expected_branch_line = f"- {release_branch}"
            if expected_ref in workflow_content and expected_branch_line in workflow_content:
                add_check(
                    checks,
                    "VC-017",
                    "Workflow Release Branch Contract",
                    "Conditional",
                    "pass",
                )
            else:
                add_check(
                    checks,
                    "VC-017",
                    "Workflow Release Branch Contract",
                    "Conditional",
                    "fail",
                    f"Workflow does not appear to target release branch '{release_branch}'.",
                )

        if with_deployment_layer:
            human_inputs_path = project_dir / "release" / "human-inputs.md"
            if human_inputs_path.exists():
                add_check(
                    checks,
                    "VC-020",
                    "Deployment Human Input File Presence",
                    "Conditional",
                    "pass",
                )
                human_inputs = parse_human_inputs_markdown(human_inputs_path)

                missing_required_fields: list[str] = []
                for key, owner in REQUIRED_HUMAN_INPUT_FIELDS:
                    if not human_inputs.get(key):
                        missing_required_fields.append(key)
                        unresolved_human_dependencies.append(
                            {
                                "field": key,
                                "owner": owner,
                                "nextAction": "Fill value in release/human-inputs.md",
                            }
                        )

                if missing_required_fields:
                    add_check(
                        checks,
                        "VC-021",
                        "Deployment Human Input Required Fields",
                        "Conditional",
                        "fail",
                        "Missing required values: " + ", ".join(missing_required_fields),
                    )
                else:
                    add_check(
                        checks,
                        "VC-021",
                        "Deployment Human Input Required Fields",
                        "Conditional",
                        "pass",
                    )

                invalid_yes_no_fields: list[str] = []
                for field in YES_NO_HUMAN_INPUT_FIELDS:
                    value = human_inputs.get(field, "")
                    if value and value.strip().lower() not in {"yes", "no"}:
                        invalid_yes_no_fields.append(field)
                if invalid_yes_no_fields:
                    add_check(
                        checks,
                        "VC-022",
                        "Deployment Human Input Boolean Field Format",
                        "Conditional",
                        "fail",
                        "Expected yes/no values for: "
                        + ", ".join(invalid_yes_no_fields),
                    )
                else:
                    add_check(
                        checks,
                        "VC-022",
                        "Deployment Human Input Boolean Field Format",
                        "Conditional",
                        "pass",
                    )

                app_identity = extract_app_identity(project_dir, use_app_config_ts)
                mismatches: list[str] = []
                file_bundle = human_inputs.get("IOS_BUNDLE_ID", "").strip()
                file_version = human_inputs.get("APP_VERSION", "").strip()
                file_build_number = human_inputs.get("IOS_BUILD_NUMBER", "").strip()
                file_release_branch = human_inputs.get("RELEASE_BRANCH", "").strip()

                if (
                    file_bundle
                    and app_identity.get("bundleIdentifier")
                    and file_bundle != app_identity["bundleIdentifier"]
                ):
                    mismatches.append(
                        "IOS_BUNDLE_ID does not match app config bundleIdentifier"
                    )
                if (
                    file_version
                    and app_identity.get("version")
                    and file_version != app_identity["version"]
                ):
                    mismatches.append("APP_VERSION does not match app config version")
                if (
                    file_build_number
                    and app_identity.get("buildNumber")
                    and file_build_number != app_identity["buildNumber"]
                ):
                    mismatches.append(
                        "IOS_BUILD_NUMBER does not match app config ios.buildNumber"
                    )
                if file_release_branch and file_release_branch != release_branch:
                    mismatches.append(
                        "RELEASE_BRANCH does not match skill.modules.json releaseBranch"
                    )

                if mismatches:
                    add_check(
                        checks,
                        "VC-023",
                        "Deployment Human Input Cross-File Alignment",
                        "Conditional",
                        "fail",
                        " | ".join(mismatches),
                    )
                else:
                    add_check(
                        checks,
                        "VC-023",
                        "Deployment Human Input Cross-File Alignment",
                        "Conditional",
                        "pass",
                    )
            else:
                add_check(
                    checks,
                    "VC-020",
                    "Deployment Human Input File Presence",
                    "Conditional",
                    "fail",
                    "release/human-inputs.md is missing while withDeploymentLayer is enabled.",
                )
                add_check(
                    checks,
                    "VC-021",
                    "Deployment Human Input Required Fields",
                    "Conditional",
                    "skipped",
                    "Skipped because release/human-inputs.md is missing.",
                )
                add_check(
                    checks,
                    "VC-022",
                    "Deployment Human Input Boolean Field Format",
                    "Conditional",
                    "skipped",
                    "Skipped because release/human-inputs.md is missing.",
                )
                add_check(
                    checks,
                    "VC-023",
                    "Deployment Human Input Cross-File Alignment",
                    "Conditional",
                    "skipped",
                    "Skipped because release/human-inputs.md is missing.",
                )
                unresolved_human_dependencies.append(
                    {
                        "field": "release/human-inputs.md",
                        "owner": "release-manager",
                        "nextAction": "Create release/human-inputs.md from skill template.",
                    }
                )
        else:
            add_check(
                checks,
                "VC-020",
                "Deployment Human Input File Presence",
                "Conditional",
                "skipped",
                "withDeploymentLayer is not enabled.",
            )
            add_check(
                checks,
                "VC-021",
                "Deployment Human Input Required Fields",
                "Conditional",
                "skipped",
                "withDeploymentLayer is not enabled.",
            )
            add_check(
                checks,
                "VC-022",
                "Deployment Human Input Boolean Field Format",
                "Conditional",
                "skipped",
                "withDeploymentLayer is not enabled.",
            )
            add_check(
                checks,
                "VC-023",
                "Deployment Human Input Cross-File Alignment",
                "Conditional",
                "skipped",
                "withDeploymentLayer is not enabled.",
            )

        module_contracts: list[tuple[str, str, list[str]]] = [
            (
                "withUiFoundation",
                "MC-001 UI Foundation Contract",
                [
                    "app/(tabs)/_layout.tsx",
                    "app/(tabs)/index.tsx",
                    "app/(tabs)/explore.tsx",
                    "app/(tabs)/profile.tsx",
                    "src/ui/StatePanel.tsx",
                    "src/ui/theme.ts",
                ],
            ),
            (
                "withProfile",
                "MC-002 Profile Contract",
                ["app/settings.tsx", "src/profile/ProfileActions.tsx"],
            ),
            (
                "withAuth",
                "MC-003 Auth Contract",
                [
                    "app/sign-in.tsx",
                    "src/auth/AuthContext.tsx",
                    "src/auth/secureSession.ts",
                    "src/auth/oauthProviders.ts",
                    "__tests__/auth-oauth.test.ts",
                ],
            ),
            (
                "withPush",
                "MC-004 Push Contract",
                [
                    "src/notifications/registerForPushNotifications.ts",
                    "src/notifications/NotificationProvider.tsx",
                    "src/notifications/notificationDeepLink.ts",
                    "__tests__/notification-deeplink.test.ts",
                ],
            ),
            (
                "withDataLayer",
                "MC-005 Data Layer Contract",
                [
                    "src/data/apiClient.ts",
                    "src/data/requestPolicy.ts",
                    "src/data/useAsyncResource.ts",
                    "__tests__/async-resource.test.ts",
                ],
            ),
            (
                "withAnalytics",
                "MC-006 Analytics Contract",
                ["src/observability/analytics.ts"],
            ),
            (
                "withCrashReporting",
                "MC-007 Crash Contract",
                ["src/observability/crashReporter.ts"],
            ),
            (
                "withLocalization",
                "MC-008 Localization Contract",
                ["src/localization/i18n.ts", "src/localization/messages/en.ts"],
            ),
            (
                "withAccessibilityChecks",
                "MC-009 Accessibility Checklist Contract",
                ["docs/accessibility-checklist.md"],
            ),
            (
                "withPrivacyChecklist",
                "MC-010 Privacy Checklist Contract",
                ["docs/privacy-checklist.md"],
            ),
        ]

        for flag_key, contract_name, required_paths in module_contracts:
            enabled = bool(modules.get(flag_key, False))
            if not enabled:
                module_checks.append(
                    {
                        "id": contract_name.split()[0],
                        "name": contract_name,
                        "result": "skipped",
                        "reason": f"{flag_key} is not enabled.",
                    }
                )
                continue
            missing = check_required_files(project_dir, required_paths)
            if missing:
                module_checks.append(
                    {
                        "id": contract_name.split()[0],
                        "name": contract_name,
                        "result": "fail",
                        "reason": "Missing required files: " + ", ".join(missing),
                    }
                )
            else:
                module_checks.append(
                    {
                        "id": contract_name.split()[0],
                        "name": contract_name,
                        "result": "pass",
                        "reason": "",
                    }
                )

        prd_path = Path(args.prd_path).resolve()
        if not prd_path.exists() or not prd_path.is_file():
            add_check(
                checks,
                "VC-025",
                "PRD Requirement Extraction",
                "Blocker",
                "fail",
                f"PRD path does not exist: {prd_path}",
            )
            add_check(
                checks,
                "VC-026",
                "PRD Implementation Report Presence",
                "Blocker",
                "skipped",
                "Skipped because PRD could not be loaded.",
            )
            add_check(
                checks,
                "VC-027",
                "PRD Mapping Completeness",
                "Blocker",
                "skipped",
                "Skipped because PRD could not be loaded.",
            )
            add_check(
                checks,
                "VC-028",
                "P0 Implementation Evidence",
                "Blocker",
                "skipped",
                "Skipped because PRD could not be loaded.",
            )
            add_check(
                checks,
                "VC-029",
                "Custom Feature Test Coverage",
                "Blocker",
                "skipped",
                "Skipped because PRD could not be loaded.",
            )
        else:
            prd_requirements: list[dict[str, str]] = []
            try:
                prd_requirements = extract_prd_requirements(prd_path)
            except Exception as exc:  # pragma: no cover - defensive parser guard
                add_check(
                    checks,
                    "VC-025",
                    "PRD Requirement Extraction",
                    "Blocker",
                    "fail",
                    f"Failed to parse PRD requirements: {exc}",
                )
            else:
                if not prd_requirements:
                    add_check(
                        checks,
                        "VC-025",
                        "PRD Requirement Extraction",
                        "Blocker",
                        "fail",
                        "No FR-* or NFR-* requirement IDs were found in the PRD.",
                    )
                else:
                    add_check(
                        checks,
                        "VC-025",
                        "PRD Requirement Extraction",
                        "Blocker",
                        "pass",
                        f"Parsed {len(prd_requirements)} requirements from PRD.",
                    )
                    prd_requirement_ids = [item["id"] for item in prd_requirements]
                    p0_requirement_ids = [
                        item["id"] for item in prd_requirements if item["priority"] == "P0"
                    ]

            if prd_requirements:
                implementation_report_path = (
                    (
                        Path(args.implementation_report_path).resolve()
                        if Path(args.implementation_report_path).is_absolute()
                        else (project_dir / args.implementation_report_path).resolve()
                    )
                    if args.implementation_report_path
                    else (
                        project_dir / DEFAULT_PRD_IMPLEMENTATION_REPORT_REL_PATH
                    ).resolve()
                )
                implementation_report: dict[str, Any] | None = None
                if not implementation_report_path.exists():
                    add_check(
                        checks,
                        "VC-026",
                        "PRD Implementation Report Presence",
                        "Blocker",
                        "fail",
                        f"Missing {implementation_report_path}. Generate it and map PRD requirements to code/tests.",
                    )
                    add_check(
                        checks,
                        "VC-027",
                        "PRD Mapping Completeness",
                        "Blocker",
                        "skipped",
                        "Skipped because PRD implementation report is missing.",
                    )
                    add_check(
                        checks,
                        "VC-028",
                        "P0 Implementation Evidence",
                        "Blocker",
                        "skipped",
                        "Skipped because PRD implementation report is missing.",
                    )
                    add_check(
                        checks,
                        "VC-029",
                        "Custom Feature Test Coverage",
                        "Blocker",
                        "skipped",
                        "Skipped because PRD implementation report is missing.",
                    )
                else:
                    try:
                        implementation_report = load_prd_implementation_report(
                            implementation_report_path
                        )
                    except ValueError as exc:
                        add_check(
                            checks,
                            "VC-026",
                            "PRD Implementation Report Presence",
                            "Blocker",
                            "fail",
                            str(exc),
                        )
                        add_check(
                            checks,
                            "VC-027",
                            "PRD Mapping Completeness",
                            "Blocker",
                            "skipped",
                            "Skipped because PRD implementation report failed to parse.",
                        )
                        add_check(
                            checks,
                            "VC-028",
                            "P0 Implementation Evidence",
                            "Blocker",
                            "skipped",
                            "Skipped because PRD implementation report failed to parse.",
                        )
                        add_check(
                            checks,
                            "VC-029",
                            "Custom Feature Test Coverage",
                            "Blocker",
                            "skipped",
                            "Skipped because PRD implementation report failed to parse.",
                        )
                    else:
                        add_check(
                            checks,
                            "VC-026",
                            "PRD Implementation Report Presence",
                            "Blocker",
                            "pass",
                            f"Loaded {implementation_report_path}.",
                        )

                        requirement_entries: dict[str, dict[str, Any]] = {}
                        for entry in implementation_report.get("requirements", []):
                            if not isinstance(entry, dict):
                                continue
                            requirement_id = normalize_requirement_id(entry.get("id"))
                            if not requirement_id:
                                continue
                            requirement_entries[requirement_id] = entry

                        missing_requirement_mappings = [
                            req_id
                            for req_id in prd_requirement_ids
                            if req_id not in requirement_entries
                        ]
                        if missing_requirement_mappings:
                            add_check(
                                checks,
                                "VC-027",
                                "PRD Mapping Completeness",
                                "Blocker",
                                "fail",
                                "Missing requirement mappings: "
                                + ", ".join(missing_requirement_mappings),
                            )
                        else:
                            add_check(
                                checks,
                                "VC-027",
                                "PRD Mapping Completeness",
                                "Blocker",
                                "pass",
                            )

                        referenced_test_paths: set[str] = set()
                        for requirement_id in p0_requirement_ids:
                            entry = requirement_entries.get(requirement_id)
                            if not entry:
                                continue

                            status = str(entry.get("status", "")).strip().lower()
                            if status not in IMPLEMENTED_STATUSES:
                                p0_implementation_failures.append(
                                    f"{requirement_id}: status must be implemented (found '{status or 'missing'}')."
                                )

                            code_paths = normalize_str_list(entry.get("code"))
                            test_paths = normalize_str_list(entry.get("tests"))
                            if not code_paths:
                                p0_implementation_failures.append(
                                    f"{requirement_id}: no code evidence paths listed."
                                )
                            if not test_paths:
                                p0_implementation_failures.append(
                                    f"{requirement_id}: no test evidence paths listed."
                                )

                            for raw_path in code_paths:
                                resolved_path, relative_path = resolve_project_path(
                                    project_dir, raw_path
                                )
                                if not resolved_path:
                                    p0_implementation_failures.append(
                                        f"{requirement_id}: code path escapes project root: {raw_path}"
                                    )
                                    continue
                                if not resolved_path.exists():
                                    p0_implementation_failures.append(
                                        f"{requirement_id}: missing code file {relative_path}"
                                    )

                            for raw_path in test_paths:
                                resolved_path, relative_path = resolve_project_path(
                                    project_dir, raw_path
                                )
                                if not resolved_path:
                                    p0_implementation_failures.append(
                                        f"{requirement_id}: test path escapes project root: {raw_path}"
                                    )
                                    continue
                                if not resolved_path.exists():
                                    p0_implementation_failures.append(
                                        f"{requirement_id}: missing test file {relative_path}"
                                    )
                                    continue

                                referenced_test_paths.add(relative_path)
                                if ".test." not in relative_path:
                                    p0_implementation_failures.append(
                                        f"{requirement_id}: test evidence must point to *.test.ts or *.test.tsx file ({relative_path})."
                                    )
                                    continue

                                test_content = resolved_path.read_text(encoding="utf-8-sig")
                                if "expect(" not in test_content:
                                    p0_implementation_failures.append(
                                        f"{requirement_id}: test file has no assertion ({relative_path})."
                                    )

                        if p0_implementation_failures:
                            add_check(
                                checks,
                                "VC-028",
                                "P0 Implementation Evidence",
                                "Blocker",
                                "fail",
                                " | ".join(p0_implementation_failures[:12]),
                            )
                        else:
                            add_check(
                                checks,
                                "VC-028",
                                "P0 Implementation Evidence",
                                "Blocker",
                                "pass",
                            )

                        has_module_features = any(
                            req_id.startswith("FR-") and not req_id.startswith("FR-GLOB-")
                            for req_id in prd_requirement_ids
                        )
                        if has_module_features:
                            custom_tests = sorted(
                                path
                                for path in referenced_test_paths
                                if path not in BASELINE_TEST_FILES
                            )
                            if custom_tests:
                                add_check(
                                    checks,
                                    "VC-029",
                                    "Custom Feature Test Coverage",
                                    "Blocker",
                                    "pass",
                                    f"Custom feature tests: {', '.join(custom_tests[:6])}",
                                )
                            else:
                                add_check(
                                    checks,
                                    "VC-029",
                                    "Custom Feature Test Coverage",
                                    "Blocker",
                                    "fail",
                                    "Only baseline tests are mapped. Add feature-specific tests for module requirements.",
                                )
                        else:
                            add_check(
                                checks,
                                "VC-029",
                                "Custom Feature Test Coverage",
                                "Blocker",
                                "skipped",
                                "No module-specific FR requirements were found in PRD.",
                            )

        placeholder_findings = scan_placeholder_markers(project_dir)
        if placeholder_findings:
            add_check(
                checks,
                "VC-030",
                "Placeholder Marker Scan",
                "Blocker",
                "fail",
                "Found unresolved placeholder markers in source files.",
            )
        else:
            add_check(
                checks,
                "VC-030",
                "Placeholder Marker Scan",
                "Blocker",
                "pass",
            )

    infra_status = compute_infra_status(checks)
    feature_status = compute_feature_status(module_checks)
    status = compute_status(infra_status, feature_status, checks)
    finished_at = utc_now_iso()

    for check in checks:
        print_check_result(check)
    for module_check in module_checks:
        print_check_result(
            {
                "id": module_check["id"],
                "name": module_check["name"],
                "blocking": "Module",
                "result": module_check["result"],
                "reason": module_check.get("reason", ""),
            }
        )

    if status == "pass":
        print("Validation passed.")
    elif status == "partial":
        print("Validation partial: blockers passed but conditional or feature checks need follow-up.")
    else:
        print("Validation failed.")

    report = {
        "schemaVersion": 4,
        "status": status,
        "infraStatus": infra_status,
        "featureStatus": feature_status,
        "startedAt": started_at,
        "finishedAt": finished_at,
        "projectDir": str(project_dir),
        "checks": checks,
        "moduleChecks": module_checks,
        "failedChecks": [
            check["id"] for check in checks if check["result"] == "fail"
        ]
        + [check["id"] for check in module_checks if check["result"] == "fail"],
        "warnings": warnings,
        "unresolvedHumanDependencies": unresolved_human_dependencies,
        "prdRequirementIds": prd_requirement_ids,
        "p0RequirementIds": p0_requirement_ids,
        "missingRequirementMappings": missing_requirement_mappings,
        "p0ImplementationFailures": p0_implementation_failures,
        "placeholderFindings": placeholder_findings,
    }

    if args.report_path:
        report_path = Path(args.report_path).resolve()
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(
            json.dumps(report, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        print(f"[OK] Wrote report: {report_path}")

    return 0 if status == "pass" else 1


if __name__ == "__main__":
    sys.exit(main())
