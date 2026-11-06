// generated from rosidl_generator_cpp/resource/idl__struct.hpp.em
// with input from parc_msgs:msg/RunStatus.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "parc_msgs/msg/run_status.hpp"


#ifndef PARC_MSGS__MSG__DETAIL__RUN_STATUS__STRUCT_HPP_
#define PARC_MSGS__MSG__DETAIL__RUN_STATUS__STRUCT_HPP_

#include <algorithm>
#include <array>
#include <cstdint>
#include <memory>
#include <string>
#include <vector>

#include "rosidl_runtime_cpp/bounded_vector.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


// Include directives for member types
// Member 'stamp'
#include "builtin_interfaces/msg/detail/time__struct.hpp"

#ifndef _WIN32
# define DEPRECATED__parc_msgs__msg__RunStatus __attribute__((deprecated))
#else
# define DEPRECATED__parc_msgs__msg__RunStatus __declspec(deprecated)
#endif

namespace parc_msgs
{

namespace msg
{

// message struct
template<class ContainerAllocator>
struct RunStatus_
{
  using Type = RunStatus_<ContainerAllocator>;

  explicit RunStatus_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : stamp(_init)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->state = 0;
      this->elapsed_s = 0.0f;
      this->time_limit_s = 0.0f;
      this->start_method = 0;
      this->false_start = false;
    }
  }

  explicit RunStatus_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : stamp(_alloc, _init)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->state = 0;
      this->elapsed_s = 0.0f;
      this->time_limit_s = 0.0f;
      this->start_method = 0;
      this->false_start = false;
    }
  }

  // field types and members
  using _stamp_type =
    builtin_interfaces::msg::Time_<ContainerAllocator>;
  _stamp_type stamp;
  using _state_type =
    uint8_t;
  _state_type state;
  using _elapsed_s_type =
    float;
  _elapsed_s_type elapsed_s;
  using _time_limit_s_type =
    float;
  _time_limit_s_type time_limit_s;
  using _tag_order_type =
    std::vector<uint8_t, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<uint8_t>>;
  _tag_order_type tag_order;
  using _tags_reported_type =
    std::vector<uint8_t, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<uint8_t>>;
  _tags_reported_type tags_reported;
  using _start_method_type =
    uint8_t;
  _start_method_type start_method;
  using _false_start_type =
    bool;
  _false_start_type false_start;

  // setters for named parameter idiom
  Type & set__stamp(
    const builtin_interfaces::msg::Time_<ContainerAllocator> & _arg)
  {
    this->stamp = _arg;
    return *this;
  }
  Type & set__state(
    const uint8_t & _arg)
  {
    this->state = _arg;
    return *this;
  }
  Type & set__elapsed_s(
    const float & _arg)
  {
    this->elapsed_s = _arg;
    return *this;
  }
  Type & set__time_limit_s(
    const float & _arg)
  {
    this->time_limit_s = _arg;
    return *this;
  }
  Type & set__tag_order(
    const std::vector<uint8_t, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<uint8_t>> & _arg)
  {
    this->tag_order = _arg;
    return *this;
  }
  Type & set__tags_reported(
    const std::vector<uint8_t, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<uint8_t>> & _arg)
  {
    this->tags_reported = _arg;
    return *this;
  }
  Type & set__start_method(
    const uint8_t & _arg)
  {
    this->start_method = _arg;
    return *this;
  }
  Type & set__false_start(
    const bool & _arg)
  {
    this->false_start = _arg;
    return *this;
  }

  // constant declarations
  static constexpr uint8_t IDLE =
    0u;
  static constexpr uint8_t ARMED =
    1u;
  static constexpr uint8_t RUNNING =
    2u;
  static constexpr uint8_t FINISHED =
    3u;
  static constexpr uint8_t TIMED_OUT =
    4u;
  static constexpr uint8_t TERMINATED =
    5u;

  // pointer types
  using RawPtr =
    parc_msgs::msg::RunStatus_<ContainerAllocator> *;
  using ConstRawPtr =
    const parc_msgs::msg::RunStatus_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<parc_msgs::msg::RunStatus_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<parc_msgs::msg::RunStatus_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      parc_msgs::msg::RunStatus_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<parc_msgs::msg::RunStatus_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      parc_msgs::msg::RunStatus_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<parc_msgs::msg::RunStatus_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<parc_msgs::msg::RunStatus_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<parc_msgs::msg::RunStatus_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__parc_msgs__msg__RunStatus
    std::shared_ptr<parc_msgs::msg::RunStatus_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__parc_msgs__msg__RunStatus
    std::shared_ptr<parc_msgs::msg::RunStatus_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const RunStatus_ & other) const
  {
    if (this->stamp != other.stamp) {
      return false;
    }
    if (this->state != other.state) {
      return false;
    }
    if (this->elapsed_s != other.elapsed_s) {
      return false;
    }
    if (this->time_limit_s != other.time_limit_s) {
      return false;
    }
    if (this->tag_order != other.tag_order) {
      return false;
    }
    if (this->tags_reported != other.tags_reported) {
      return false;
    }
    if (this->start_method != other.start_method) {
      return false;
    }
    if (this->false_start != other.false_start) {
      return false;
    }
    return true;
  }
  bool operator!=(const RunStatus_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct RunStatus_

// alias to use template instance with default allocator
using RunStatus =
  parc_msgs::msg::RunStatus_<std::allocator<void>>;

// constant definitions
#if __cplusplus < 201703L
// static constexpr member variable definitions are only needed in C++14 and below, deprecated in C++17
template<typename ContainerAllocator>
constexpr uint8_t RunStatus_<ContainerAllocator>::IDLE;
#endif  // __cplusplus < 201703L
#if __cplusplus < 201703L
// static constexpr member variable definitions are only needed in C++14 and below, deprecated in C++17
template<typename ContainerAllocator>
constexpr uint8_t RunStatus_<ContainerAllocator>::ARMED;
#endif  // __cplusplus < 201703L
#if __cplusplus < 201703L
// static constexpr member variable definitions are only needed in C++14 and below, deprecated in C++17
template<typename ContainerAllocator>
constexpr uint8_t RunStatus_<ContainerAllocator>::RUNNING;
#endif  // __cplusplus < 201703L
#if __cplusplus < 201703L
// static constexpr member variable definitions are only needed in C++14 and below, deprecated in C++17
template<typename ContainerAllocator>
constexpr uint8_t RunStatus_<ContainerAllocator>::FINISHED;
#endif  // __cplusplus < 201703L
#if __cplusplus < 201703L
// static constexpr member variable definitions are only needed in C++14 and below, deprecated in C++17
template<typename ContainerAllocator>
constexpr uint8_t RunStatus_<ContainerAllocator>::TIMED_OUT;
#endif  // __cplusplus < 201703L
#if __cplusplus < 201703L
// static constexpr member variable definitions are only needed in C++14 and below, deprecated in C++17
template<typename ContainerAllocator>
constexpr uint8_t RunStatus_<ContainerAllocator>::TERMINATED;
#endif  // __cplusplus < 201703L

}  // namespace msg

}  // namespace parc_msgs

#endif  // PARC_MSGS__MSG__DETAIL__RUN_STATUS__STRUCT_HPP_
