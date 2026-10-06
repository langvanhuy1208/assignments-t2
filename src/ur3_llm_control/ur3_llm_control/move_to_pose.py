import sys

import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient

from moveit_msgs.action import MoveGroup
from moveit_msgs.msg import Constraints, PositionConstraint
from shape_msgs.msg import SolidPrimitive
from geometry_msgs.msg import Pose


class MoveToPose(Node):

    def __init__(self):
        super().__init__('move_to_pose')

        self.client = ActionClient(
            self,
            MoveGroup,
            '/move_action'
        )

    def move_to_pose(self, x, y, z):

        self.get_logger().info('Waiting for MoveIt...')

        if not self.client.wait_for_server(timeout_sec=10.0):
            self.get_logger().error(
                'MoveIt action server not available!'
            )
            return False

        goal = MoveGroup.Goal()

        goal.request.group_name = 'ur_manipulator'

        goal.request.allowed_planning_time = 10.0
        goal.request.num_planning_attempts = 10

        goal.request.max_velocity_scaling_factor = 0.2
        goal.request.max_acceleration_scaling_factor = 0.2

        goal.request.start_state.is_diff = True

        # ==========================================
        # POSITION CONSTRAINT
        # ==========================================

        position_constraint = PositionConstraint()

        position_constraint.header.frame_id = 'base_link'
        position_constraint.link_name = 'tool0'

        position_constraint.target_point_offset.x = 0.0
        position_constraint.target_point_offset.y = 0.0
        position_constraint.target_point_offset.z = 0.0

        box = SolidPrimitive()

        box.type = SolidPrimitive.BOX

        # Vung chap nhan quanh target
        box.dimensions = [
            0.05,
            0.05,
            0.05
        ]

        position_constraint.constraint_region.primitives.append(
            box
        )

        target_position = Pose()

        target_position.position.x = x
        target_position.position.y = y
        target_position.position.z = z

        # Quaternion hop le
        target_position.orientation.w = 1.0

        position_constraint.constraint_region.primitive_poses.append(
            target_position
        )

        position_constraint.weight = 1.0

        constraints = Constraints()

        constraints.position_constraints.append(
            position_constraint
        )

        goal.request.goal_constraints.append(
            constraints
        )

        self.get_logger().info(
            f'Target base_link position: '
            f'x={x:.3f}, y={y:.3f}, z={z:.3f}'
        )

        future = self.client.send_goal_async(goal)

        rclpy.spin_until_future_complete(
            self,
            future
        )

        goal_handle = future.result()

        if not goal_handle.accepted:

            self.get_logger().error(
                'Goal rejected!'
            )

            return False

        self.get_logger().info(
            'Goal accepted. Waiting for result...'
        )

        result_future = goal_handle.get_result_async()

        rclpy.spin_until_future_complete(
            self,
            result_future
        )

        result = result_future.result().result

        error_code = result.error_code.val

        self.get_logger().info(
            f'MoveIt error code: {error_code}'
        )

        if error_code == 1:

            self.get_logger().info(
                'Robot moved to target pose successfully!'
            )

            return True

        self.get_logger().error(
            'Robot failed to move to target pose!'
        )

        return False


def main(args=None):

    if len(sys.argv) != 4:

        print(
            'Usage: ros2 run ur3_llm_control '
            'move_to_pose x y z'
        )

        return

    try:

        x = float(sys.argv[1])
        y = float(sys.argv[2])
        z = float(sys.argv[3])

    except ValueError:

        print(
            'Loi: x y z phai la so.'
        )

        return

    rclpy.init(args=args)

    node = MoveToPose()

    success = node.move_to_pose(
        x,
        y,
        z
    )

    if success:

        node.get_logger().info(
            'MOVE TO POSE SUCCESS'
        )

    else:

        node.get_logger().error(
            'MOVE TO POSE FAILED'
        )

    node.destroy_node()

    rclpy.shutdown()


if __name__ == '__main__':
    main()
