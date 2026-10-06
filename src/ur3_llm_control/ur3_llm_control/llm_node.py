import json
import os
import sys

import rclpy
from rclpy.node import Node

from ur3_llm_control.llm_planner import LLMPlanner
from ur3_llm_control.task_validator import TaskValidator
from ur3_llm_control.skill_executor import SkillExecutor


class LLMNode(Node):
    def __init__(self):
        super().__init__('llm_node')
        self.planner = LLMPlanner()
        self.validator = TaskValidator()

    def execute(self, user_text):
        self.get_logger().info(f"USER COMMAND: {user_text}")

        plan = self.planner.plan_from_text(user_text)
        self.get_logger().info(f"LLM PLAN: {json.dumps(plan, ensure_ascii=False, indent=2)}")

        ok, message = self.validator.validate(plan)
        if not ok:
            self.get_logger().error(f"VALIDATION FAILED: {message}")
            return False

        executor = SkillExecutor()
        result = executor.execute_plan(plan)
        self.get_logger().info(f"EXECUTION RESULT: {json.dumps(result, ensure_ascii=False, indent=2)}")
        return result


def main(args=None):
    if len(sys.argv) != 2:
        print('Usage: ros2 run ur3_llm_control llm_node "Put the red cube in zone B."')
        return

    rclpy.init(args=args)
    node = LLMNode()
    result = node.execute(sys.argv[1])
    node.destroy_node()
    rclpy.shutdown()
    return result


if __name__ == '__main__':
    main()
