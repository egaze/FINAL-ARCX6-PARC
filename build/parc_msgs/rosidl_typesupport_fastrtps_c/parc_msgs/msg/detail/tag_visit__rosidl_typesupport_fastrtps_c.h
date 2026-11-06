// generated from rosidl_typesupport_fastrtps_c/resource/idl__rosidl_typesupport_fastrtps_c.h.em
// with input from parc_msgs:msg/TagVisit.idl
// generated code does not contain a copyright notice
#ifndef PARC_MSGS__MSG__DETAIL__TAG_VISIT__ROSIDL_TYPESUPPORT_FASTRTPS_C_H_
#define PARC_MSGS__MSG__DETAIL__TAG_VISIT__ROSIDL_TYPESUPPORT_FASTRTPS_C_H_


#include <stddef.h>
#include "rosidl_runtime_c/message_type_support_struct.h"
#include "rosidl_typesupport_interface/macros.h"
#include "parc_msgs/msg/rosidl_typesupport_fastrtps_c__visibility_control.h"
#include "parc_msgs/msg/detail/tag_visit__struct.h"
#include "fastcdr/Cdr.h"

#ifdef __cplusplus
extern "C"
{
#endif

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_parc_msgs
bool cdr_serialize_parc_msgs__msg__TagVisit(
  const parc_msgs__msg__TagVisit * ros_message,
  eprosima::fastcdr::Cdr & cdr);

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_parc_msgs
bool cdr_deserialize_parc_msgs__msg__TagVisit(
  eprosima::fastcdr::Cdr &,
  parc_msgs__msg__TagVisit * ros_message);

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_parc_msgs
size_t get_serialized_size_parc_msgs__msg__TagVisit(
  const void * untyped_ros_message,
  size_t current_alignment);

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_parc_msgs
size_t max_serialized_size_parc_msgs__msg__TagVisit(
  bool & full_bounded,
  bool & is_plain,
  size_t current_alignment);

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_parc_msgs
bool cdr_serialize_key_parc_msgs__msg__TagVisit(
  const parc_msgs__msg__TagVisit * ros_message,
  eprosima::fastcdr::Cdr & cdr);

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_parc_msgs
size_t get_serialized_size_key_parc_msgs__msg__TagVisit(
  const void * untyped_ros_message,
  size_t current_alignment);

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_parc_msgs
size_t max_serialized_size_key_parc_msgs__msg__TagVisit(
  bool & full_bounded,
  bool & is_plain,
  size_t current_alignment);

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_parc_msgs
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_fastrtps_c, parc_msgs, msg, TagVisit)();

#ifdef __cplusplus
}
#endif

#endif  // PARC_MSGS__MSG__DETAIL__TAG_VISIT__ROSIDL_TYPESUPPORT_FASTRTPS_C_H_
