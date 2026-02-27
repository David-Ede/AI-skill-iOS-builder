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

    if not has_router_plugin(expo.get("plugins", [])):
        errors.append("app.json is missing expo-router in expo.plugins.")

    return errors


def check_app_config_ts(app_config_path: Path) -> list[str]:
    errors: list[str] = []
    content = app_config_path.read_text(encoding="utf-8-sig")
    if not re.search(r"bundleIdentifier\s*:\s*['\"][^'\"]+['\"]", content):
        errors.append("app.config.ts is missing ios.bundleIdentifier.")
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


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-dir", required=True)
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

        metadata_path = project_dir / "skill.modules.json"
        modules: dict[str, bool] = {}
        release_branch = "main"
        use_app_config_ts = False
        if metadata_path.exists():
            try:
                metadata = load_json(metadata_path)
                release_branch_raw = metadata.get("releaseBranch", "main")
                if isinstance(release_branch_raw, str) and release_branch_raw.strip():
                    release_branch = release_branch_raw.strip()
                raw_modules = metadata.get("modules", {})
                if isinstance(raw_modules, dict):
                    modules = {k: bool(v) for k, v in raw_modules.items()}
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

        module_contracts: list[tuple[str, str, list[str]]] = [
            (
                "withUiFoundation",
                "MC-001 UI Foundation Contract",
                [
                    "app/(tabs)/_layout.tsx",
                    "app/(tabs)/index.tsx",
                    "app/(tabs)/explore.tsx",
                    "app/(tabs)/profile.tsx",
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
        "schemaVersion": 2,
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
