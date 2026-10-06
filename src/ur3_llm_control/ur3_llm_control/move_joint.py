import sys

import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient

from moveit_msgs.action import MoveGroup
from moveit_msgs.msg import Constraints, JointConstraint


class MoveJoint(Node):

    def __init__(self):
        super().__init__('move_joint')

        self.action_client = ActionClient(
            self,
            MoveGroup,
            '/move_action'
        )

    def send_goal(self, joint_positions):

        self.get_logger().info('Waiting for MoveIt...')

        if not self.action_client.wait_for_server(timeout_sec=10.0):
            self.get_logger().error(
                'Khong tim thay /move_action'
            )
            return

        goal_msg = MoveGroup.Goal()

        # MoveIt planning group
        goal_msg.request.group_name = 'ur_manipulator'

        # Planning parameters
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

        for name, position in zip(joint_names, joint_positions):

            joint_constraint = JointConstraint()

            joint_constraint.joint_name = name
            joint_constraint.position = position

            joint_constraint.tolerance_above = 0.01
            joint_constraint.tolerance_below = 0.01
            joint_constraint.weight = 1.0

            constraints.joint_constraints.append(
                joint_constraint
            )

        goal_msg.request.goal_constraints.append(
            constraints
        )

        # Plan + Execute
        goal_msg.planning_options.plan_only = False
        goal_msg.planning_options.look_around = False
        goal_msg.planning_options.replan = True
        goal_msg.planning_options.replan_attempts = 2

        self.get_logger().info(
            'Sending joint goal to MoveIt...'
        )

        self.get_logger().info(
            f'Joints: {joint_positions}'
        )

        future = self.action_client.send_goal_async(
            goal_msg
        )

        future.add_done_callback(
            self.goal_response_callback
        )

    def goal_response_callback(self, future):

        goal_handle = future.result()

        if not goal_handle.accepted:

            self.get_logger().error(
                'MoveIt tu choi goal'
            )

            rclpy.shutdown()
            return

        self.get_logger().info(
            'Goal accepted. Waiting for result...'
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
                'Move Joint thanh cong!'
            )

        else:

            self.get_logger().error(
                f'Move Joint that bai. '
                f'error_code = {error_code}'
            )

        rclpy.shutdown()


def main(args=None):

    if len(sys.argv) != 7:

        print(
            'Usage: ros2 run ur3_llm_control move_joint '
            'j1 j2 j3 j4 j5 j6'
        )

        return

    try:

        joint_positions = [
            float(value)
            for value in sys.argv[1:7]
        ]

    except ValueError:

        print(
            'Loi: 6 gia tri joint phai la so.'
        )

        return

    rclpy.init(args=args)

    node = MoveJoint()

    node.send_goal(joint_positions)

    rclpy.spin(node)


if __name__ == '__main__':
    main()
