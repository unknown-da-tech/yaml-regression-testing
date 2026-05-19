import json

from src.yaml_regression.yaml_loader import load_yaml_file
from src.yaml_regression.diff_engine import diff_yaml_data


old_data = load_yaml_file("examples/github-actions/old.yml")
new_data = load_yaml_file("examples/github-actions/new.yml")

diff = diff_yaml_data(old_data, new_data)

print(json.dumps(diff, indent=2))