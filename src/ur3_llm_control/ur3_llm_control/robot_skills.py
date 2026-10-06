import shutil
import subprocess
import threading
import time

import rclpy
import rclpy.time

from rclpy.node import Node
from rclpy.action import ActionClient

from tf2_ros import Buffer, TransformListener, TransformException

from moveit_msgs.action import MoveGroup, ExecuteTrajectory
from moveit_msgs.srv import GetCartesianPath
from moveit_msgs.msg import (
    Constraints,
    PositionConstraint,
    OrientationConstraint,
    JointConstraint,
)
from shape_msgs.msg import SolidPrimitive
from geometry_msgs.msg import Pose
from builtin_interfaces.msg import Duration


class RobotSkills(Node):

    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    INVALID_OBJECT = "INVALID_OBJECT"
    INVALID_ZONE = "INVALID_ZONE"
    PLANNING_FAILED = "PLANNING_FAILED"
    ZONE_OCCUPIED = "ZONE_OCCUPIED"

    # ==========================================================
    # HOME
    # ==========================================================

    HOME = [0.0, -1.5708, 1.5708, -1.5708, -1.5708, 0.0]

    # ==========================================================
    # TOA DO (he base_link)   base_link = world - (0, -0.20, 0.55)
    # Phai khop worlds/llm_scene.sdf
    # ==========================================================

    BASE_IN_WORLD = (0.0, -0.20, 0.55)

    OBJECT_POSITIONS = {
        "red_cube": [-0.10, 0.35, 0.05],
        "yellow_cube": [0.00, 0.35, 0.05],
        "blue_cube": [0.10, 0.35, 0.05],
    }

    ZONE_POSITIONS = {
        "zone_a": [-0.40, 0.35, 0.01],
        "zone_b": [-0.40, 0.15, 0.01],
        "zone_c": [-0.40, -0.05, 0.01],
    }

    # ==========================================================
    # DO CAO (base_link)
    # SAFE_Z = 0.20: zone_a cach base 0.53 m, tool huong xuong thi
    # z = 0.25 khong voi toi (da kiem tra IK).
    # GRIP_Z/PLACE_Z = 0.085: mat bich tool0 cach dinh cube 5 mm.
    # ==========================================================

    SAFE_Z = 0.20
    APPROACH_Z = 0.15
    GRIP_Z = 0.09     # mat bich tool0 cach dinh cube 1 cm (tranh cham cube)
    PLACE_Z = 0.09

    # ==========================================================
    # GAZEBO SIM (Ignition) - gia lap gap/tha bang service set_pose
    # ==========================================================

    WORLD_NAME = "llm_scene"
    CUBE_HALF = 0.04
    CARRY_OFFSET = 0.05           # tam cube thap hon tool0 (khop GRIP_Z)
    TABLE_TOP_WORLD_Z = 0.55

    POSITION_TOLERANCE = 0.01
    ORIENT_TOLERANCE = 0.08       # ~4.6 do: gioi han do nghieng cua tool

    GOAL_ACCEPT_TIMEOUT = 15.0    # giay cho MoveIt nhan goal
    RESULT_TIMEOUT = 90.0         # giay cho mot chuyen dong hoan tat
    CART_SLOWDOWN = 5.0           # lam cham duong thang dung (x lan)

    RETRY_CODES = (-1, -2, -3, -4, -6, 99999)
    MAX_ATTEMPTS = 3
    SETTLE_SEC = 0.7

    JOINT_NAMES = [
        "shoulder_pan_joint",
        "shoulder_lift_joint",
        "elbow_joint",
        "wrist_1_joint",
        "wrist_2_joint",
        "wrist_3_joint",
    ]

    def __init__(self, attach_cubes=True):
        super().__init__("robot_skills")

        # attach_cubes=False: robot van di chuyen day du nhung cube khong
        # bam theo tool (dung de thu chuyen dong)
        self.attach_cubes = attach_cubes

        self.held_object = None
        self.object_positions = {
            k: list(v) for k, v in self.OBJECT_POSITIONS.items()
        }
        self.cube_zone = {}       # cube -> zone dang nam
        self.zone_occupant = {}   # zone -> cube dang nam

        self.move_action_client = ActionClient(self, MoveGroup, "/move_action")
        self.execute_client = ActionClient(
            self, ExecuteTrajectory, "/execute_trajectory"
        )
        self.cartesian_client = self.create_client(
            GetCartesianPath, "/compute_cartesian_path"
        )

        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(
            self.tf_buffer, self, spin_thread=True
        )

        self._gz_exe, self._gz_prefix = self._detect_gz()
        self._gz_lock = threading.Lock()
        self._stop = threading.Event()
        self._follow_thread = threading.Thread(
            target=self._follow_loop, daemon=True
        )
        self._follow_thread.start()

    def destroy_node(self):
        self._stop.set()
        return super().destroy_node()

    # ==========================================================
    # GAZEBO SIM: set_pose qua lenh `ign service` (hoac `gz service`)
    # ==========================================================

    @staticmethod
    def _detect_gz():
        for exe, prefix in (("ign", "ignition"), ("gz", "gz")):
            if shutil.which(exe):
                return exe, prefix
        return None, None

    def _gazebo_ready(self):
        if self._gz_exe is None:
            self.get_logger().error(
                "Khong tim thay lenh 'ign' hoac 'gz'. Hay source moi truong Gazebo."
            )
            return False

        service = f"/world/{self.WORLD_NAME}/set_pose"
        try:
            out = subprocess.run(
                [self._gz_exe, "service", "-l"],
                capture_output=True, text=True, timeout=10,
            ).stdout
        except (subprocess.TimeoutExpired, OSError):
            out = ""

        if service not in out:
            self.get_logger().error(
                f"Service {service} khong ton tai. Gazebo dang mo world nao? "
                f"(world phai ten '{self.WORLD_NAME}', file llm_scene.sdf)"
            )
            return False
        return True

    def _gz_set_pose(self, name, x, y, z):
        if self._gz_exe is None:
            return False

        req = (
            f'name: "{name}", '
            f"position: {{x: {x:.4f}, y: {y:.4f}, z: {z:.4f}}}, "
            "orientation: {x: 0, y: 0, z: 0, w: 1}"
        )
        cmd = [
            self._gz_exe, "service",
            "-s", f"/world/{self.WORLD_NAME}/set_pose",
            "--reqtype", f"{self._gz_prefix}.msgs.Pose",
            "--reptype", f"{self._gz_prefix}.msgs.Boolean",
            "--timeout", "2000",
            "--req", req,
        ]
        try:
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=6)
        except (subprocess.TimeoutExpired, OSError):
            return False
        return res.returncode == 0 and "true" in res.stdout.lower()

    def _tool0_in_world(self):
        try:
            tf = self.tf_buffer.lookup_transform(
                "world", "tool0", rclpy.time.Time()
            )
        except TransformException:
            return None
        t = tf.transform.translation
        return t.x, t.y, t.z

    def _snap_to_tool(self, name):
        """Dat cube ngay duoi tool0 (goi lien tuc khi dang cam cube)."""
        pos = self._tool0_in_world()
        if pos is None:
            time.sleep(0.05)
            return False
        with self._gz_lock:
            if self.held_object != name:
                return False
            return self._gz_set_pose(
                name, pos[0], pos[1], pos[2] - self.CARRY_OFFSET
            )

    def _follow_loop(self):
        while not self._stop.is_set():
            name = self.held_object
            if name is None or not self.attach_cubes:
                time.sleep(0.05)
                continue
            self._snap_to_tool(name)

    # ==========================================================
    # MOVEIT
    # ==========================================================

    def _wait(self, future, timeout):
        rclpy.spin_until_future_complete(self, future, timeout_sec=timeout)
        return future.done()

    def _send_goal(self, constraints):
        if not self.move_action_client.wait_for_server(timeout_sec=10.0):
            self.get_logger().error("MoveIt action /move_action is not available")
            return False

        for attempt in range(1, self.MAX_ATTEMPTS + 1):
            time.sleep(self.SETTLE_SEC)   # cho robot dung han

            goal = MoveGroup.Goal()
            goal.request.group_name = "ur_manipulator"
            goal.request.allowed_planning_time = 10.0
            goal.request.num_planning_attempts = 10
            goal.request.max_velocity_scaling_factor = 0.2
            goal.request.max_acceleration_scaling_factor = 0.2
            goal.request.start_state.is_diff = True
            goal.request.goal_constraints.append(constraints)

            future = self.move_action_client.send_goal_async(goal)
            if not self._wait(future, self.GOAL_ACCEPT_TIMEOUT):
                self.get_logger().error(
                    "MoveIt khong phan hoi (move_group dang treo?). "
                    "Neu vua khoi dong lai Gazebo, hay khoi dong lai MoveIt."
                )
                return False

            goal_handle = future.result()
            if goal_handle is None or not goal_handle.accepted:
                self.get_logger().error("MoveIt rejected the goal")
                return False

            result_future = goal_handle.get_result_async()
            if not self._wait(result_future, self.RESULT_TIMEOUT):
                goal_handle.cancel_goal_async()
                self.get_logger().error(
                    "Chuyen dong qua thoi gian cho, da huy goal. "
                    "Kiem tra robot co bi ket/va cham trong Gazebo khong."
                )
                return False

            error_code = result_future.result().result.error_code.val
            self.get_logger().info(f"MoveIt error_code = {error_code}")
            if error_code == 1:
                return True

            if error_code not in self.RETRY_CODES or attempt == self.MAX_ATTEMPTS:
                return False

            self.get_logger().warn(
                f"Attempt {attempt}/{self.MAX_ATTEMPTS} failed "
                f"(error_code={error_code}), retrying..."
            )
        return False

    # ----------------------------------------------------------
    # Duong thang dung (Cartesian): hai/nhac theo phuong thang dung,
    # khong de planner chon duong di vong.
    # ----------------------------------------------------------

    def _tool0_in_base(self):
        try:
            tf = self.tf_buffer.lookup_transform(
                "base_link", "tool0", rclpy.time.Time()
            )
        except TransformException:
            return None
        return tf.transform

    def _slow_down(self, trajectory, factor):
        for point in trajectory.joint_trajectory.points:
            total = (
                point.time_from_start.sec * 1_000_000_000
                + point.time_from_start.nanosec
            ) * factor
            point.time_from_start = Duration(
                sec=int(total // 1_000_000_000),
                nanosec=int(total % 1_000_000_000),
            )
            point.velocities = [v / factor for v in point.velocities]
            point.accelerations = [a / (factor * factor) for a in point.accelerations]

    def _move_cartesian(self, x, y, z):
        tf = self._tool0_in_base()
        if tf is None:
            self.get_logger().warn("Chua co TF tool0 -> dung planner thuong")
            return False

        if not self.cartesian_client.wait_for_service(timeout_sec=3.0):
            self.get_logger().warn("/compute_cartesian_path khong co -> dung planner thuong")
            return False
        if not self.execute_client.wait_for_server(timeout_sec=3.0):
            self.get_logger().warn("/execute_trajectory khong co -> dung planner thuong")
            return False

        time.sleep(self.SETTLE_SEC)

        target = Pose()
        target.position.x = x
        target.position.y = y
        target.position.z = z
        target.orientation = tf.rotation     # giu nguyen huong tool

        req = GetCartesianPath.Request()
        req.header.frame_id = "base_link"
        req.start_state.is_diff = True
        req.group_name = "ur_manipulator"
        req.link_name = "tool0"
        req.waypoints = [target]
        req.max_step = 0.005
        req.jump_threshold = 0.0
        req.avoid_collisions = True

        future = self.cartesian_client.call_async(req)
        if not self._wait(future, 10.0) or future.result() is None:
            self.get_logger().warn("compute_cartesian_path khong phan hoi")
            return False

        res = future.result()
        if res.fraction < 0.99:
            self.get_logger().warn(
                f"Duong thang dung chi dat {res.fraction:.0%} -> dung planner thuong"
            )
            return False

        self._slow_down(res.solution, self.CART_SLOWDOWN)

        goal = ExecuteTrajectory.Goal()
        goal.trajectory = res.solution
        send = self.execute_client.send_goal_async(goal)
        if not self._wait(send, self.GOAL_ACCEPT_TIMEOUT):
            self.get_logger().error("execute_trajectory khong phan hoi")
            return False

        handle = send.result()
        if handle is None or not handle.accepted:
            self.get_logger().error("execute_trajectory bi tu choi")
            return False

        result = handle.get_result_async()
        if not self._wait(result, self.RESULT_TIMEOUT):
            handle.cancel_goal_async()
            self.get_logger().error("execute_trajectory qua thoi gian cho, da huy")
            return False

        code = result.result().result.error_code.val
        self.get_logger().info(f"Cartesian move error_code = {code}")
        return code == 1

    def _move_vertical(self, x, y, z):
        """Di chuyen thang dung; neu khong duoc thi du phong bang planner thuong."""
        self.get_logger().info(
            f"Vertical move to x={x:.3f}, y={y:.3f}, z={z:.3f}"
        )
        if self._move_cartesian(x, y, z):
            return True
        return self._move_to_position(x, y, z)

    def _move_to_position(self, x, y, z):
        self.get_logger().info(
            f"Moving tool0 to x={x:.3f}, y={y:.3f}, z={z:.3f}"
        )

        pc = PositionConstraint()
        pc.header.frame_id = "base_link"
        pc.link_name = "tool0"
        pc.weight = 1.0

        box = SolidPrimitive()
        box.type = SolidPrimitive.BOX
        box.dimensions = [self.POSITION_TOLERANCE] * 3

        target = Pose()
        target.position.x = x
        target.position.y = y
        target.position.z = z
        target.orientation.w = 1.0

        pc.constraint_region.primitives.append(box)
        pc.constraint_region.primitive_poses.append(target)

        # tool0 z huong xuong (quaternion x=1, w=0), tu do xoay quanh truc tool
        oc = OrientationConstraint()
        oc.header.frame_id = "base_link"
        oc.link_name = "tool0"
        oc.orientation.x = 1.0
        oc.orientation.w = 0.0
        oc.absolute_x_axis_tolerance = self.ORIENT_TOLERANCE
        oc.absolute_y_axis_tolerance = self.ORIENT_TOLERANCE
        oc.absolute_z_axis_tolerance = 3.14159
        oc.weight = 1.0

        constraints = Constraints()
        constraints.position_constraints.append(pc)
        constraints.orientation_constraints.append(oc)
        return self._send_goal(constraints)

    def _lift(self, x, y):
        self.get_logger().info("LIFT: moving tool0 to safe height")
        return self._move_vertical(x, y, self.SAFE_Z)

    def _move_to_joint_values(self, joint_values):
        constraints = Constraints()
        for name, value in zip(self.JOINT_NAMES, joint_values):
            jc = JointConstraint()
            jc.joint_name = name
            jc.position = value
            jc.tolerance_above = 0.02
            jc.tolerance_below = 0.02
            jc.weight = 1.0
            constraints.joint_constraints.append(jc)
        return self._send_goal(constraints)

    # ==========================================================
    # SKILLS
    # ==========================================================

    def home(self):
        self.get_logger().info("HOME: moving robot to home position")

        if self._move_to_joint_values(self.HOME):
            self.get_logger().info("HOME -> SUCCESS")
            return self.SUCCESS

        self.get_logger().error("HOME -> FAILED")
        return self.FAILED

    def pick(self, object_name):
        object_name = str(object_name).lower().strip()

        if object_name not in self.OBJECT_POSITIONS:
            self.get_logger().error(f"Invalid object: {object_name}")
            return self.INVALID_OBJECT

        if self.held_object is not None:
            self.get_logger().error(f"Already holding {self.held_object}")
            return self.FAILED

        if self.attach_cubes and not self._gazebo_ready():
            return self.FAILED

        x, y, _ = self.object_positions[object_name]
        self.get_logger().info(f"PICK {object_name}")

        self.get_logger().info("PICK STEP: SAFE")
        if not self._move_to_position(x, y, self.SAFE_Z):
            return self.PLANNING_FAILED

        for label, z in (("APPROACH", self.APPROACH_Z), ("GRIP", self.GRIP_Z)):
            self.get_logger().info(f"PICK STEP: {label}")
            if not self._move_vertical(x, y, z):
                return self.PLANNING_FAILED

        # ATTACH: tu day cube bam theo tool0 (xem _follow_loop)
        self.get_logger().info(f"PICK: attach {object_name}")
        self.held_object = object_name

        old_zone = self.cube_zone.pop(object_name, None)
        if old_zone is not None:
            self.zone_occupant.pop(old_zone, None)

        if not self._lift(x, y):
            self.held_object = None
            return self.PLANNING_FAILED

        self.get_logger().info(f"PICK {object_name} -> SUCCESS")
        return self.SUCCESS

    def place(self, object_name, zone_name):
        object_name = str(object_name).lower().strip()
        zone_name = str(zone_name).lower().strip()

        if object_name not in self.OBJECT_POSITIONS:
            self.get_logger().error(f"Invalid object: {object_name}")
            return self.INVALID_OBJECT

        if zone_name not in self.ZONE_POSITIONS:
            self.get_logger().error(f"Invalid zone: {zone_name}")
            return self.INVALID_ZONE

        if self.held_object != object_name:
            self.get_logger().error(f"Robot is not holding {object_name}")
            return self.FAILED

        occupant = self.zone_occupant.get(zone_name)
        if occupant is not None and occupant != object_name:
            self.get_logger().error(f"{zone_name} is occupied by {occupant}")
            return self.ZONE_OCCUPIED

        x, y, _ = self.ZONE_POSITIONS[zone_name]
        self.get_logger().info(f"PLACE {object_name} -> {zone_name}")

        self.get_logger().info("PLACE STEP: SAFE")
        if not self._move_to_position(x, y, self.SAFE_Z):
            return self.PLANNING_FAILED

        for label, z in (("APPROACH", self.APPROACH_Z), ("PLACE", self.PLACE_Z)):
            self.get_logger().info(f"PLACE STEP: {label}")
            if not self._move_vertical(x, y, z):
                return self.PLANNING_FAILED

        # DETACH: ngung bam theo, dat cube chinh giua zone tren mat ban
        self.get_logger().info(f"PLACE: detach {object_name}")
        self.held_object = None

        wx = x + self.BASE_IN_WORLD[0]
        wy = y + self.BASE_IN_WORLD[1]
        wz = self.TABLE_TOP_WORLD_Z + self.CUBE_HALF + 0.001

        if self.attach_cubes:
            with self._gz_lock:     # doi lan follow dang chay xong
                ok = self._gz_set_pose(object_name, wx, wy, wz)
            if not ok:
                self.get_logger().error("Khong dat duoc cube vao zone (set_pose that bai)")
                return self.FAILED

        self.object_positions[object_name] = [x, y, 0.05]
        self.cube_zone[object_name] = zone_name
        self.zone_occupant[zone_name] = object_name

        if not self._lift(x, y):
            return self.PLANNING_FAILED

        self.get_logger().info(f"PLACE {object_name} -> {zone_name} SUCCESS")
        return self.SUCCESS
