from setuptools import find_packages, setup

package_name = 'ur3_llm_control'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', ['launch/llm_robot.launch.py']),
        ('share/' + package_name + '/config', ['config/student_config.yaml', 'config/scene.yaml', 'config/initial_positions.yaml']),
        ('share/' + package_name + '/urdf', ['urdf/ur.urdf.xacro']),
        ('share/' + package_name + '/worlds', ['worlds/llm_scene.sdf']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Lang Van Huy',
    maintainer_email='student@example.com',
    description='UR3 skill-based planning with LLM and MoveIt 2',
    license='Apache-2.0',
    extras_require={'test': ['pytest']},
    entry_points={
        'console_scripts': [
            'llm_node = ur3_llm_control.llm_node:main',
            'skill_executor = ur3_llm_control.skill_executor:main',
            'command_node = ur3_llm_control.command_node:main',
            'ur3_cli = ur3_llm_control.cli_node:main',
            'move_home = ur3_llm_control.move_home:main',
            'move_joint = ur3_llm_control.move_joint:main',
            'move_to_pose = ur3_llm_control.move_to_pose:main',
        ],
    },
)
