// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from parc_msgs:msg/Finish.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "parc_msgs/msg/finish.hpp"


#ifndef PARC_MSGS__MSG__DETAIL__FINISH__BUILDER_HPP_
#define PARC_MSGS__MSG__DETAIL__FINISH__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "parc_msgs/msg/detail/finish__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace parc_msgs
{

namespace msg
{

namespace builder
{

class Init_Finish_reason
{
public:
  explicit Init_Finish_reason(::parc_msgs::msg::Finish & msg)
  : msg_(msg)
  {}
  ::parc_msgs::msg::Finish reason(::parc_msgs::msg::Finish::_reason_type arg)
  {
    msg_.reason = std::move(arg);
    return std::move(msg_);
  }

private:
  ::parc_msgs::msg::Finish msg_;
};

class Init_Finish_stamp
{
public:
  Init_Finish_stamp()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_Finish_reason stamp(::parc_msgs::msg::Finish::_stamp_type arg)
  {
    msg_.stamp = std::move(arg);
    return Init_Finish_reason(msg_);
  }

private:
  ::parc_msgs::msg::Finish msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::parc_msgs::msg::Finish>()
{
  return parc_msgs::msg::builder::Init_Finish_stamp();
}

}  // namespace parc_msgs

#endif  // PARC_MSGS__MSG__DETAIL__FINISH__BUILDER_HPP_
