from src.yaml_regression.yaml_loader import load_yaml_file

old_data = load_yaml_file("examples/github-actions/old.yml")
new_data = load_yaml_file("examples/github-actions/new.yml")

print("OLD YAML:")
print(old_data)

print("\nNEW YAML:")
print(new_data)

print("\nOld workflow name:")
print(old_data["name"])

print("\nOld workflow triggers:")
print(old_data["on"])

print("\nNew workflow triggers:")
print(new_data["on"])