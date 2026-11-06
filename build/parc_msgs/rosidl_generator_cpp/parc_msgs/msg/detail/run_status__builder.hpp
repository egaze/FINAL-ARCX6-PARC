// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from parc_msgs:msg/RunStatus.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "parc_msgs/msg/run_status.hpp"


#ifndef PARC_MSGS__MSG__DETAIL__RUN_STATUS__BUILDER_HPP_
#define PARC_MSGS__MSG__DETAIL__RUN_STATUS__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "parc_msgs/msg/detail/run_status__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace parc_msgs
{

namespace msg
{

namespace builder
{

class Init_RunStatus_false_start
{
public:
  explicit Init_RunStatus_false_start(::parc_msgs::msg::RunStatus & msg)
  : msg_(msg)
  {}
  ::parc_msgs::msg::RunStatus false_start(::parc_msgs::msg::RunStatus::_false_start_type arg)
  {
    msg_.false_start = std::move(arg);
    return std::move(msg_);
  }

private:
  ::parc_msgs::msg::RunStatus msg_;
};

class Init_RunStatus_start_method
{
public:
  explicit Init_RunStatus_start_method(::parc_msgs::msg::RunStatus & msg)
  : msg_(msg)
  {}
  Init_RunStatus_false_start start_method(::parc_msgs::msg::RunStatus::_start_method_type arg)
  {
    msg_.start_method = std::move(arg);
    return Init_RunStatus_false_start(msg_);
  }

private:
  ::parc_msgs::msg::RunStatus msg_;
};

class Init_RunStatus_tags_reported
{
public:
  explicit Init_RunStatus_tags_reported(::parc_msgs::msg::RunStatus & msg)
  : msg_(msg)
  {}
  Init_RunStatus_start_method tags_reported(::parc_msgs::msg::RunStatus::_tags_reported_type arg)
  {
    msg_.tags_reported = std::move(arg);
    return Init_RunStatus_start_method(msg_);
  }

private:
  ::parc_msgs::msg::RunStatus msg_;
};

class Init_RunStatus_tag_order
{
public:
  explicit Init_RunStatus_tag_order(::parc_msgs::msg::RunStatus & msg)
  : msg_(msg)
  {}
  Init_RunStatus_tags_reported tag_order(::parc_msgs::msg::RunStatus::_tag_order_type arg)
  {
    msg_.tag_order = std::move(arg);
    return Init_RunStatus_tags_reported(msg_);
  }

private:
  ::parc_msgs::msg::RunStatus msg_;
};

class Init_RunStatus_time_limit_s
{
public:
  explicit Init_RunStatus_time_limit_s(::parc_msgs::msg::RunStatus & msg)
  : msg_(msg)
  {}
  Init_RunStatus_tag_order time_limit_s(::parc_msgs::msg::RunStatus::_time_limit_s_type arg)
  {
    msg_.time_limit_s = std::move(arg);
    return Init_RunStatus_tag_order(msg_);
  }

private:
  ::parc_msgs::msg::RunStatus msg_;
};

class Init_RunStatus_elapsed_s
{
public:
  explicit Init_RunStatus_elapsed_s(::parc_msgs::msg::RunStatus & msg)
  : msg_(msg)
  {}
  Init_RunStatus_time_limit_s elapsed_s(::parc_msgs::msg::RunStatus::_elapsed_s_type arg)
  {
    msg_.elapsed_s = std::move(arg);
    return Init_RunStatus_time_limit_s(msg_);
  }

private:
  ::parc_msgs::msg::RunStatus msg_;
};

class Init_RunStatus_state
{
public:
  explicit Init_RunStatus_state(::parc_msgs::msg::RunStatus & msg)
  : msg_(msg)
  {}
  Init_RunStatus_elapsed_s state(::parc_msgs::msg::RunStatus::_state_type arg)
  {
    msg_.state = std::move(arg);
    return Init_RunStatus_elapsed_s(msg_);
  }

private:
  ::parc_msgs::msg::RunStatus msg_;
};

class Init_RunStatus_stamp
{
public:
  Init_RunStatus_stamp()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_RunStatus_state stamp(::parc_msgs::msg::RunStatus::_stamp_type arg)
  {
    msg_.stamp = std::move(arg);
    return Init_RunStatus_state(msg_);
  }

private:
  ::parc_msgs::msg::RunStatus msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::parc_msgs::msg::RunStatus>()
{
  return parc_msgs::msg::builder::Init_RunStatus_stamp();
}

}  // namespace parc_msgs

#endif  // PARC_MSGS__MSG__DETAIL__RUN_STATUS__BUILDER_HPP_
