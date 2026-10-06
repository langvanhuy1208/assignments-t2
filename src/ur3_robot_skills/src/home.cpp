#include <memory>
#include <vector>

#include <rclcpp/rclcpp.hpp>
#include <moveit/move_group_interface/move_group_interface.h>

int main(int argc, char * argv[])
{
    rclcpp::init(argc, argv);

    auto node = std::make_shared<rclcpp::Node>(
        "ur3_home_skill",
        rclcpp::NodeOptions()
            .automatically_declare_parameters_from_overrides(true)
    );

    const std::string planning_group = "ur_manipulator";

    moveit::planning_interface::MoveGroupInterface move_group(
        node,
        planning_group
    );

    // HOME position for UR3
    std::vector<double> home_joint_values = {
        0.0,      // shoulder_pan_joint
        -1.57,    // shoulder_lift_joint
        0.0,      // elbow_joint
        -1.57,    // wrist_1_joint
        0.0,      // wrist_2_joint
        0.0       // wrist_3_joint
    };

    RCLCPP_INFO(
        node->get_logger(),
        "Moving UR3 to HOME..."
    );

    move_group.setJointValueTarget(home_joint_values);

    moveit::planning_interface::MoveGroupInterface::Plan plan;

    bool success =
        (move_group.plan(plan) ==
         moveit::core::MoveItErrorCode::SUCCESS);

    if (!success)
    {
        RCLCPP_ERROR(
            node->get_logger(),
            "PLANNING_FAILED"
        );

        rclcpp::shutdown();
        return 1;
    }

    RCLCPP_INFO(
        node->get_logger(),
        "Planning successful. Executing..."
    );

    auto result = move_group.execute(plan);

    if (result != moveit::core::MoveItErrorCode::SUCCESS)
    {
        RCLCPP_ERROR(
            node->get_logger(),
            "EXECUTION_FAILED"
        );

        rclcpp::shutdown();
        return 1;
    }

    RCLCPP_INFO(
        node->get_logger(),
        "HOME SUCCESS"
    );

    rclcpp::shutdown();

    return 0;
}
