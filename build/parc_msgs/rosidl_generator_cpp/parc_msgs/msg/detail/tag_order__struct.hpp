// generated from rosidl_generator_cpp/resource/idl__struct.hpp.em
// with input from parc_msgs:msg/TagOrder.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "parc_msgs/msg/tag_order.hpp"


#ifndef PARC_MSGS__MSG__DETAIL__TAG_ORDER__STRUCT_HPP_
#define PARC_MSGS__MSG__DETAIL__TAG_ORDER__STRUCT_HPP_

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
# define DEPRECATED__parc_msgs__msg__TagOrder __attribute__((deprecated))
#else
# define DEPRECATED__parc_msgs__msg__TagOrder __declspec(deprecated)
#endif

namespace parc_msgs
{

namespace msg
{

// message struct
template<class ContainerAllocator>
struct TagOrder_
{
  using Type = TagOrder_<ContainerAllocator>;

  explicit TagOrder_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : stamp(_init)
  {
    (void)_init;
  }

  explicit TagOrder_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : stamp(_alloc, _init)
  {
    (void)_init;
  }

  // field types and members
  using _stamp_type =
    builtin_interfaces::msg::Time_<ContainerAllocator>;
  _stamp_type stamp;
  using _tag_ids_type =
    std::vector<uint8_t, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<uint8_t>>;
  _tag_ids_type tag_ids;

  // setters for named parameter idiom
  Type & set__stamp(
    const builtin_interfaces::msg::Time_<ContainerAllocator> & _arg)
  {
    this->stamp = _arg;
    return *this;
  }
  Type & set__tag_ids(
    const std::vector<uint8_t, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<uint8_t>> & _arg)
  {
    this->tag_ids = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    parc_msgs::msg::TagOrder_<ContainerAllocator> *;
  using ConstRawPtr =
    const parc_msgs::msg::TagOrder_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<parc_msgs::msg::TagOrder_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<parc_msgs::msg::TagOrder_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      parc_msgs::msg::TagOrder_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<parc_msgs::msg::TagOrder_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      parc_msgs::msg::TagOrder_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<parc_msgs::msg::TagOrder_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<parc_msgs::msg::TagOrder_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<parc_msgs::msg::TagOrder_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__parc_msgs__msg__TagOrder
    std::shared_ptr<parc_msgs::msg::TagOrder_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__parc_msgs__msg__TagOrder
    std::shared_ptr<parc_msgs::msg::TagOrder_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const TagOrder_ & other) const
  {
    if (this->stamp != other.stamp) {
      return false;
    }
    if (this->tag_ids != other.tag_ids) {
      return false;
    }
    return true;
  }
  bool operator!=(const TagOrder_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct TagOrder_

// alias to use template instance with default allocator
using TagOrder =
  parc_msgs::msg::TagOrder_<std::allocator<void>>;

// constant definitions

}  // namespace msg

}  // namespace parc_msgs

#endif  // PARC_MSGS__MSG__DETAIL__TAG_ORDER__STRUCT_HPP_
