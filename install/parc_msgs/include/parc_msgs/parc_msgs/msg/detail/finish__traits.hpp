// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from parc_msgs:msg/Finish.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "parc_msgs/msg/finish.hpp"


#ifndef PARC_MSGS__MSG__DETAIL__FINISH__TRAITS_HPP_
#define PARC_MSGS__MSG__DETAIL__FINISH__TRAITS_HPP_

#include <stdint.h>

#include <sstream>
#include <string>
#include <type_traits>

#include "parc_msgs/msg/detail/finish__struct.hpp"
#include "rosidl_runtime_cpp/traits.hpp"

// Include directives for member types
// Member 'stamp'
#include "builtin_interfaces/msg/detail/time__traits.hpp"

namespace parc_msgs
{

namespace msg
{

inline void to_flow_style_yaml(
  const Finish & msg,
  std::ostream & out)
{
  out << "{";
  // member: stamp
  {
    out << "stamp: ";
    to_flow_style_yaml(msg.stamp, out);
    out << ", ";
  }

  // member: reason
  {
    out << "reason: ";
    rosidl_generator_traits::value_to_yaml(msg.reason, out);
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const Finish & msg,
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

  // member: reason
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "reason: ";
    rosidl_generator_traits::value_to_yaml(msg.reason, out);
    out << "\n";
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const Finish & msg, bool use_flow_style = false)
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
  const parc_msgs::msg::Finish & msg,
  std::ostream & out, size_t indentation = 0)
{
  parc_msgs::msg::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use parc_msgs::msg::to_yaml() instead")]]
inline std::string to_yaml(const parc_msgs::msg::Finish & msg)
{
  return parc_msgs::msg::to_yaml(msg);
}

template<>
inline const char * data_type<parc_msgs::msg::Finish>()
{
  return "parc_msgs::msg::Finish";
}

template<>
inline const char * name<parc_msgs::msg::Finish>()
{
  return "parc_msgs/msg/Finish";
}

template<>
struct has_fixed_size<parc_msgs::msg::Finish>
  : std::integral_constant<bool, has_fixed_size<builtin_interfaces::msg::Time>::value> {};

template<>
struct has_bounded_size<parc_msgs::msg::Finish>
  : std::integral_constant<bool, has_bounded_size<builtin_interfaces::msg::Time>::value> {};

template<>
struct is_message<parc_msgs::msg::Finish>
  : std::true_type {};

}  // namespace rosidl_generator_traits

#endif  // PARC_MSGS__MSG__DETAIL__FINISH__TRAITS_HPP_
