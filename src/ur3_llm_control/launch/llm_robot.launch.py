from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        Node(
            package='ur3_llm_control',
            executable='llm_node',
            name='llm_node',
            output='screen',
            arguments=['"Put the red cube in zone B."'],
        ),
        Node(
            package='ur3_llm_control',
            executable='skill_executor',
            name='skill_executor',
            output='screen',
        ),
    ])
