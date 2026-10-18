from pathlib import Path

import yaml


def test_openapi_contract_paths_fields_and_responses():
    contract_path = Path(__file__).resolve().parents[2] / "specs" / "001-agentic-todo-app" / "contracts" / "openapi.yaml"
    contract = yaml.safe_load(contract_path.read_text(encoding="utf-8"))

    assert contract["openapi"] == "3.1.0"
    paths = contract["paths"]
    assert {"get", "post"} <= paths["/api/tasks"].keys()
    assert {"get", "patch", "delete"} <= paths["/api/tasks/{task_id}"].keys()
    assert "/api/assistant" in paths
    assert "/api/plan/next" in paths
    assert "/api/summary" in paths
    task_schema = contract["components"]["schemas"]["Task"]["properties"]
    assert task_schema["priority"]["enum"] == ["high", "normal", "low"]
    assert task_schema["due_date"]["format"] == "date"
    assert paths["/api/tasks"]["post"]["responses"]["201"]
    assert paths["/api/tasks/{task_id}"]["delete"]["responses"]["204"]
