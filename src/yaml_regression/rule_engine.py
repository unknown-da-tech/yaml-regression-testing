from typing import Any, Dict, List


Finding = Dict[str, Any]


def create_finding(
    rule_id: str,
    severity: str,
    category: str,
    path: str,
    message: str,
    recommendation: str,
) -> Finding:
    """
    Create a standard rule finding.
    """

    return {
        "rule_id": rule_id,
        "severity": severity,
        "category": category,
        "path": path,
        "message": message,
        "recommendation": recommendation,
    }


def detect_pull_request_trigger_removed(diff: Dict[str, Any]) -> List[Finding]:
    """
    R001: Detect if the pull_request trigger was removed.
    """

    findings = []

    for item in diff.get("removed", []):
        if item.get("path") == "on.pull_request":
            findings.append(
                create_finding(
                    rule_id="R001",
                    severity="high",
                    category="trigger-safety",
                    path=item["path"],
                    message="Pull request trigger was removed.",
                    recommendation="Restore the pull_request trigger so changes are validated before merging.",
                )
            )

    return findings


def detect_test_step_removed(diff: Dict[str, Any]) -> List[Finding]:
    """
    R002: Detect if a test step was removed.
    """

    findings = []

    for item in diff.get("removed", []):
        old_value = item.get("old")
        path = item.get("path", "")

        if isinstance(old_value, dict):
            step_name = str(old_value.get("name", "")).lower()
            run_command = str(old_value.get("run", "")).lower()

            if "test" in step_name or "test" in run_command:
                findings.append(
                    create_finding(
                        rule_id="R002",
                        severity="high",
                        category="test-coverage",
                        path=path,
                        message="A test step was removed.",
                        recommendation="Restore the removed test step or add an equivalent test command.",
                    )
                )

    return findings


def detect_deployment_condition_removed(diff: Dict[str, Any]) -> List[Finding]:
    """
    R003: Detect if a deployment condition was removed.
    """

    findings = []

    for item in diff.get("removed", []):
        path = item.get("path", "")

        if path.endswith(".if") and "deploy" in path.lower():
            findings.append(
                create_finding(
                    rule_id="R003",
                    severity="critical",
                    category="deployment-safety",
                    path=path,
                    message="Deployment condition was removed.",
                    recommendation="Restore the deployment condition, especially for production deployments.",
                )
            )

    return findings


def detect_permission_increase(diff: Dict[str, Any]) -> List[Finding]:
    """
    R004: Detect if workflow permissions increased from read to write.
    """

    findings = []

    for item in diff.get("changed", []):
        path = item.get("path", "")
        old_value = item.get("old")
        new_value = item.get("new")

        if path.startswith("permissions.") and old_value == "read" and new_value == "write":
            findings.append(
                create_finding(
                    rule_id="R004",
                    severity="critical",
                    category="security",
                    path=path,
                    message="Workflow permission increased from read to write.",
                    recommendation="Use the least privilege required. Keep permission as read unless write access is necessary.",
                )
            )

    for item in diff.get("added", []):
        path = item.get("path", "")
        value = item.get("value")

        if path.startswith("permissions.") and value == "write":
            findings.append(
                create_finding(
                    rule_id="R004",
                    severity="critical",
                    category="security",
                    path=path,
                    message="New write permission was added.",
                    recommendation="Avoid adding write permissions unless they are explicitly required.",
                )
            )

    return findings


def detect_main_branch_changed(diff: Dict[str, Any]) -> List[Finding]:
    """
    R005: Detect if a branch changed from main to another branch.
    """

    findings = []

    for item in diff.get("changed", []):
        path = item.get("path", "")
        old_value = item.get("old")
        new_value = item.get("new")

        if "branches" in path and old_value == "main" and new_value != "main":
            findings.append(
                create_finding(
                    rule_id="R005",
                    severity="high",
                    category="branch-safety",
                    path=path,
                    message=f"Branch changed from main to {new_value}.",
                    recommendation="Verify that changing the branch from main is intentional.",
                )
            )

    return findings


def run_rules(diff: Dict[str, Any]) -> List[Finding]:
    """
    Run all regression detection rules.
    """

    findings = []

    rule_functions = [
        detect_pull_request_trigger_removed,
        detect_test_step_removed,
        detect_deployment_condition_removed,
        detect_permission_increase,
        detect_main_branch_changed,
    ]

    for rule_function in rule_functions:
        findings.extend(rule_function(diff))

    return findings