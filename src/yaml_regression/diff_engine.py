"""
Result of this will be input for
Rule Engine
AI Reviewer
Report Generator

expected output:

{
  "added": [
    "permissions.actions"
  ],
  "removed": [
    "on.pull_request",
    "jobs.deploy.if",
    "jobs.test.steps[2]"
  ],
  "changed": [
    {
      "path": "on.push.branches[0]",
      "old": "main",
      "new": "develop"
    },
    {
      "path": "permissions.contents",
      "old": "read",
      "new": "write"
    }
  ]
}
"""

from typing import Any, Dict, List


DiffResult = Dict[str, List[Dict[str, Any]]]


def join_path(parent_path: str, key: Any) -> str:
    """
    Build a readable path for dictionary keys.
    Example:
        parent_path='jobs.deploy', key='if'
        result='jobs.deploy.if'
    """

    key_text = str(key)

    if parent_path:
        return f"{parent_path}.{key_text}"

    return key_text


def list_path(parent_path: str, index: int) -> str:
    """
    Build a readable path for list indexes.
    Example:
        parent_path='on.push.branches', index=0
        result='on.push.branches[0]'
    """

    return f"{parent_path}[{index}]"


def create_empty_diff() -> DiffResult:
    """
    Create an empty diff structure.
    """

    return {
        "added": [],
        "removed": [],
        "changed": []
    }


def compare_values(old: Any, new: Any, path: str = "") -> DiffResult:
    """
    Recursively compare two Python values.

    The values can be:
    - dictionaries
    - lists
    - strings
    - numbers
    - booleans

    Returns:
        A structured diff with added, removed, and changed entries.
    """

    diff = create_empty_diff()

    if isinstance(old, dict) and isinstance(new, dict):
        old_keys = set(old.keys())
        new_keys = set(new.keys())

        for key in sorted(old_keys - new_keys):
            diff["removed"].append({
                "path": join_path(path, key),
                "old": old[key]
            })

        for key in sorted(new_keys - old_keys):
            diff["added"].append({
                "path": join_path(path, key),
                "value": new[key]
            })

        for key in sorted(old_keys & new_keys):
            child_path = join_path(path, key)
            child_diff = compare_values(old[key], new[key], child_path)

            diff["added"].extend(child_diff["added"])
            diff["removed"].extend(child_diff["removed"])
            diff["changed"].extend(child_diff["changed"])

        return diff

    if isinstance(old, list) and isinstance(new, list):
        max_length = max(len(old), len(new))

        for index in range(max_length):
            child_path = list_path(path, index)

            if index >= len(old):
                diff["added"].append({
                    "path": child_path,
                    "value": new[index]
                })
            elif index >= len(new):
                diff["removed"].append({
                    "path": child_path,
                    "old": old[index]
                })
            else:
                child_diff = compare_values(old[index], new[index], child_path)

                diff["added"].extend(child_diff["added"])
                diff["removed"].extend(child_diff["removed"])
                diff["changed"].extend(child_diff["changed"])

        return diff

    if old != new:
        diff["changed"].append({
            "path": path,
            "old": old,
            "new": new
        })

    return diff


def diff_yaml_data(old_data: Dict[str, Any], new_data: Dict[str, Any]) -> DiffResult:
    """
    Compare two parsed YAML dictionaries.

    Args:
        old_data: Parsed old YAML data.
        new_data: Parsed new YAML data.

    Returns:
        Structured diff result.
    """

    return compare_values(old_data, new_data)