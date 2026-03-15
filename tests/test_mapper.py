from src.decision_mapper import map_issue_to_action

def test_map_issue_crash():
    assert map_issue_to_action("App crashed", "container_crash") == "restart"

def test_map_issue_oom():
    assert map_issue_to_action("System slow", "OOMKilled") == "restart"

def test_map_issue_dependency():
    assert map_issue_to_action("Cannot reach DB", "dependency_failure") == "restart_dependency"

def test_map_issue_unknown():
    assert map_issue_to_action("Unknown", "Unknown Error") == "restart"
