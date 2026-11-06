// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from parc_msgs:msg/TagVisit.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "parc_msgs/msg/tag_visit.hpp"


#ifndef PARC_MSGS__MSG__DETAIL__TAG_VISIT__TRAITS_HPP_
#define PARC_MSGS__MSG__DETAIL__TAG_VISIT__TRAITS_HPP_

#include <stdint.h>

#include <sstream>
#include <string>
#include <type_traits>

#include "parc_msgs/msg/detail/tag_visit__struct.hpp"
#include "rosidl_runtime_cpp/traits.hpp"

// Include directives for member types
// Member 'header'
#include "std_msgs/msg/detail/header__traits.hpp"
// Member 'image'
#include "sensor_msgs/msg/detail/compressed_image__traits.hpp"

namespace parc_msgs
{

namespace msg
{

inline void to_flow_style_yaml(
  const TagVisit & msg,
  std::ostream & out)
{
  out << "{";
  // member: header
  {
    out << "header: ";
    to_flow_style_yaml(msg.header, out);
    out << ", ";
  }

  // member: tag_id
  {
    out << "tag_id: ";
    rosidl_generator_traits::value_to_yaml(msg.tag_id, out);
    out << ", ";
  }

  // member: image
  {
    out << "image: ";
    to_flow_style_yaml(msg.image, out);
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const TagVisit & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: header
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "header:\n";
    to_block_style_yaml(msg.header, out, indentation + 2);
  }

  // member: tag_id
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "tag_id: ";
    rosidl_generator_traits::value_to_yaml(msg.tag_id, out);
    out << "\n";
  }

  // member: image
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "image:\n";
    to_block_style_yaml(msg.image, out, indentation + 2);
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const TagVisit & msg, bool use_flow_style = false)
{
  std::ostringstream out;
  if (use_flow_style) {
    to_flow_style_yaml(msg, out);
  } else {
    to_block_style_yaml(msg, out);
  }
  return out.str();
}

}  // namespace msg

}  // namespace parc_msgs

namespace rosidl_generator_traits
{

[[deprecated("use parc_msgs::msg::to_block_style_yaml() instead")]]
inline void to_yaml(
  const parc_msgs::msg::TagVisit & msg,
  std::ostream & out, size_t indentation = 0)
{
  parc_msgs::msg::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use parc_msgs::msg::to_yaml() instead")]]
inline std::string to_yaml(const parc_msgs::msg::TagVisit & msg)
{
  return parc_msgs::msg::to_yaml(msg);
}

template<>
inline const char * data_type<parc_msgs::msg::TagVisit>()
{
  return "parc_msgs::msg::TagVisit";
}

template<>
inline const char * name<parc_msgs::msg::TagVisit>()
{
  return "parc_msgs/msg/TagVisit";
}

template<>
struct has_fixed_size<parc_msgs::msg::TagVisit>
  : std::integral_constant<bool, has_fixed_size<sensor_msgs::msg::CompressedImage>::value && has_fixed_size<std_msgs::msg::Header>::value> {};

template<>
struct has_bounded_size<parc_msgs::msg::TagVisit>
  : std::integral_constant<bool, has_bounded_size<sensor_msgs::msg::CompressedImage>::value && has_bounded_size<std_msgs::msg::Header>::value> {};

template<>
struct is_message<parc_msgs::msg::TagVisit>
  : std::true_type {};

}  // namespace rosidl_generator_traits

#endif  // PARC_MSGS__MSG__DETAIL__TAG_VISIT__TRAITS_HPP_
