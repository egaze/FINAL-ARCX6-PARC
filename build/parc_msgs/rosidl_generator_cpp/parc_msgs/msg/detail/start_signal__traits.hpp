// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from parc_msgs:msg/StartSignal.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "parc_msgs/msg/start_signal.hpp"


#ifndef PARC_MSGS__MSG__DETAIL__START_SIGNAL__TRAITS_HPP_
#define PARC_MSGS__MSG__DETAIL__START_SIGNAL__TRAITS_HPP_

#include <stdint.h>

#include <sstream>
#include <string>
#include <type_traits>

#include "parc_msgs/msg/detail/start_signal__struct.hpp"
#include "rosidl_runtime_cpp/traits.hpp"

// Include directives for member types
// Member 'stamp'
#include "builtin_interfaces/msg/detail/time__traits.hpp"

namespace parc_msgs
{

namespace msg
{

inline void to_flow_style_yaml(
  const StartSignal & msg,
  std::ostream & out)
{
  out << "{";
  // member: stamp
  {
    out << "stamp: ";
    to_flow_style_yaml(msg.stamp, out);
    out << ", ";
  }

  // member: method
  {
    out << "method: ";
    rosidl_generator_traits::value_to_yaml(msg.method, out);
    out << ", ";
  }

  // member: heard
  {
    out << "heard: ";
    rosidl_generator_traits::value_to_yaml(msg.heard, out);
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const StartSignal & msg,
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

  // member: method
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "method: ";
    rosidl_generator_traits::value_to_yaml(msg.method, out);
    out << "\n";
  }

  // member: heard
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "heard: ";
    rosidl_generator_traits::value_to_yaml(msg.heard, out);
    out << "\n";
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const StartSignal & msg, bool use_flow_style = false)
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
  const parc_msgs::msg::StartSignal & msg,
  std::ostream & out, size_t indentation = 0)
{
  parc_msgs::msg::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use parc_msgs::msg::to_yaml() instead")]]
inline std::string to_yaml(const parc_msgs::msg::StartSignal & msg)
{
  return parc_msgs::msg::to_yaml(msg);
}

template<>
inline const char * data_type<parc_msgs::msg::StartSignal>()
{
  return "parc_msgs::msg::StartSignal";
}

template<>
inline const char * name<parc_msgs::msg::StartSignal>()
{
  return "parc_msgs/msg/StartSignal";
}

template<>
struct has_fixed_size<parc_msgs::msg::StartSignal>
  : std::integral_constant<bool, false> {};

template<>
struct has_bounded_size<parc_msgs::msg::StartSignal>
  : std::integral_constant<bool, false> {};

template<>
struct is_message<parc_msgs::msg::StartSignal>
  : std::true_type {};

}  // namespace rosidl_generator_traits

#endif  // PARC_MSGS__MSG__DETAIL__START_SIGNAL__TRAITS_HPP_
