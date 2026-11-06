// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from parc_msgs:msg/TagOrder.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "parc_msgs/msg/tag_order.h"


#ifndef PARC_MSGS__MSG__DETAIL__TAG_ORDER__STRUCT_H_
#define PARC_MSGS__MSG__DETAIL__TAG_ORDER__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

// Constants defined in the message

// Include directives for member types
// Member 'stamp'
#include "builtin_interfaces/msg/detail/time__struct.h"
// Member 'tag_ids'
#include "rosidl_runtime_c/primitives_sequence.h"

/// Struct defined in msg/TagOrder in the package parc_msgs.
/**
  * Published by the referee on /parc/tag_order when the judge arms the run.
  * QoS: reliable, transient local, depth 1 (late subscribers still receive it).
 */
typedef struct parc_msgs__msg__TagOrder
{
  builtin_interfaces__msg__Time stamp;
  /// The order in which the tags must be visited, e.g. [7, 1, 9, 4].
  rosidl_runtime_c__uint8__Sequence tag_ids;
} parc_msgs__msg__TagOrder;

// Struct for a sequence of parc_msgs__msg__TagOrder.
typedef struct parc_msgs__msg__TagOrder__Sequence
{
  parc_msgs__msg__TagOrder * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} parc_msgs__msg__TagOrder__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // PARC_MSGS__MSG__DETAIL__TAG_ORDER__STRUCT_H_
