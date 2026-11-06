// generated from rosidl_typesupport_introspection_c/resource/idl__type_support.c.em
// with input from parc_msgs:msg/StartSignal.idl
// generated code does not contain a copyright notice

#include <stddef.h>
#include "parc_msgs/msg/detail/start_signal__rosidl_typesupport_introspection_c.h"
#include "parc_msgs/msg/rosidl_typesupport_introspection_c__visibility_control.h"
#include "rosidl_typesupport_introspection_c/field_types.h"
#include "rosidl_typesupport_introspection_c/identifier.h"
#include "rosidl_typesupport_introspection_c/message_introspection.h"
#include "parc_msgs/msg/detail/start_signal__functions.h"
#include "parc_msgs/msg/detail/start_signal__struct.h"


// Include directives for member types
// Member `stamp`
#include "builtin_interfaces/msg/time.h"
// Member `stamp`
#include "builtin_interfaces/msg/detail/time__rosidl_typesupport_introspection_c.h"
// Member `heard`
#include "rosidl_runtime_c/string_functions.h"

#ifdef __cplusplus
extern "C"
{
#endif

void parc_msgs__msg__StartSignal__rosidl_typesupport_introspection_c__StartSignal_init_function(
  void * message_memory, enum rosidl_runtime_c__message_initialization _init)
{
  // TODO(karsten1987): initializers are not yet implemented for typesupport c
  // see https://github.com/ros2/ros2/issues/397
  (void) _init;
  parc_msgs__msg__StartSignal__init(message_memory);
}

void parc_msgs__msg__StartSignal__rosidl_typesupport_introspection_c__StartSignal_fini_function(void * message_memory)
{
  parc_msgs__msg__StartSignal__fini(message_memory);
}

static rosidl_typesupport_introspection_c__MessageMember parc_msgs__msg__StartSignal__rosidl_typesupport_introspection_c__StartSignal_message_member_array[3] = {
  {
    "stamp",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    NULL,  // members of sub message (initialized later)
    false,  // is key
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(parc_msgs__msg__StartSignal, stamp),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "method",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_UINT8,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is key
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(parc_msgs__msg__StartSignal, method),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "heard",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_STRING,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is key
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(parc_msgs__msg__StartSignal, heard),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  }
};

static const rosidl_typesupport_introspection_c__MessageMembers parc_msgs__msg__StartSignal__rosidl_typesupport_introspection_c__StartSignal_message_members = {
  "parc_msgs__msg",  // message namespace
  "StartSignal",  // message name
  3,  // number of fields
  sizeof(parc_msgs__msg__StartSignal),
  false,  // has_any_key_member_
  parc_msgs__msg__StartSignal__rosidl_typesupport_introspection_c__StartSignal_message_member_array,  // message members
  parc_msgs__msg__StartSignal__rosidl_typesupport_introspection_c__StartSignal_init_function,  // function to initialize message memory (memory has to be allocated)
  parc_msgs__msg__StartSignal__rosidl_typesupport_introspection_c__StartSignal_fini_function  // function to terminate message instance (will not free memory)
};

// this is not const since it must be initialized on first access
// since C does not allow non-integral compile-time constants
static rosidl_message_type_support_t parc_msgs__msg__StartSignal__rosidl_typesupport_introspection_c__StartSignal_message_type_support_handle = {
  0,
  &parc_msgs__msg__StartSignal__rosidl_typesupport_introspection_c__StartSignal_message_members,
  get_message_typesupport_handle_function,
  &parc_msgs__msg__StartSignal__get_type_hash,
  &parc_msgs__msg__StartSignal__get_type_description,
  &parc_msgs__msg__StartSignal__get_type_description_sources,
};

ROSIDL_TYPESUPPORT_INTROSPECTION_C_EXPORT_parc_msgs
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, parc_msgs, msg, StartSignal)() {
  parc_msgs__msg__StartSignal__rosidl_typesupport_introspection_c__StartSignal_message_member_array[0].members_ =
    ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, builtin_interfaces, msg, Time)();
  if (!parc_msgs__msg__StartSignal__rosidl_typesupport_introspection_c__StartSignal_message_type_support_handle.typesupport_identifier) {
    parc_msgs__msg__StartSignal__rosidl_typesupport_introspection_c__StartSignal_message_type_support_handle.typesupport_identifier =
      rosidl_typesupport_introspection_c__identifier;
  }
  return &parc_msgs__msg__StartSignal__rosidl_typesupport_introspection_c__StartSignal_message_type_support_handle;
}
#ifdef __cplusplus
}
#endif
