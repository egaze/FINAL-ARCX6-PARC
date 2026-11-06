// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from parc_msgs:msg/Finish.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "parc_msgs/msg/finish.h"


#ifndef PARC_MSGS__MSG__DETAIL__FINISH__STRUCT_H_
#define PARC_MSGS__MSG__DETAIL__FINISH__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

// Constants defined in the message

/// Constant 'REASON_COMPLETED'.
/**
  * the robot has done everything it is going to do
 */
enum
{
  parc_msgs__msg__Finish__REASON_COMPLETED = 0
};

/// Constant 'REASON_GAVE_UP'.
/**
  * the robot cannot continue
 */
enum
{
  parc_msgs__msg__Finish__REASON_GAVE_UP = 1
};

// Include directives for member types
// Member 'stamp'
#include "builtin_interfaces/msg/detail/time__struct.h"

/// Struct defined in msg/Finish in the package parc_msgs.
/**
  * Published by the team on /parc/finish to end the run early, e.g. after
  * skipping a tag. Not needed if all four tags are reported: the referee ends
  * the run automatically after the fourth report.
  * QoS: reliable, depth 10.
 */
typedef struct parc_msgs__msg__Finish
{
  builtin_interfaces__msg__Time stamp;
  uint8_t reason;
} parc_msgs__msg__Finish;

// Struct for a sequence of parc_msgs__msg__Finish.
typedef struct parc_msgs__msg__Finish__Sequence
{
  parc_msgs__msg__Finish * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} parc_msgs__msg__Finish__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // PARC_MSGS__MSG__DETAIL__FINISH__STRUCT_H_
