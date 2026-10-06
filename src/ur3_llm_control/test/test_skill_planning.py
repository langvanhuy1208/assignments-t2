import json

from ur3_llm_control.student_config import OBJECT_TO_ZONE, ZONE_ASSIGNMENT
from ur3_llm_control.task_validator import TaskValidator
from ur3_llm_control.llm_planner import LLMPlanner


def test_student_zone_mapping():
    assert ZONE_ASSIGNMENT == {
        "zone_a": "yellow_cube",
        "zone_b": "blue_cube",
        "zone_c": "red_cube",
    }
    assert OBJECT_TO_ZONE["yellow_cube"] == "zone_a"
    assert OBJECT_TO_ZONE["blue_cube"] == "zone_b"
    assert OBJECT_TO_ZONE["red_cube"] == "zone_c"


def test_validator_accepts_valid_plan():
    plan = {
        "plan": [
            {"skill": "pick", "object": "red_cube"},
            {"skill": "place", "object": "red_cube", "zone": "zone_c"},
            {"skill": "home"},
        ]
    }
    ok, msg = TaskValidator().validate(plan)
    assert ok is True
    assert msg == "VALID"


def test_validator_rejects_invalid_skill():
    plan = {"plan": [{"skill": "move_joint", "joints": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]}]}
    ok, msg = TaskValidator().validate(plan)
    assert ok is False
    assert "Invalid skill" in msg


def test_planner_generates_plan_for_basic_command():
    planner = LLMPlanner()
    plan = planner.plan_from_text("Put the red cube in zone B.")
    assert plan["plan"][0]["skill"] == "pick"
    assert plan["plan"][0]["object"] == "red_cube"
    assert plan["plan"][1]["skill"] == "place"
    assert plan["plan"][1]["zone"] == "zone_b"
    assert plan["plan"][2]["skill"] == "home"
