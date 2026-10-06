cmake_minimum_required(VERSION 3.8)

project(ur3_robot_skills)

if(NOT CMAKE_CXX_STANDARD)
  set(CMAKE_CXX_STANDARD 17)
endif()

find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(moveit_ros_planning_interface REQUIRED)

add_executable(home src/home.cpp)

ament_target_dependencies(home
  rclcpp
  moveit_ros_planning_interface
)

install(
  TARGETS home
  DESTINATION lib/${PROJECT_NAME}
)

ament_package()
