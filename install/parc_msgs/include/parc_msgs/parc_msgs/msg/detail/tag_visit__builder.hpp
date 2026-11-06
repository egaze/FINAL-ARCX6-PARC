// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from parc_msgs:msg/TagVisit.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "parc_msgs/msg/tag_visit.hpp"


#ifndef PARC_MSGS__MSG__DETAIL__TAG_VISIT__BUILDER_HPP_
#define PARC_MSGS__MSG__DETAIL__TAG_VISIT__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "parc_msgs/msg/detail/tag_visit__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace parc_msgs
{

namespace msg
{

namespace builder
{

class Init_TagVisit_image
{
public:
  explicit Init_TagVisit_image(::parc_msgs::msg::TagVisit & msg)
  : msg_(msg)
  {}
  ::parc_msgs::msg::TagVisit image(::parc_msgs::msg::TagVisit::_image_type arg)
  {
    msg_.image = std::move(arg);
    return std::move(msg_);
  }

private:
  ::parc_msgs::msg::TagVisit msg_;
};

class Init_TagVisit_tag_id
{
public:
  explicit Init_TagVisit_tag_id(::parc_msgs::msg::TagVisit & msg)
  : msg_(msg)
  {}
  Init_TagVisit_image tag_id(::parc_msgs::msg::TagVisit::_tag_id_type arg)
  {
    msg_.tag_id = std::move(arg);
    return Init_TagVisit_image(msg_);
  }

private:
  ::parc_msgs::msg::TagVisit msg_;
};

class Init_TagVisit_header
{
public:
  Init_TagVisit_header()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_TagVisit_tag_id header(::parc_msgs::msg::TagVisit::_header_type arg)
  {
    msg_.header = std::move(arg);
    return Init_TagVisit_tag_id(msg_);
  }

private:
  ::parc_msgs::msg::TagVisit msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::parc_msgs::msg::TagVisit>()
{
  return parc_msgs::msg::builder::Init_TagVisit_header();
}

}  // namespace parc_msgs

#endif  // PARC_MSGS__MSG__DETAIL__TAG_VISIT__BUILDER_HPP_
