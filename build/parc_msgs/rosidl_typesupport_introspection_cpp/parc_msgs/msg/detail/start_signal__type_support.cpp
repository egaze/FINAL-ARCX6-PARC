// generated from rosidl_typesupport_introspection_cpp/resource/idl__type_support.cpp.em
// with input from parc_msgs:msg/StartSignal.idl
// generated code does not contain a copyright notice

#include "array"
#include "cstddef"
#include "string"
#include "vector"
#include "rosidl_runtime_c/message_type_support_struct.h"
#include "rosidl_typesupport_cpp/message_type_support.hpp"
#include "rosidl_typesupport_interface/macros.h"
#include "parc_msgs/msg/detail/start_signal__functions.h"
#include "parc_msgs/msg/detail/start_signal__struct.hpp"
#include "rosidl_typesupport_introspection_cpp/field_types.hpp"
#include "rosidl_typesupport_introspection_cpp/identifier.hpp"
#include "rosidl_typesupport_introspection_cpp/message_introspection.hpp"
#include "rosidl_typesupport_introspection_cpp/message_type_support_decl.hpp"
#include "rosidl_typesupport_introspection_cpp/visibility_control.h"

namespace parc_msgs
{

namespace msg
{

namespace rosidl_typesupport_introspection_cpp
{

void StartSignal_init_function(
  void * message_memory, rosidl_runtime_cpp::MessageInitialization _init)
{
  new (message_memory) parc_msgs::msg::StartSignal(_init);
}

void StartSignal_fini_function(void * message_memory)
{
  auto typed_message = static_cast<parc_msgs::msg::StartSignal *>(message_memory);
  typed_message->~StartSignal();
}

static const ::rosidl_typesupport_introspection_cpp::MessageMember StartSignal_message_member_array[3] = {
  {
    "stamp",  // name
    ::rosidl_typesupport_introspection_cpp::ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    ::rosidl_typesupport_introspection_cpp::get_message_type_support_handle<builtin_interfaces::msg::Time>(),  // members of sub message
    false,  // is key
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(parc_msgs::msg::StartSignal, stamp),  // bytes offset in struct
    nullptr,  // default value
    nullptr,  // size() function pointer
    nullptr,  // get_const(index) function pointer
    nullptr,  // get(index) function pointer
    nullptr,  // fetch(index, &value) function pointer
    nullptr,  // assign(index, value) function pointer
    nullptr  // resize(index) function pointer
  },
  {
    "method",  // name
    ::rosidl_typesupport_introspection_cpp::ROS_TYPE_UINT8,  // type
    0,  // upper bound of string
    nullptr,  // members of sub message
    false,  // is key
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(parc_msgs::msg::StartSignal, method),  // bytes offset in struct
    nullptr,  // default value
    nullptr,  // size() function pointer
    nullptr,  // get_const(index) function pointer
    nullptr,  // get(index) function pointer
    nullptr,  // fetch(index, &value) function pointer
    nullptr,  // assign(index, value) function pointer
    nullptr  // resize(index) function pointer
  },
  {
    "heard",  // name
    ::rosidl_typesupport_introspection_cpp::ROS_TYPE_STRING,  // type
    0,  // upper bound of string
    nullptr,  // members of sub message
    false,  // is key
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(parc_msgs::msg::StartSignal, heard),  // bytes offset in struct
    nullptr,  // default value
    nullptr,  // size() function pointer
    nullptr,  // get_const(index) function pointer
    nullptr,  // get(index) function pointer
    nullptr,  // fetch(index, &value) function pointer
    nullptr,  // assign(index, value) function pointer
    nullptr  // resize(index) function pointer
  }
};

static const ::rosidl_typesupport_introspection_cpp::MessageMembers StartSignal_message_members = {
  "parc_msgs::msg",  // message namespace
  "StartSignal",  // message name
  3,  // number of fields
  sizeof(parc_msgs::msg::StartSignal),
  false,  // has_any_key_member_
  StartSignal_message_member_array,  // message members
  StartSignal_init_function,  // function to initialize message memory (memory has to be allocated)
  StartSignal_fini_function  // function to terminate message instance (will not free memory)
};

static const rosidl_message_type_support_t StartSignal_message_type_support_handle = {
  ::rosidl_typesupport_introspection_cpp::typesupport_identifier,
  &StartSignal_message_members,
  get_message_typesupport_handle_function,
  &parc_msgs__msg__StartSignal__get_type_hash,
  &parc_msgs__msg__StartSignal__get_type_description,
  &parc_msgs__msg__StartSignal__get_type_description_sources,
};

}  // namespace rosidl_typesupport_introspection_cpp

}  // namespace msg

}  // namespace parc_msgs


namespace rosidl_typesupport_introspection_cpp
{

template<>
ROSIDL_TYPESUPPORT_INTROSPECTION_CPP_PUBLIC
const rosidl_message_type_support_t *
get_message_type_support_handle<parc_msgs::msg::StartSignal>()
{
  return &::parc_msgs::msg::rosidl_typesupport_introspection_cpp::StartSignal_message_type_support_handle;
}

}  // namespace rosidl_typesupport_introspection_cpp

#ifdef __cplusplus
extern "C"
{
#endif

ROSIDL_TYPESUPPORT_INTROSPECTION_CPP_PUBLIC
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_cpp, parc_msgs, msg, StartSignal)() {
  return &::parc_msgs::msg::rosidl_typesupport_introspection_cpp::StartSignal_message_type_support_handle;
}

#ifdef __cplusplus
}
#endif
