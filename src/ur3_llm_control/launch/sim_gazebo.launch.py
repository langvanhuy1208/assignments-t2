"""Mo Gazebo Classic (world llm_scene.sdf) + UR3 + MoveIt 2 + RViz.

ros2 launch ur3_llm_control sim_gazebo.launch.py
ros2 launch ur3_llm_control sim_gazebo.launch.py gui:=false launch_rviz:=false
"""
from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    IncludeLaunchDescription,
    RegisterEventHandler,
)
from launch.event_handlers import OnProcessExit
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import (
    Command,
    FindExecutable,
    LaunchConfiguration,
    PathJoinSubstitution,
)
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    gui = LaunchConfiguration("gui")
    launch_rviz = LaunchConfiguration("launch_rviz")

    pkg = FindPackageShare("ur3_llm_control")
    world = PathJoinSubstitution([pkg, "worlds", "llm_scene.sdf"])
    urdf = PathJoinSubstitution([pkg, "urdf", "ur.urdf.xacro"])
    controllers = PathJoinSubstitution([pkg, "config", "sim_controllers.yaml"])

    robot_description = {
        "robot_description": ParameterValue(
            Command([
                PathJoinSubstitution([FindExecutable(name="xacro")]), " ", urdf,
                " name:=ur ur_type:=ur3 safety_limits:=true",
                " sim_gazebo:=true",
                " simulation_controllers:=", controllers,
            ]),
            value_type=str,
        )
    }

    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([FindPackageShare("gazebo_ros"), "launch", "gazebo.launch.py"])
        ),
        launch_arguments={"world": world, "gui": gui, "verbose": "false"}.items(),
    )

    robot_state_publisher = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        output="screen",
        parameters=[robot_description, {"use_sim_time": True}],
    )

    spawn_robot = Node(
        package="gazebo_ros",
        executable="spawn_entity.py",
        output="screen",
        arguments=["-topic", "robot_description", "-entity", "ur3"],
    )

    spawn_jsb = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["joint_state_broadcaster", "--controller-manager", "/controller_manager"],
    )
    spawn_jtc = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["joint_trajectory_controller", "--controller-manager", "/controller_manager"],
    )

    # use_sim_time:=true -> ur_moveit.launch.py chon joint_trajectory_controller
    moveit = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([FindPackageShare("ur_moveit_config"), "launch", "ur_moveit.launch.py"])
        ),
        launch_arguments={
            "ur_type": "ur3",
            "use_sim_time": "true",
            "launch_rviz": launch_rviz,
            "launch_servo": "false",
        }.items(),
    )

    return LaunchDescription([
        DeclareLaunchArgument("gui", default_value="true", description="Mo cua so Gazebo"),
        DeclareLaunchArgument("launch_rviz", default_value="true", description="Mo RViz"),
        gazebo,
        robot_state_publisher,
        spawn_robot,
        # spawn_robot xong -> joint_state_broadcaster -> joint_trajectory_controller -> MoveIt
        RegisterEventHandler(OnProcessExit(target_action=spawn_robot, on_exit=[spawn_jsb])),
        RegisterEventHandler(OnProcessExit(target_action=spawn_jsb, on_exit=[spawn_jtc])),
        RegisterEventHandler(OnProcessExit(target_action=spawn_jtc, on_exit=[moveit])),
    ])
