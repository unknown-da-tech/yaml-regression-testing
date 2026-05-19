import json

from src.yaml_regression.yaml_loader import load_yaml_file
from src.yaml_regression.diff_engine import diff_yaml_data
from src.yaml_regression.rule_engine import run_rules
from src.yaml_regression.report_generator import generate_reports


old_file = "examples/github-actions/old.yml"
new_file = "examples/github-actions/new.yml"

old_data = load_yaml_file(old_file)
new_data = load_yaml_file(new_file)

diff = diff_yaml_data(old_data, new_data)
findings = run_rules(diff)

report = generate_reports(
    findings=findings,
    old_file=old_file,
    new_file=new_file,
    markdown_output="reports/report.md",
    json_output="reports/report.json",
)

print(json.dumps(report, indent=2))