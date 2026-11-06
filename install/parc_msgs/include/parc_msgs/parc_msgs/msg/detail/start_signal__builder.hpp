// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from parc_msgs:msg/StartSignal.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "parc_msgs/msg/start_signal.hpp"


#ifndef PARC_MSGS__MSG__DETAIL__START_SIGNAL__BUILDER_HPP_
#define PARC_MSGS__MSG__DETAIL__START_SIGNAL__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "parc_msgs/msg/detail/start_signal__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace parc_msgs
{

namespace msg
{

namespace builder
{

class Init_StartSignal_heard
{
public:
  explicit Init_StartSignal_heard(::parc_msgs::msg::StartSignal & msg)
  : msg_(msg)
  {}
  ::parc_msgs::msg::StartSignal heard(::parc_msgs::msg::StartSignal::_heard_type arg)
  {
    msg_.heard = std::move(arg);
    return std::move(msg_);
  }

private:
  ::parc_msgs::msg::StartSignal msg_;
};

class Init_StartSignal_method
{
public:
  explicit Init_StartSignal_method(::parc_msgs::msg::StartSignal & msg)
  : msg_(msg)
  {}
  Init_StartSignal_heard method(::parc_msgs::msg::StartSignal::_method_type arg)
  {
    msg_.method = std::move(arg);
    return Init_StartSignal_heard(msg_);
  }

private:
  ::parc_msgs::msg::StartSignal msg_;
};

class Init_StartSignal_stamp
{
public:
  Init_StartSignal_stamp()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_StartSignal_method stamp(::parc_msgs::msg::StartSignal::_stamp_type arg)
  {
    msg_.stamp = std::move(arg);
    return Init_StartSignal_method(msg_);
  }

private:
  ::parc_msgs::msg::StartSignal msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::parc_msgs::msg::StartSignal>()
{
  return parc_msgs::msg::builder::Init_StartSignal_stamp();
}

}  // namespace parc_msgs

#endif  // PARC_MSGS__MSG__DETAIL__START_SIGNAL__BUILDER_HPP_
