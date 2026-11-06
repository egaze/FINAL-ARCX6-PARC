// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from parc_msgs:msg/RunStatus.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "parc_msgs/msg/run_status.h"


#ifndef PARC_MSGS__MSG__DETAIL__RUN_STATUS__STRUCT_H_
#define PARC_MSGS__MSG__DETAIL__RUN_STATUS__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

// Constants defined in the message

/// Constant 'IDLE'.
/**
  * no run in progress
 */
enum
{
  parc_msgs__msg__RunStatus__IDLE = 0
};

/// Constant 'ARMED'.
/**
  * order published, waiting for /parc/start
 */
enum
{
  parc_msgs__msg__RunStatus__ARMED = 1
};

/// Constant 'RUNNING'.
/**
  * clock running
 */
enum
{
  parc_msgs__msg__RunStatus__RUNNING = 2
};

/// Constant 'FINISHED'.
/**
  * fourth tag reported or /parc/finish received
 */
enum
{
  parc_msgs__msg__RunStatus__FINISHED = 3
};

/// Constant 'TIMED_OUT'.
/**
  * time limit reached
 */
enum
{
  parc_msgs__msg__RunStatus__TIMED_OUT = 4
};

/// Constant 'TERMINATED'.
/**
  * ended by a judge (safety stop, contact with a person, loss of control)
 */
enum
{
  parc_msgs__msg__RunStatus__TERMINATED = 5
};

// Include directives for member types
// Member 'stamp'
#include "builtin_interfaces/msg/detail/time__struct.h"
// Member 'tag_order'
// Member 'tags_reported'
#include "rosidl_runtime_c/primitives_sequence.h"

/// Struct defined in msg/RunStatus in the package parc_msgs.
/**
  * Published by the referee on /parc/run_status at 2 Hz and on every change.
  * QoS: reliable, transient local, depth 1.
  * Teams can use it to confirm their start and visits were received, and should
  * stop the robot when the state is FINISHED, TIMED_OUT or TERMINATED.
 */
typedef struct parc_msgs__msg__RunStatus
{
  builtin_interfaces__msg__Time stamp;
  uint8_t state;
  /// seconds since the start signal
  float elapsed_s;
  /// 600
  float time_limit_s;
  /// same as /parc/tag_order
  rosidl_runtime_c__uint8__Sequence tag_order;
  /// tag IDs reported, in the order received (the judges' verdict is separate)
  rosidl_runtime_c__uint8__Sequence tags_reported;
  /// StartSignal.METHOD_*, valid once RUNNING
  uint8_t start_method;
  /// robot moved before the start signal
  bool false_start;
} parc_msgs__msg__RunStatus;

// Struct for a sequence of parc_msgs__msg__RunStatus.
typedef struct parc_msgs__msg__RunStatus__Sequence
{
  parc_msgs__msg__RunStatus * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} parc_msgs__msg__RunStatus__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // PARC_MSGS__MSG__DETAIL__RUN_STATUS__STRUCT_H_
