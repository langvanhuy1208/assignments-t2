// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from ur_dashboard_msgs:srv/DownloadSupportFile.idl
// generated code does not contain a copyright notice

#ifndef UR_DASHBOARD_MSGS__SRV__DETAIL__DOWNLOAD_SUPPORT_FILE__BUILDER_HPP_
#define UR_DASHBOARD_MSGS__SRV__DETAIL__DOWNLOAD_SUPPORT_FILE__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "ur_dashboard_msgs/srv/detail/download_support_file__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace ur_dashboard_msgs
{

namespace srv
{

namespace builder
{

class Init_DownloadSupportFile_Request_target_path
{
public:
  Init_DownloadSupportFile_Request_target_path()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  ::ur_dashboard_msgs::srv::DownloadSupportFile_Request target_path(::ur_dashboard_msgs::srv::DownloadSupportFile_Request::_target_path_type arg)
  {
    msg_.target_path = std::move(arg);
    return std::move(msg_);
  }

private:
  ::ur_dashboard_msgs::srv::DownloadSupportFile_Request msg_;
};

}  // namespace builder

}  // namespace srv

template<typename MessageType>
auto build();

template<>
inline
auto build<::ur_dashboard_msgs::srv::DownloadSupportFile_Request>()
{
  return ur_dashboard_msgs::srv::builder::Init_DownloadSupportFile_Request_target_path();
}

}  // namespace ur_dashboard_msgs


namespace ur_dashboard_msgs
{

namespace srv
{

namespace builder
{

class Init_DownloadSupportFile_Response_support_files_present
{
public:
  explicit Init_DownloadSupportFile_Response_support_files_present(::ur_dashboard_msgs::srv::DownloadSupportFile_Response & msg)
  : msg_(msg)
  {}
  ::ur_dashboard_msgs::srv::DownloadSupportFile_Response support_files_present(::ur_dashboard_msgs::srv::DownloadSupportFile_Response::_support_files_present_type arg)
  {
    msg_.support_files_present = std::move(arg);
    return std::move(msg_);
  }

private:
  ::ur_dashboard_msgs::srv::DownloadSupportFile_Response msg_;
};

class Init_DownloadSupportFile_Response_success
{
public:
  explicit Init_DownloadSupportFile_Response_success(::ur_dashboard_msgs::srv::DownloadSupportFile_Response & msg)
  : msg_(msg)
  {}
  Init_DownloadSupportFile_Response_support_files_present success(::ur_dashboard_msgs::srv::DownloadSupportFile_Response::_success_type arg)
  {
    msg_.success = std::move(arg);
    return Init_DownloadSupportFile_Response_support_files_present(msg_);
  }

private:
  ::ur_dashboard_msgs::srv::DownloadSupportFile_Response msg_;
};

class Init_DownloadSupportFile_Response_answer
{
public:
  Init_DownloadSupportFile_Response_answer()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_DownloadSupportFile_Response_success answer(::ur_dashboard_msgs::srv::DownloadSupportFile_Response::_answer_type arg)
  {
    msg_.answer = std::move(arg);
    return Init_DownloadSupportFile_Response_success(msg_);
  }

private:
  ::ur_dashboard_msgs::srv::DownloadSupportFile_Response msg_;
};

}  // namespace builder

}  // namespace srv

template<typename MessageType>
auto build();

template<>
inline
auto build<::ur_dashboard_msgs::srv::DownloadSupportFile_Response>()
{
  return ur_dashboard_msgs::srv::builder::Init_DownloadSupportFile_Response_answer();
}

}  // namespace ur_dashboard_msgs

#endif  // UR_DASHBOARD_MSGS__SRV__DETAIL__DOWNLOAD_SUPPORT_FILE__BUILDER_HPP_
