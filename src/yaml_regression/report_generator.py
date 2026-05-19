import json
from pathlib import Path
from typing import Any, Dict, List


Finding = Dict[str, Any]


SEVERITY_ORDER = {
    "critical": 4,
    "high": 3,
    "medium": 2,
    "low": 1,
}


def calculate_overall_risk(findings: List[Finding]) -> str:
    """
    Calculate the overall risk based on the highest severity finding.
    """

    if not findings:
        return "none"

    highest = "low"

    for finding in findings:
        severity = finding.get("severity", "low").lower()

        if SEVERITY_ORDER.get(severity, 0) > SEVERITY_ORDER.get(highest, 0):
            highest = severity

    return highest


def count_findings_by_severity(findings: List[Finding]) -> Dict[str, int]:
    """
    Count findings grouped by severity.
    """

    counts = {
        "critical": 0,
        "high": 0,
        "medium": 0,
        "low": 0,
    }

    for finding in findings:
        severity = finding.get("severity", "low").lower()

        if severity in counts:
            counts[severity] += 1

    return counts


def should_block_pr(overall_risk: str) -> bool:
    """
    Decide whether the PR should be blocked.

    For our basic version:
    - critical blocks PR
    - high blocks PR
    - medium and low only warn
    """

    return overall_risk in {"critical", "high"}


def build_json_report(
    findings: List[Finding],
    old_file: str,
    new_file: str,
) -> Dict[str, Any]:
    """
    Build a machine-readable JSON report.
    """

    overall_risk = calculate_overall_risk(findings)
    severity_counts = count_findings_by_severity(findings)
    block_pr = should_block_pr(overall_risk)

    return {
        "report_type": "yaml_regression_report",
        "old_file": old_file,
        "new_file": new_file,
        "overall_risk": overall_risk,
        "block_pr": block_pr,
        "summary": {
            "total_findings": len(findings),
            "severity_counts": severity_counts,
        },
        "findings": findings,
    }


def build_markdown_report(report: Dict[str, Any]) -> str:
    """
    Build a human-readable Markdown report from JSON report data.
    """

    overall_risk = report["overall_risk"]
    block_pr = report["block_pr"]
    total_findings = report["summary"]["total_findings"]
    severity_counts = report["summary"]["severity_counts"]
    findings = report["findings"]

    lines = []

    lines.append("# YAML Regression Report")
    lines.append("")
    lines.append("## Files Compared")
    lines.append("")
    lines.append(f"- Old file: `{report['old_file']}`")
    lines.append(f"- New file: `{report['new_file']}`")
    lines.append("")
    lines.append("## Overall Risk")
    lines.append("")
    lines.append(f"**{overall_risk.upper()}**")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- Total findings: **{total_findings}**")
    lines.append(f"- Critical: **{severity_counts['critical']}**")
    lines.append(f"- High: **{severity_counts['high']}**")
    lines.append(f"- Medium: **{severity_counts['medium']}**")
    lines.append(f"- Low: **{severity_counts['low']}**")
    lines.append("")
    lines.append("## Decision")
    lines.append("")

    if block_pr:
        lines.append("**PR should be blocked until high-risk findings are fixed.**")
    else:
        lines.append("**PR can proceed, but review the warnings if any.**")

    lines.append("")

    if not findings:
        lines.append("## Findings")
        lines.append("")
        lines.append("No risky YAML regressions were detected.")
        lines.append("")
        return "\n".join(lines)

    for severity in ["critical", "high", "medium", "low"]:
        severity_findings = [
            finding for finding in findings
            if finding.get("severity", "low").lower() == severity
        ]

        if not severity_findings:
            continue

        lines.append(f"## {severity.capitalize()} Findings")
        lines.append("")

        for index, finding in enumerate(severity_findings, start=1):
            lines.append(f"### {index}. {finding.get('rule_id', 'UNKNOWN')}: {finding.get('message', '')}")
            lines.append("")
            lines.append(f"- Category: `{finding.get('category', 'unknown')}`")
            lines.append(f"- Path: `{finding.get('path', 'unknown')}`")
            lines.append(f"- Severity: `{finding.get('severity', 'unknown')}`")
            lines.append(f"- Recommendation: {finding.get('recommendation', 'No recommendation provided.')}")
            lines.append("")

    lines.append("## Recommended Next Steps")
    lines.append("")
    lines.append("1. Review all critical and high findings.")
    lines.append("2. Restore removed safety checks such as tests, branch guards, and PR triggers.")
    lines.append("3. Reduce permissions to least privilege.")
    lines.append("4. Re-run the YAML regression checker after fixing the workflow.")
    lines.append("")

    return "\n".join(lines)


def write_text_file(path: str, content: str) -> None:
    """
    Write text content to a file, creating parent folders if needed.
    """

    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(content, encoding="utf-8")


def write_json_file(path: str, content: Dict[str, Any]) -> None:
    """
    Write JSON content to a file, creating parent folders if needed.
    """

    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(content, indent=2), encoding="utf-8")


def generate_reports(
    findings: List[Finding],
    old_file: str,
    new_file: str,
    markdown_output: str,
    json_output: str,
) -> Dict[str, Any]:
    """
    Generate both Markdown and JSON reports.

    Returns:
        The JSON report dictionary.
    """

    json_report = build_json_report(
        findings=findings,
        old_file=old_file,
        new_file=new_file,
    )

    markdown_report = build_markdown_report(json_report)

    write_text_file(markdown_output, markdown_report)
    write_json_file(json_output, json_report)

    return json_report