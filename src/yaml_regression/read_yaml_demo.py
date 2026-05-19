from pathlib import Path
import yaml

BASE_DIR = Path(__file__).resolve().parents[2]
file_path = BASE_DIR / "examples" / "github-actions" / "old.yml"

with file_path.open("r", encoding="utf-8") as file:
    data = yaml.safe_load(file)

print(data)