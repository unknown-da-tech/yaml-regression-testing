import argparse
import json
import sys

from src.yaml_regression.yaml_loader import YamlLoadError, load_yaml_file
from src.yaml_regression.diff_engine import diff_yaml_data
from src.yaml_regression.rule_engine import run_rules
from src.yaml_regression.report_generator import generate_reports


def build_parser() -> argparse.ArgumentParser:
    """
    Build the command-line argument parser.
    """

    parser = argparse.ArgumentParser(
        description="AI-Powered DevOps YAML Regression Tester"
    )

    parser.add_argument(
        "--old-file",
        required=True,
        help="Path to the old/baseline YAML file.",
    )

    parser.add_argument(
        "--new-file",
        required=True,
        help="Path to the new/changed YAML file.",
    )

    parser.add_argument(
        "--markdown-output",
        default="reports/report.md",
        help="Path where the Markdown report should be written.",
    )

    parser.add_argument(
        "--json-output",
        default="reports/report.json",
        help="Path where the JSON report should be written.",
    )

    parser.add_argument(
        "--print-diff",
        action="store_true",
        help="Print the raw structural diff to the terminal.",
    )

    parser.add_argument(
        "--print-findings",
        action="store_true",
        help="Print rule findings to the terminal.",
    )

    return parser


def run_check(args: argparse.Namespace) -> int:
    """
    Run the full YAML regression check.

    Returns:
        Exit code:
        0 = success / safe
        1 = risky / block PR
        2 = tool error
    """

    try:
        old_data = load_yaml_file(args.old_file)
        new_data = load_yaml_file(args.new_file)
    except YamlLoadError as error:
        print(f"ERROR: {error}")
        return 2

    diff = diff_yaml_data(old_data, new_data)
    findings = run_rules(diff)

    if args.print_diff:
        print("\nStructural Diff:")
        print(json.dumps(diff, indent=2))

    if args.print_findings:
        print("\nRule Findings:")
        print(json.dumps(findings, indent=2))

    report = generate_reports(
        findings=findings,
        old_file=args.old_file,
        new_file=args.new_file,
        markdown_output=args.markdown_output,
        json_output=args.json_output,
    )

    print("")
    print("YAML Regression Check Completed")
    print("--------------------------------")
    print(f"Old file: {args.old_file}")
    print(f"New file: {args.new_file}")
    print(f"Overall risk: {report['overall_risk'].upper()}")
    print(f"Total findings: {report['summary']['total_findings']}")
    print(f"Block PR: {'YES' if report['block_pr'] else 'NO'}")
    print("")
    print(f"Markdown report: {args.markdown_output}")
    print(f"JSON report: {args.json_output}")
    print("")

    if report["block_pr"]:
        return 1

    return 0


def main() -> None:
    """
    CLI entry point.
    """

    parser = build_parser()
    args = parser.parse_args()

    exit_code = run_check(args)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()