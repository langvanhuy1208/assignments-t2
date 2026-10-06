import json
import sys

import rclpy
from rclpy.node import Node

from ur3_llm_control.robot_skills import RobotSkills
from ur3_llm_control.task_validator import TaskValidator


class SkillExecutor(Node):
    def __init__(self, attach_cubes=True):
        super().__init__('skill_executor')
        self.skills = RobotSkills(attach_cubes=attach_cubes)
        self.validator = TaskValidator()

    def execute_plan(self, plan):
        ok, message = self.validator.validate(plan)
        if not ok:
            print(f"INVALID PLAN: {message}")
            return {"status": "INVALID_PLAN", "message": message}

        results = []
        for step in plan["plan"]:
            skill = step["skill"]
            if skill == "home":
                status = self.skills.home()
                results.append({"skill": "home", "status": status})
                print(f"home() ................. {status}")

            elif skill == "pick":
                obj = step["object"]
                status = self.skills.pick(obj)
                results.append({"skill": "pick", "object": obj, "status": status})
                print(f"pick({obj}) ............ {status}")

            elif skill == "place":
                obj = step["object"]
                zone = step["zone"]
                status = self.skills.place(obj, zone)
                results.append({"skill": "place", "object": obj, "zone": zone, "status": status})
                print(f"place({obj}, {zone}) ... {status}")

            # Dung ngay khi co buoc that bai, khong chay tiep cac buoc sau
            if results[-1]["status"] != "SUCCESS":
                print("STOP: step failed, remaining steps skipped")
                break

        if results and all(item["status"] == "SUCCESS" for item in results):
            print("TASK SUCCESS")
            return {"status": "SUCCESS", "results": results}

        print("TASK FAILED")
        return {"status": "FAILED", "results": results}


def main(args=None):
    if len(sys.argv) != 2:
        print('Usage: ros2 run ur3_llm_control skill_executor \'{"plan":[{"skill":"pick","object":"red_cube"},{"skill":"place","object":"red_cube","zone":"zone_b"},{"skill":"home"}]}\'')
        return

    try:
        plan = json.loads(sys.argv[1])
    except json.JSONDecodeError as exc:
        print(f"Invalid JSON plan: {exc}")
        return

    rclpy.init(args=args)
    node = SkillExecutor()
    result = node.execute_plan(plan)
    node.destroy_node()
    rclpy.shutdown()
    return result


if __name__ == '__main__':
    main()
