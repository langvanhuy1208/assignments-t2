# UR3 LLM Skill-based Control

This package implements a simple skill-based robot planning system for UR3/UR3e in ROS 2.

## Student
- Name: Lang Van Huy
- Student ID: 23020745

## Student-specific mapping
- 45 mod 6 = 3
- Zone A = Yellow
- Zone B = Blue
- Zone C = Red

Therefore:
- yellow_cube -> zone_a
- blue_cube -> zone_b
- red_cube -> zone_c
## Architecture

User Command
  -> LLM Planner
  -> JSON Plan
  -> Validator
  -> Skill Executor
  -> MoveIt 2
  -> UR3/UR3e

LLM only picks skills and object/zone names. It does not generate robot joint commands directly.

## Node roles
- `llm_node`: receives natural language command and converts it to a skill plan
- `skill_executor`: validates and executes each skill in sequence
- `robot_skills`: provides `home()`, `pick(object)`, and `place(object, zone)`

## Example

```bash
ros2 run ur3_llm_control llm_node "Put the red cube in zone B."
```

Expected plan:

```json
{
  "plan": [
    {"skill": "pick", "object": "red_cube"},
    {"skill": "place", "object": "red_cube", "zone": "zone_b"},
    {"skill": "home"}
  ]
}
```

## Build

```bash
cd ~/ur3_llm_ws
colcon build --packages-select ur3_llm_control
source install/setup.bash
```

## Run

```bash
ros2 run ur3_llm_control llm_node "Put the red cube in zone B."
ros2 run ur3_llm_control skill_executor '{"plan":[{"skill":"pick","object":"red_cube"},{"skill":"place","object":"red_cube","zone":"zone_b"},{"skill":"home"}]}'
```

## Notes
- If the 9Router endpoint is not configured, the planner falls back to keyword-based planning rules.
- The package is designed to match the assignment requirements while remaining executable in a typical ROS 2 + MoveIt environment.
