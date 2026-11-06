// generated from rosidl_typesupport_introspection_c/resource/idl__type_support.c.em
// with input from parc_msgs:msg/RunStatus.idl
// generated code does not contain a copyright notice

#include <stddef.h>
#include "parc_msgs/msg/detail/run_status__rosidl_typesupport_introspection_c.h"
#include "parc_msgs/msg/rosidl_typesupport_introspection_c__visibility_control.h"
#include "rosidl_typesupport_introspection_c/field_types.h"
#include "rosidl_typesupport_introspection_c/identifier.h"
#include "rosidl_typesupport_introspection_c/message_introspection.h"
#include "parc_msgs/msg/detail/run_status__functions.h"
#include "parc_msgs/msg/detail/run_status__struct.h"


// Include directives for member types
// Member `stamp`
#include "builtin_interfaces/msg/time.h"
// Member `stamp`
#include "builtin_interfaces/msg/detail/time__rosidl_typesupport_introspection_c.h"
// Member `tag_order`
// Member `tags_reported`
#include "rosidl_runtime_c/primitives_sequence_functions.h"

#ifdef __cplusplus
extern "C"
{
#endif

void parc_msgs__msg__RunStatus__rosidl_typesupport_introspection_c__RunStatus_init_function(
  void * message_memory, enum rosidl_runtime_c__message_initialization _init)
{
  // TODO(karsten1987): initializers are not yet implemented for typesupport c
  // see https://github.com/ros2/ros2/issues/397
  (void) _init;
  parc_msgs__msg__RunStatus__init(message_memory);
}

void parc_msgs__msg__RunStatus__rosidl_typesupport_introspection_c__RunStatus_fini_function(void * message_memory)
{
  parc_msgs__msg__RunStatus__fini(message_memory);
}

size_t parc_msgs__msg__RunStatus__rosidl_typesupport_introspection_c__size_function__RunStatus__tag_order(
  const void * untyped_member)
{
  const rosidl_runtime_c__uint8__Sequence * member =
    (const rosidl_runtime_c__uint8__Sequence *)(untyped_member);
  return member->size;
}

const void * parc_msgs__msg__RunStatus__rosidl_typesupport_introspection_c__get_const_function__RunStatus__tag_order(
  const void * untyped_member, size_t index)
{
  const rosidl_runtime_c__uint8__Sequence * member =
    (const rosidl_runtime_c__uint8__Sequence *)(untyped_member);
  return &member->data[index];
}

void * parc_msgs__msg__RunStatus__rosidl_typesupport_introspection_c__get_function__RunStatus__tag_order(
  void * untyped_member, size_t index)
{
  rosidl_runtime_c__uint8__Sequence * member =
    (rosidl_runtime_c__uint8__Sequence *)(untyped_member);
  return &member->data[index];
}

void parc_msgs__msg__RunStatus__rosidl_typesupport_introspection_c__fetch_function__RunStatus__tag_order(
  const void * untyped_member, size_t index, void * untyped_value)
{
  const uint8_t * item =
    ((const uint8_t *)
    parc_msgs__msg__RunStatus__rosidl_typesupport_introspection_c__get_const_function__RunStatus__tag_order(untyped_member, index));
  uint8_t * value =
    (uint8_t *)(untyped_value);
  *value = *item;
}

void parc_msgs__msg__RunStatus__rosidl_typesupport_introspection_c__assign_function__RunStatus__tag_order(
  void * untyped_member, size_t index, const void * untyped_value)
{
  uint8_t * item =
    ((uint8_t *)
    parc_msgs__msg__RunStatus__rosidl_typesupport_introspection_c__get_function__RunStatus__tag_order(untyped_member, index));
  const uint8_t * value =
    (const uint8_t *)(untyped_value);
  *item = *value;
}

bool parc_msgs__msg__RunStatus__rosidl_typesupport_introspection_c__resize_function__RunStatus__tag_order(
  void * untyped_member, size_t size)
{
  rosidl_runtime_c__uint8__Sequence * member =
    (rosidl_runtime_c__uint8__Sequence *)(untyped_member);
  rosidl_runtime_c__uint8__Sequence__fini(member);
  return rosidl_runtime_c__uint8__Sequence__init(member, size);
}

size_t parc_msgs__msg__RunStatus__rosidl_typesupport_introspection_c__size_function__RunStatus__tags_reported(
  const void * untyped_member)
{
  const rosidl_runtime_c__uint8__Sequence * member =
    (const rosidl_runtime_c__uint8__Sequence *)(untyped_member);
  return member->size;
}

const void * parc_msgs__msg__RunStatus__rosidl_typesupport_introspection_c__get_const_function__RunStatus__tags_reported(
  const void * untyped_member, size_t index)
{
  const rosidl_runtime_c__uint8__Sequence * member =
    (const rosidl_runtime_c__uint8__Sequence *)(untyped_member);
  return &member->data[index];
}

void * parc_msgs__msg__RunStatus__rosidl_typesupport_introspection_c__get_function__RunStatus__tags_reported(
  void * untyped_member, size_t index)
{
  rosidl_runtime_c__uint8__Sequence * member =
    (rosidl_runtime_c__uint8__Sequence *)(untyped_member);
  return &member->data[index];
}

void parc_msgs__msg__RunStatus__rosidl_typesupport_introspection_c__fetch_function__RunStatus__tags_reported(
  const void * untyped_member, size_t index, void * untyped_value)
{
  const uint8_t * item =
    ((const uint8_t *)
    parc_msgs__msg__RunStatus__rosidl_typesupport_introspection_c__get_const_function__RunStatus__tags_reported(untyped_member, index));
  uint8_t * value =
    (uint8_t *)(untyped_value);
  *value = *item;
}

void parc_msgs__msg__RunStatus__rosidl_typesupport_introspection_c__assign_function__RunStatus__tags_reported(
  void * untyped_member, size_t index, const void * untyped_value)
{
  uint8_t * item =
    ((uint8_t *)
    parc_msgs__msg__RunStatus__rosidl_typesupport_introspection_c__get_function__RunStatus__tags_reported(untyped_member, index));
  const uint8_t * value =
    (const uint8_t *)(untyped_value);
  *item = *value;
}

bool parc_msgs__msg__RunStatus__rosidl_typesupport_introspection_c__resize_function__RunStatus__tags_reported(
  void * untyped_member, size_t size)
{
  rosidl_runtime_c__uint8__Sequence * member =
    (rosidl_runtime_c__uint8__Sequence *)(untyped_member);
  rosidl_runtime_c__uint8__Sequence__fini(member);
  return rosidl_runtime_c__uint8__Sequence__init(member, size);
}

static rosidl_typesupport_introspection_c__MessageMember parc_msgs__msg__RunStatus__rosidl_typesupport_introspection_c__RunStatus_message_member_array[8] = {
  {
    "stamp",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    NULL,  // members of sub message (initialized later)
    false,  // is key
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(parc_msgs__msg__RunStatus, stamp),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "state",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_UINT8,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is key
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(parc_msgs__msg__RunStatus, state),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "elapsed_s",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_FLOAT,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is key
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(parc_msgs__msg__RunStatus, elapsed_s),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "time_limit_s",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_FLOAT,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is key
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(parc_msgs__msg__RunStatus, time_limit_s),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "tag_order",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_UINT8,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is key
    true,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(parc_msgs__msg__RunStatus, tag_order),  // bytes offset in struct
    NULL,  // default value
    parc_msgs__msg__RunStatus__rosidl_typesupport_introspection_c__size_function__RunStatus__tag_order,  // size() function pointer
    parc_msgs__msg__RunStatus__rosidl_typesupport_introspection_c__get_const_function__RunStatus__tag_order,  // get_const(index) function pointer
    parc_msgs__msg__RunStatus__rosidl_typesupport_introspection_c__get_function__RunStatus__tag_order,  // get(index) function pointer
    parc_msgs__msg__RunStatus__rosidl_typesupport_introspection_c__fetch_function__RunStatus__tag_order,  // fetch(index, &value) function pointer
    parc_msgs__msg__RunStatus__rosidl_typesupport_introspection_c__assign_function__RunStatus__tag_order,  // assign(index, value) function pointer
    parc_msgs__msg__RunStatus__rosidl_typesupport_introspection_c__resize_function__RunStatus__tag_order  // resize(index) function pointer
  },
  {
    "tags_reported",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_UINT8,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is key
    true,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(parc_msgs__msg__RunStatus, tags_reported),  // bytes offset in struct
    NULL,  // default value
    parc_msgs__msg__RunStatus__rosidl_typesupport_introspection_c__size_function__RunStatus__tags_reported,  // size() function pointer
    parc_msgs__msg__RunStatus__rosidl_typesupport_introspection_c__get_const_function__RunStatus__tags_reported,  // get_const(index) function pointer
    parc_msgs__msg__RunStatus__rosidl_typesupport_introspection_c__get_function__RunStatus__tags_reported,  // get(index) function pointer
    parc_msgs__msg__RunStatus__rosidl_typesupport_introspection_c__fetch_function__RunStatus__tags_reported,  // fetch(index, &value) function pointer
    parc_msgs__msg__RunStatus__rosidl_typesupport_introspection_c__assign_function__RunStatus__tags_reported,  // assign(index, value) function pointer
    parc_msgs__msg__RunStatus__rosidl_typesupport_introspection_c__resize_function__RunStatus__tags_reported  // resize(index) function pointer
  },
  {
    "start_method",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_UINT8,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is key
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(parc_msgs__msg__RunStatus, start_method),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "false_start",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_BOOLEAN,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is key
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(parc_msgs__msg__RunStatus, false_start),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  }
};

static const rosidl_typesupport_introspection_c__MessageMembers parc_msgs__msg__RunStatus__rosidl_typesupport_introspection_c__RunStatus_message_members = {
  "parc_msgs__msg",  // message namespace
  "RunStatus",  // message name
  8,  // number of fields
  sizeof(parc_msgs__msg__RunStatus),
  false,  // has_any_key_member_
  parc_msgs__msg__RunStatus__rosidl_typesupport_introspection_c__RunStatus_message_member_array,  // message members
  parc_msgs__msg__RunStatus__rosidl_typesupport_introspection_c__RunStatus_init_function,  // function to initialize message memory (memory has to be allocated)
  parc_msgs__msg__RunStatus__rosidl_typesupport_introspection_c__RunStatus_fini_function  // function to terminate message instance (will not free memory)
};

// this is not const since it must be initialized on first access
// since C does not allow non-integral compile-time constants
static rosidl_message_type_support_t parc_msgs__msg__RunStatus__rosidl_typesupport_introspection_c__RunStatus_message_type_support_handle = {
  0,
  &parc_msgs__msg__RunStatus__rosidl_typesupport_introspection_c__RunStatus_message_members,
  get_message_typesupport_handle_function,
  &parc_msgs__msg__RunStatus__get_type_hash,
  &parc_msgs__msg__RunStatus__get_type_description,
  &parc_msgs__msg__RunStatus__get_type_description_sources,
};

ROSIDL_TYPESUPPORT_INTROSPECTION_C_EXPORT_parc_msgs
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, parc_msgs, msg, RunStatus)() {
  parc_msgs__msg__RunStatus__rosidl_typesupport_introspection_c__RunStatus_message_member_array[0].members_ =
    ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, builtin_interfaces, msg, Time)();
  if (!parc_msgs__msg__RunStatus__rosidl_typesupport_introspection_c__RunStatus_message_type_support_handle.typesupport_identifier) {
    parc_msgs__msg__RunStatus__rosidl_typesupport_introspection_c__RunStatus_message_type_support_handle.typesupport_identifier =
      rosidl_typesupport_introspection_c__identifier;
  }
  return &parc_msgs__msg__RunStatus__rosidl_typesupport_introspection_c__RunStatus_message_type_support_handle;
}
#ifdef __cplusplus
}
#endif
