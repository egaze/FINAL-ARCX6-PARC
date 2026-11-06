// generated from rosidl_generator_cpp/resource/idl__struct.hpp.em
// with input from parc_msgs:msg/Finish.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "parc_msgs/msg/finish.hpp"


#ifndef PARC_MSGS__MSG__DETAIL__FINISH__STRUCT_HPP_
#define PARC_MSGS__MSG__DETAIL__FINISH__STRUCT_HPP_

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
# define DEPRECATED__parc_msgs__msg__Finish __attribute__((deprecated))
#else
# define DEPRECATED__parc_msgs__msg__Finish __declspec(deprecated)
#endif

namespace parc_msgs
{

namespace msg
{

// message struct
template<class ContainerAllocator>
struct Finish_
{
  using Type = Finish_<ContainerAllocator>;

  explicit Finish_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : stamp(_init)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->reason = 0;
    }
  }

  explicit Finish_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : stamp(_alloc, _init)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->reason = 0;
    }
  }

  // field types and members
  using _stamp_type =
    builtin_interfaces::msg::Time_<ContainerAllocator>;
  _stamp_type stamp;
  using _reason_type =
    uint8_t;
  _reason_type reason;

  // setters for named parameter idiom
  Type & set__stamp(
    const builtin_interfaces::msg::Time_<ContainerAllocator> & _arg)
  {
    this->stamp = _arg;
    return *this;
  }
  Type & set__reason(
    const uint8_t & _arg)
  {
    this->reason = _arg;
    return *this;
  }

  // constant declarations
  static constexpr uint8_t REASON_COMPLETED =
    0u;
  static constexpr uint8_t REASON_GAVE_UP =
    1u;

  // pointer types
  using RawPtr =
    parc_msgs::msg::Finish_<ContainerAllocator> *;
  using ConstRawPtr =
    const parc_msgs::msg::Finish_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<parc_msgs::msg::Finish_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<parc_msgs::msg::Finish_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      parc_msgs::msg::Finish_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<parc_msgs::msg::Finish_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      parc_msgs::msg::Finish_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<parc_msgs::msg::Finish_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<parc_msgs::msg::Finish_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<parc_msgs::msg::Finish_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__parc_msgs__msg__Finish
    std::shared_ptr<parc_msgs::msg::Finish_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__parc_msgs__msg__Finish
    std::shared_ptr<parc_msgs::msg::Finish_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const Finish_ & other) const
  {
    if (this->stamp != other.stamp) {
      return false;
    }
    if (this->reason != other.reason) {
      return false;
    }
    return true;
  }
  bool operator!=(const Finish_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct Finish_

// alias to use template instance with default allocator
using Finish =
  parc_msgs::msg::Finish_<std::allocator<void>>;

// constant definitions
#if __cplusplus < 201703L
// static constexpr member variable definitions are only needed in C++14 and below, deprecated in C++17
template<typename ContainerAllocator>
constexpr uint8_t Finish_<ContainerAllocator>::REASON_COMPLETED;
#endif  // __cplusplus < 201703L
#if __cplusplus < 201703L
// static constexpr member variable definitions are only needed in C++14 and below, deprecated in C++17
template<typename ContainerAllocator>
constexpr uint8_t Finish_<ContainerAllocator>::REASON_GAVE_UP;
#endif  // __cplusplus < 201703L

}  // namespace msg

}  // namespace parc_msgs

#endif  // PARC_MSGS__MSG__DETAIL__FINISH__STRUCT_HPP_
