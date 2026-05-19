from pathlib import Path
from typing import Any, Dict

import yaml

class YamlLoadError(Exception):
    """Raised when a YAML file cannot be loaded safely."""


def normalize_github_actions_keys(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    PyYAML can parse the GitHub Actions key 'on' as boolean True.
    This function converts True back to 'on' when needed.
    """

    if True in data and "on" not in data:
        data["on"] = data.pop(True)
    return data

def load_yaml_file(path: str) -> Dict[str, Any]:
    """
    Load a YAML file and return it as a Python dictionary.

    Args:
        path: Path to the YAML file.

    Returns:
        Parsed YAML content as a dictionary.

    Raises:
        YamlLoadError: If file is missing, invalid, empty, or not a dictionary.
    """
    file_path = Path(path)

    if not file_path.exists():
        raise YamlLoadError(f"YAML file not found: {path}")
    try:
        with file_path.open("r", encoding="utf-8") as file:
            data = yaml.safe_load(file)
    except yaml.YAMLError as error:
        raise YamlLoadError(f"Invalid YAML in {path}: {error}") from error
    
    if data is None:
        raise YamlLoadError(f"YAML file is empty: {path}")
    
    if not isinstance(data, dict):
        raise YamlLoadError(f"YAML root must be an object/dictionary: {path}")
    
    data = normalize_github_actions_keys(data)

    return data
