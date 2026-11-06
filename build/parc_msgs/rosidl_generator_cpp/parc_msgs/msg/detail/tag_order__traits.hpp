// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from parc_msgs:msg/TagOrder.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "parc_msgs/msg/tag_order.hpp"


#ifndef PARC_MSGS__MSG__DETAIL__TAG_ORDER__TRAITS_HPP_
#define PARC_MSGS__MSG__DETAIL__TAG_ORDER__TRAITS_HPP_

#include <stdint.h>

#include <sstream>
#include <string>
#include <type_traits>

#include "parc_msgs/msg/detail/tag_order__struct.hpp"
#include "rosidl_runtime_cpp/traits.hpp"

// Include directives for member types
// Member 'stamp'
#include "builtin_interfaces/msg/detail/time__traits.hpp"

namespace parc_msgs
{

namespace msg
{

inline void to_flow_style_yaml(
  const TagOrder & msg,
  std::ostream & out)
{
  out << "{";
  // member: stamp
  {
    out << "stamp: ";
    to_flow_style_yaml(msg.stamp, out);
    out << ", ";
  }

  // member: tag_ids
  {
    if (msg.tag_ids.size() == 0) {
      out << "tag_ids: []";
    } else {
      out << "tag_ids: [";
      size_t pending_items = msg.tag_ids.size();
      for (auto item : msg.tag_ids) {
        rosidl_generator_traits::value_to_yaml(item, out);
        if (--pending_items > 0) {
          out << ", ";
        }
      }
      out << "]";
    }
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const TagOrder & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: stamp
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "stamp:\n";
    to_block_style_yaml(msg.stamp, out, indentation + 2);
  }

  // member: tag_ids
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    if (msg.tag_ids.size() == 0) {
      out << "tag_ids: []\n";
    } else {
      out << "tag_ids:\n";
      for (auto item : msg.tag_ids) {
        if (indentation > 0) {
          out << std::string(indentation, ' ');
        }
        out << "- ";
        rosidl_generator_traits::value_to_yaml(item, out);
        out << "\n";
      }
    }
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const TagOrder & msg, bool use_flow_style = false)
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
  const parc_msgs::msg::TagOrder & msg,
  std::ostream & out, size_t indentation = 0)
{
  parc_msgs::msg::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use parc_msgs::msg::to_yaml() instead")]]
inline std::string to_yaml(const parc_msgs::msg::TagOrder & msg)
{
  return parc_msgs::msg::to_yaml(msg);
}

template<>
inline const char * data_type<parc_msgs::msg::TagOrder>()
{
  return "parc_msgs::msg::TagOrder";
}

template<>
inline const char * name<parc_msgs::msg::TagOrder>()
{
  return "parc_msgs/msg/TagOrder";
}

template<>
struct has_fixed_size<parc_msgs::msg::TagOrder>
  : std::integral_constant<bool, false> {};

template<>
struct has_bounded_size<parc_msgs::msg::TagOrder>
  : std::integral_constant<bool, false> {};

template<>
struct is_message<parc_msgs::msg::TagOrder>
  : std::true_type {};

}  // namespace rosidl_generator_traits

#endif  // PARC_MSGS__MSG__DETAIL__TAG_ORDER__TRAITS_HPP_
