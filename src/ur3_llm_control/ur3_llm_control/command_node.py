import sys
import json
import re

import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient

from moveit_msgs.action import MoveGroup
from moveit_msgs.msg import Constraints, JointConstraint


# ============================================================
# Mapping ten vat
# ============================================================

OBJECT_ALIASES = {
    'vang': 'yellow_cube',
    'khoi vang': 'yellow_cube',
    'yellow': 'yellow_cube',
    'yellow cube': 'yellow_cube',
    'yellow_cube': 'yellow_cube',

    'do': 'red_cube',
    'khoi do': 'red_cube',
    'red': 'red_cube',
    'red cube': 'red_cube',
    'red_cube': 'red_cube',

    'xanh': 'blue_cube',
    'khoi xanh': 'blue_cube',
    'blue': 'blue_cube',
    'blue cube': 'blue_cube',
    'blue_cube': 'blue_cube',
}


# ============================================================
# Mapping ten zone
# ============================================================

ZONE_ALIASES = {
    'a': 'zone_a',
    'zone a': 'zone_a',
    'zone_a': 'zone_a',

    'b': 'zone_b',
    'zone b': 'zone_b',
    'zone_b': 'zone_b',

    'c': 'zone_c',
    'zone c': 'zone_c',
    'zone_c': 'zone_c',
}


# ============================================================
# Parse natural language
# ============================================================

def parse_natural_language(text):

    text = text.lower().strip()

    # --------------------------------------------------------
    # Tim object
    # --------------------------------------------------------

    object_name = None

    # Sap xep dai -> ngan de tranh match sai
    object_patterns = sorted(
        OBJECT_ALIASES.keys(),
        key=len,
        reverse=True
    )

    for pattern in object_patterns:

        if pattern in text:

            object_name = OBJECT_ALIASES[pattern]
            break

    if object_name is None:

        return {
            'success': False,
            'error': 'Khong xac dinh duoc vat can gap.'
        }

    # --------------------------------------------------------
    # Tim zone
    # --------------------------------------------------------

    zone_name = None

    zone_patterns = sorted(
        ZONE_ALIASES.keys(),
        key=len,
        reverse=True
    )

    for pattern in zone_patterns:

        if pattern in text:

            zone_name = ZONE_ALIASES[pattern]
            break

    if zone_name is None:

        return {
            'success': False,
            'error': 'Khong xac dinh duoc zone.'
        }

    # --------------------------------------------------------
    # Tao skill plan
    # --------------------------------------------------------

    plan = {
        'skills': [
            {
                'name': 'pick',
                'object': object_name
            },
            {
                'name': 'place',
                'object': object_name,
                'zone': zone_name
            }
        ]
    }

    return {
        'success': True,
        'plan': plan
    }


# ============================================================
# Command Node
# ============================================================

class CommandNode(Node):

    def __init__(self):

        super().__init__('command_node')

        self.action_client = ActionClient(
            self,
            MoveGroup,
            '/move_action'
        )

    # ========================================================
    # Execute JSON move_joint
    # ========================================================

    def execute_command(self, command):

        action = command.get('action')

        if action != 'move_joint':

            self.get_logger().error(
                f'Action khong hop le: {action}'
            )

            return

        joints = command.get('joints')

        if joints is None:

            self.get_logger().error(
                'Thieu truong joints'
            )

            return

        if len(joints) != 6:

            self.get_logger().error(
                'UR3 can dung 6 gia tri joint'
            )

            return

        try:

            joints = [
                float(value)
                for value in joints
            ]

        except (TypeError, ValueError):

            self.get_logger().error(
                'Gia tri joints phai la so'
            )

            return

        self.get_logger().info(
            f'Nhan command: {command}'
        )

        self.get_logger().info(
            'Waiting for MoveIt...'
        )

        if not self.action_client.wait_for_server(
            timeout_sec=10.0
        ):

            self.get_logger().error(
                'Khong tim thay /move_action'
            )

            return

        goal_msg = MoveGroup.Goal()

        goal_msg.request.group_name = (
            'ur_manipulator'
        )

        goal_msg.request.allowed_planning_time = 5.0
        goal_msg.request.num_planning_attempts = 5

        goal_msg.request.max_velocity_scaling_factor = 0.3
        goal_msg.request.max_acceleration_scaling_factor = 0.3

        joint_names = [
            'shoulder_pan_joint',
            'shoulder_lift_joint',
            'elbow_joint',
            'wrist_1_joint',
            'wrist_2_joint',
            'wrist_3_joint'
        ]

        constraints = Constraints()

        for name, position in zip(
            joint_names,
            joints
        ):

            jc = JointConstraint()

            jc.joint_name = name
            jc.position = position

            jc.tolerance_above = 0.01
            jc.tolerance_below = 0.01
            jc.weight = 1.0

            constraints.joint_constraints.append(jc)

        goal_msg.request.goal_constraints.append(
            constraints
        )

        goal_msg.planning_options.plan_only = False
        goal_msg.planning_options.look_around = False
        goal_msg.planning_options.replan = True
        goal_msg.planning_options.replan_attempts = 2

        self.get_logger().info(
            'Sending command to MoveIt...'
        )

        future = self.action_client.send_goal_async(
            goal_msg
        )

        future.add_done_callback(
            self.goal_response_callback
        )

    # ========================================================
    # MoveIt callbacks
    # ========================================================

    def goal_response_callback(self, future):

        goal_handle = future.result()

        if not goal_handle.accepted:

            self.get_logger().error(
                'MoveIt tu choi goal'
            )

            rclpy.shutdown()

            return

        self.get_logger().info(
            'Goal accepted.'
        )

        result_future = goal_handle.get_result_async()

        result_future.add_done_callback(
            self.result_callback
        )

    def result_callback(self, future):

        result = future.result().result

        error_code = result.error_code.val

        self.get_logger().info(
            f'MoveIt error_code = {error_code}'
        )

        if error_code == 1:

            self.get_logger().info(
                'Command thuc hien thanh cong!'
            )

        else:

            self.get_logger().error(
                f'Command that bai: error_code = '
                f'{error_code}'
            )

        rclpy.shutdown()


# ============================================================
# Main
# ============================================================

def main(args=None):

    if len(sys.argv) != 2:

        print(
            'Usage:'
        )

        print(
            'JSON: ros2 run ur3_llm_control '
            'command_node \'{"action":"move_joint",'
            '"joints":[...] }\''
        )

        print(
            'Natural language:'
        )

        print(
            'ros2 run ur3_llm_control command_node '
            '"gap khoi vang vao zone A"'
        )

        return

    user_input = sys.argv[1].strip()

    # ========================================================
    # 1. Thu parse JSON truoc
    # ========================================================

    try:

        command = json.loads(user_input)

        rclpy.init(args=args)

        node = CommandNode()

        node.execute_command(command)

        rclpy.spin(node)

        return

    except json.JSONDecodeError:

        pass

    # ========================================================
    # 2. Neu khong phai JSON -> parse natural language
    # ========================================================

    result = parse_natural_language(user_input)

    if not result['success']:

        print(
            f"LOI: {result['error']}"
        )

        return

    plan = result['plan']

    print(
        'Plan da tao:'
    )

    print(
        json.dumps(
            plan,
            indent=2,
            ensure_ascii=False
        )
    )

    print()

    print(
        'Nhan dang natural language thanh cong.'
    )


if __name__ == '__main__':
    main()
