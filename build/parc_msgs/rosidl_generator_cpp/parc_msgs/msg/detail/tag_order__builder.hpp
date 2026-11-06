// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from parc_msgs:msg/TagOrder.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "parc_msgs/msg/tag_order.hpp"


#ifndef PARC_MSGS__MSG__DETAIL__TAG_ORDER__BUILDER_HPP_
#define PARC_MSGS__MSG__DETAIL__TAG_ORDER__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "parc_msgs/msg/detail/tag_order__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace parc_msgs
{

namespace msg
{

namespace builder
{

class Init_TagOrder_tag_ids
{
public:
  explicit Init_TagOrder_tag_ids(::parc_msgs::msg::TagOrder & msg)
  : msg_(msg)
  {}
  ::parc_msgs::msg::TagOrder tag_ids(::parc_msgs::msg::TagOrder::_tag_ids_type arg)
  {
    msg_.tag_ids = std::move(arg);
    return std::move(msg_);
  }

private:
  ::parc_msgs::msg::TagOrder msg_;
};

class Init_TagOrder_stamp
{
public:
  Init_TagOrder_stamp()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_TagOrder_tag_ids stamp(::parc_msgs::msg::TagOrder::_stamp_type arg)
  {
    msg_.stamp = std::move(arg);
    return Init_TagOrder_tag_ids(msg_);
  }

private:
  ::parc_msgs::msg::TagOrder msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::parc_msgs::msg::TagOrder>()
{
  return parc_msgs::msg::builder::Init_TagOrder_stamp();
}

}  // namespace parc_msgs

#endif  // PARC_MSGS__MSG__DETAIL__TAG_ORDER__BUILDER_HPP_
