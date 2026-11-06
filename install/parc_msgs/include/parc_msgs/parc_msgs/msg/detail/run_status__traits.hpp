// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from parc_msgs:msg/RunStatus.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "parc_msgs/msg/run_status.hpp"


#ifndef PARC_MSGS__MSG__DETAIL__RUN_STATUS__TRAITS_HPP_
#define PARC_MSGS__MSG__DETAIL__RUN_STATUS__TRAITS_HPP_

#include <stdint.h>

#include <sstream>
#include <string>
#include <type_traits>

#include "parc_msgs/msg/detail/run_status__struct.hpp"
#include "rosidl_runtime_cpp/traits.hpp"

// Include directives for member types
// Member 'stamp'
#include "builtin_interfaces/msg/detail/time__traits.hpp"

namespace parc_msgs
{

namespace msg
{

inline void to_flow_style_yaml(
  const RunStatus & msg,
  std::ostream & out)
{
  out << "{";
  // member: stamp
  {
    out << "stamp: ";
    to_flow_style_yaml(msg.stamp, out);
    out << ", ";
  }

  // member: state
  {
    out << "state: ";
    rosidl_generator_traits::value_to_yaml(msg.state, out);
    out << ", ";
  }

  // member: elapsed_s
  {
    out << "elapsed_s: ";
    rosidl_generator_traits::value_to_yaml(msg.elapsed_s, out);
    out << ", ";
  }

  // member: time_limit_s
  {
    out << "time_limit_s: ";
    rosidl_generator_traits::value_to_yaml(msg.time_limit_s, out);
    out << ", ";
  }

  // member: tag_order
  {
    if (msg.tag_order.size() == 0) {
      out << "tag_order: []";
    } else {
      out << "tag_order: [";
      size_t pending_items = msg.tag_order.size();
      for (auto item : msg.tag_order) {
        rosidl_generator_traits::value_to_yaml(item, out);
        if (--pending_items > 0) {
          out << ", ";
        }
      }
      out << "]";
    }
    out << ", ";
  }

  // member: tags_reported
  {
    if (msg.tags_reported.size() == 0) {
      out << "tags_reported: []";
    } else {
      out << "tags_reported: [";
      size_t pending_items = msg.tags_reported.size();
      for (auto item : msg.tags_reported) {
        rosidl_generator_traits::value_to_yaml(item, out);
        if (--pending_items > 0) {
          out << ", ";
        }
      }
      out << "]";
    }
    out << ", ";
  }

  // member: start_method
  {
    out << "start_method: ";
    rosidl_generator_traits::value_to_yaml(msg.start_method, out);
    out << ", ";
  }

  // member: false_start
  {
    out << "false_start: ";
    rosidl_generator_traits::value_to_yaml(msg.false_start, out);
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const RunStatus & msg,
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

  // member: state
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "state: ";
    rosidl_generator_traits::value_to_yaml(msg.state, out);
    out << "\n";
  }

  // member: elapsed_s
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "elapsed_s: ";
    rosidl_generator_traits::value_to_yaml(msg.elapsed_s, out);
    out << "\n";
  }

  // member: time_limit_s
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "time_limit_s: ";
    rosidl_generator_traits::value_to_yaml(msg.time_limit_s, out);
    out << "\n";
  }

  // member: tag_order
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    if (msg.tag_order.size() == 0) {
      out << "tag_order: []\n";
    } else {
      out << "tag_order:\n";
      for (auto item : msg.tag_order) {
        if (indentation > 0) {
          out << std::string(indentation, ' ');
        }
        out << "- ";
        rosidl_generator_traits::value_to_yaml(item, out);
        out << "\n";
      }
    }
  }

  // member: tags_reported
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    if (msg.tags_reported.size() == 0) {
      out << "tags_reported: []\n";
    } else {
      out << "tags_reported:\n";
      for (auto item : msg.tags_reported) {
        if (indentation > 0) {
          out << std::string(indentation, ' ');
        }
        out << "- ";
        rosidl_generator_traits::value_to_yaml(item, out);
        out << "\n";
      }
    }
  }

  // member: start_method
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "start_method: ";
    rosidl_generator_traits::value_to_yaml(msg.start_method, out);
    out << "\n";
  }

  // member: false_start
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "false_start: ";
    rosidl_generator_traits::value_to_yaml(msg.false_start, out);
    out << "\n";
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const RunStatus & msg, bool use_flow_style = false)
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
  const parc_msgs::msg::RunStatus & msg,
  std::ostream & out, size_t indentation = 0)
{
  parc_msgs::msg::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use parc_msgs::msg::to_yaml() instead")]]
inline std::string to_yaml(const parc_msgs::msg::RunStatus & msg)
{
  return parc_msgs::msg::to_yaml(msg);
}

template<>
inline const char * data_type<parc_msgs::msg::RunStatus>()
{
  return "parc_msgs::msg::RunStatus";
}

template<>
inline const char * name<parc_msgs::msg::RunStatus>()
{
  return "parc_msgs/msg/RunStatus";
}

template<>
struct has_fixed_size<parc_msgs::msg::RunStatus>
  : std::integral_constant<bool, false> {};

template<>
struct has_bounded_size<parc_msgs::msg::RunStatus>
  : std::integral_constant<bool, false> {};

template<>
struct is_message<parc_msgs::msg::RunStatus>
  : std::true_type {};

}  // namespace rosidl_generator_traits

#endif  // PARC_MSGS__MSG__DETAIL__RUN_STATUS__TRAITS_HPP_
