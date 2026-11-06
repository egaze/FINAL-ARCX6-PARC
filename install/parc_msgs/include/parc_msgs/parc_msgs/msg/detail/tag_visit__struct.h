// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from parc_msgs:msg/TagVisit.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "parc_msgs/msg/tag_visit.h"


#ifndef PARC_MSGS__MSG__DETAIL__TAG_VISIT__STRUCT_H_
#define PARC_MSGS__MSG__DETAIL__TAG_VISIT__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

// Constants defined in the message

// Include directives for member types
// Member 'header'
#include "std_msgs/msg/detail/header__struct.h"
// Member 'image'
#include "sensor_msgs/msg/detail/compressed_image__struct.h"

/// Struct defined in msg/TagVisit in the package parc_msgs.
/**
  * Published once by the team on /parc/tag_visit at each tag, while the robot is
  * stopped in the visit pose (0.5 m from the tag, facing it within +-12 degrees).
  * After publishing, the robot must hold the pose for at least 3 seconds.
  * QoS: reliable, depth 10.
 */
typedef struct parc_msgs__msg__TagVisit
{
  /// header.stamp: the moment of the visit. header.frame_id: the camera frame used.
  std_msgs__msg__Header header;
  /// AprilTag 36h11 ID of the tag being visited (1, 4, 7 or 9).
  uint8_t tag_id;
  /// JPEG image from a robot camera in which the tag is clearly visible.
  sensor_msgs__msg__CompressedImage image;
} parc_msgs__msg__TagVisit;

// Struct for a sequence of parc_msgs__msg__TagVisit.
typedef struct parc_msgs__msg__TagVisit__Sequence
{
  parc_msgs__msg__TagVisit * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} parc_msgs__msg__TagVisit__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // PARC_MSGS__MSG__DETAIL__TAG_VISIT__STRUCT_H_
