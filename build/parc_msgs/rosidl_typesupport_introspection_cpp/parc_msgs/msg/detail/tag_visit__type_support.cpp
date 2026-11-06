// generated from rosidl_typesupport_introspection_cpp/resource/idl__type_support.cpp.em
// with input from parc_msgs:msg/TagVisit.idl
// generated code does not contain a copyright notice

#include "array"
#include "cstddef"
#include "string"
#include "vector"
#include "rosidl_runtime_c/message_type_support_struct.h"
#include "rosidl_typesupport_cpp/message_type_support.hpp"
#include "rosidl_typesupport_interface/macros.h"
#include "parc_msgs/msg/detail/tag_visit__functions.h"
#include "parc_msgs/msg/detail/tag_visit__struct.hpp"
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

void TagVisit_init_function(
  void * message_memory, rosidl_runtime_cpp::MessageInitialization _init)
{
  new (message_memory) parc_msgs::msg::TagVisit(_init);
}

void TagVisit_fini_function(void * message_memory)
{
  auto typed_message = static_cast<parc_msgs::msg::TagVisit *>(message_memory);
  typed_message->~TagVisit();
}

static const ::rosidl_typesupport_introspection_cpp::MessageMember TagVisit_message_member_array[3] = {
  {
    "header",  // name
    ::rosidl_typesupport_introspection_cpp::ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    ::rosidl_typesupport_introspection_cpp::get_message_type_support_handle<std_msgs::msg::Header>(),  // members of sub message
    false,  // is key
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(parc_msgs::msg::TagVisit, header),  // bytes offset in struct
    nullptr,  // default value
    nullptr,  // size() function pointer
    nullptr,  // get_const(index) function pointer
    nullptr,  // get(index) function pointer
    nullptr,  // fetch(index, &value) function pointer
    nullptr,  // assign(index, value) function pointer
    nullptr  // resize(index) function pointer
  },
  {
    "tag_id",  // name
    ::rosidl_typesupport_introspection_cpp::ROS_TYPE_UINT8,  // type
    0,  // upper bound of string
    nullptr,  // members of sub message
    false,  // is key
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(parc_msgs::msg::TagVisit, tag_id),  // bytes offset in struct
    nullptr,  // default value
    nullptr,  // size() function pointer
    nullptr,  // get_const(index) function pointer
    nullptr,  // get(index) function pointer
    nullptr,  // fetch(index, &value) function pointer
    nullptr,  // assign(index, value) function pointer
    nullptr  // resize(index) function pointer
  },
  {
    "image",  // name
    ::rosidl_typesupport_introspection_cpp::ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    ::rosidl_typesupport_introspection_cpp::get_message_type_support_handle<sensor_msgs::msg::CompressedImage>(),  // members of sub message
    false,  // is key
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(parc_msgs::msg::TagVisit, image),  // bytes offset in struct
    nullptr,  // default value
    nullptr,  // size() function pointer
    nullptr,  // get_const(index) function pointer
    nullptr,  // get(index) function pointer
    nullptr,  // fetch(index, &value) function pointer
    nullptr,  // assign(index, value) function pointer
    nullptr  // resize(index) function pointer
  }
};

static const ::rosidl_typesupport_introspection_cpp::MessageMembers TagVisit_message_members = {
  "parc_msgs::msg",  // message namespace
  "TagVisit",  // message name
  3,  // number of fields
  sizeof(parc_msgs::msg::TagVisit),
  false,  // has_any_key_member_
  TagVisit_message_member_array,  // message members
  TagVisit_init_function,  // function to initialize message memory (memory has to be allocated)
  TagVisit_fini_function  // function to terminate message instance (will not free memory)
};

static const rosidl_message_type_support_t TagVisit_message_type_support_handle = {
  ::rosidl_typesupport_introspection_cpp::typesupport_identifier,
  &TagVisit_message_members,
  get_message_typesupport_handle_function,
  &parc_msgs__msg__TagVisit__get_type_hash,
  &parc_msgs__msg__TagVisit__get_type_description,
  &parc_msgs__msg__TagVisit__get_type_description_sources,
};

}  // namespace rosidl_typesupport_introspection_cpp

}  // namespace msg

}  // namespace parc_msgs


namespace rosidl_typesupport_introspection_cpp
{

template<>
ROSIDL_TYPESUPPORT_INTROSPECTION_CPP_PUBLIC
const rosidl_message_type_support_t *
get_message_type_support_handle<parc_msgs::msg::TagVisit>()
{
  return &::parc_msgs::msg::rosidl_typesupport_introspection_cpp::TagVisit_message_type_support_handle;
}

}  // namespace rosidl_typesupport_introspection_cpp

#ifdef __cplusplus
extern "C"
{
#endif

ROSIDL_TYPESUPPORT_INTROSPECTION_CPP_PUBLIC
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_cpp, parc_msgs, msg, TagVisit)() {
  return &::parc_msgs::msg::rosidl_typesupport_introspection_cpp::TagVisit_message_type_support_handle;
}

#ifdef __cplusplus
}
#endif
