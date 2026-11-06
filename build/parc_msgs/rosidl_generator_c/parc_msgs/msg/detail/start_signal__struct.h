// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from parc_msgs:msg/StartSignal.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "parc_msgs/msg/start_signal.h"


#ifndef PARC_MSGS__MSG__DETAIL__START_SIGNAL__STRUCT_H_
#define PARC_MSGS__MSG__DETAIL__START_SIGNAL__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

// Constants defined in the message

/// Constant 'METHOD_COMMAND'.
/**
  * started by a typed command
 */
enum
{
  parc_msgs__msg__StartSignal__METHOD_COMMAND = 0
};

/// Constant 'METHOD_VOICE'.
/**
  * started by a spoken start word (bonus)
 */
enum
{
  parc_msgs__msg__StartSignal__METHOD_VOICE = 1
};

// Include directives for member types
// Member 'stamp'
#include "builtin_interfaces/msg/detail/time__struct.h"
// Member 'heard'
#include "rosidl_runtime_c/string.h"

/// Struct defined in msg/StartSignal in the package parc_msgs.
/**
  * Published once by the team on /parc/start when the robot starts its run.
  * QoS: reliable, depth 10. The run clock starts when the referee receives it.
 */
typedef struct parc_msgs__msg__StartSignal
{
  builtin_interfaces__msg__Time stamp;
  uint8_t method;
  /// For voice starts: the recognised word ("go", "allez" or "vai"). Empty otherwise.
  rosidl_runtime_c__String heard;
} parc_msgs__msg__StartSignal;

// Struct for a sequence of parc_msgs__msg__StartSignal.
typedef struct parc_msgs__msg__StartSignal__Sequence
{
  parc_msgs__msg__StartSignal * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} parc_msgs__msg__StartSignal__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // PARC_MSGS__MSG__DETAIL__START_SIGNAL__STRUCT_H_
