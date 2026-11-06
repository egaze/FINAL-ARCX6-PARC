// generated from rosidl_generator_c/resource/idl__functions.h.em
// with input from parc_msgs:msg/RunStatus.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "parc_msgs/msg/run_status.h"


#ifndef PARC_MSGS__MSG__DETAIL__RUN_STATUS__FUNCTIONS_H_
#define PARC_MSGS__MSG__DETAIL__RUN_STATUS__FUNCTIONS_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stdlib.h>

#include "rosidl_runtime_c/action_type_support_struct.h"
#include "rosidl_runtime_c/message_type_support_struct.h"
#include "rosidl_runtime_c/service_type_support_struct.h"
#include "rosidl_runtime_c/type_description/type_description__struct.h"
#include "rosidl_runtime_c/type_description/type_source__struct.h"
#include "rosidl_runtime_c/type_hash.h"
#include "rosidl_runtime_c/visibility_control.h"
#include "parc_msgs/msg/rosidl_generator_c__visibility_control.h"

#include "parc_msgs/msg/detail/run_status__struct.h"

/// Initialize msg/RunStatus message.
/**
 * If the init function is called twice for the same message without
 * calling fini inbetween previously allocated memory will be leaked.
 * \param[in,out] msg The previously allocated message pointer.
 * Fields without a default value will not be initialized by this function.
 * You might want to call memset(msg, 0, sizeof(
 * parc_msgs__msg__RunStatus
 * )) before or use
 * parc_msgs__msg__RunStatus__create()
 * to allocate and initialize the message.
 * \return true if initialization was successful, otherwise false
 */
ROSIDL_GENERATOR_C_PUBLIC_parc_msgs
bool
parc_msgs__msg__RunStatus__init(parc_msgs__msg__RunStatus * msg);

/// Finalize msg/RunStatus message.
/**
 * \param[in,out] msg The allocated message pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_parc_msgs
void
parc_msgs__msg__RunStatus__fini(parc_msgs__msg__RunStatus * msg);

/// Create msg/RunStatus message.
/**
 * It allocates the memory for the message, sets the memory to zero, and
 * calls
 * parc_msgs__msg__RunStatus__init().
 * \return The pointer to the initialized message if successful,
 * otherwise NULL
 */
ROSIDL_GENERATOR_C_PUBLIC_parc_msgs
parc_msgs__msg__RunStatus *
parc_msgs__msg__RunStatus__create(void);

/// Destroy msg/RunStatus message.
/**
 * It calls
 * parc_msgs__msg__RunStatus__fini()
 * and frees the memory of the message.
 * \param[in,out] msg The allocated message pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_parc_msgs
void
parc_msgs__msg__RunStatus__destroy(parc_msgs__msg__RunStatus * msg);

/// Check for msg/RunStatus message equality.
/**
 * \param[in] lhs The message on the left hand size of the equality operator.
 * \param[in] rhs The message on the right hand size of the equality operator.
 * \return true if messages are equal, otherwise false.
 */
ROSIDL_GENERATOR_C_PUBLIC_parc_msgs
bool
parc_msgs__msg__RunStatus__are_equal(const parc_msgs__msg__RunStatus * lhs, const parc_msgs__msg__RunStatus * rhs);

/// Copy a msg/RunStatus message.
/**
 * This functions performs a deep copy, as opposed to the shallow copy that
 * plain assignment yields.
 *
 * \param[in] input The source message pointer.
 * \param[out] output The target message pointer, which must
 *   have been initialized before calling this function.
 * \return true if successful, or false if either pointer is null
 *   or memory allocation fails.
 */
ROSIDL_GENERATOR_C_PUBLIC_parc_msgs
bool
parc_msgs__msg__RunStatus__copy(
  const parc_msgs__msg__RunStatus * input,
  parc_msgs__msg__RunStatus * output);

/// Retrieve pointer to the hash of the description of this type.
ROSIDL_GENERATOR_C_PUBLIC_parc_msgs
const rosidl_type_hash_t *
parc_msgs__msg__RunStatus__get_type_hash(
  const rosidl_message_type_support_t * type_support);

/// Retrieve pointer to the description of this type.
ROSIDL_GENERATOR_C_PUBLIC_parc_msgs
const rosidl_runtime_c__type_description__TypeDescription *
parc_msgs__msg__RunStatus__get_type_description(
  const rosidl_message_type_support_t * type_support);

/// Retrieve pointer to the single raw source text that defined this type.
ROSIDL_GENERATOR_C_PUBLIC_parc_msgs
const rosidl_runtime_c__type_description__TypeSource *
parc_msgs__msg__RunStatus__get_individual_type_description_source(
  const rosidl_message_type_support_t * type_support);

/// Retrieve pointer to the recursive raw sources that defined the description of this type.
ROSIDL_GENERATOR_C_PUBLIC_parc_msgs
const rosidl_runtime_c__type_description__TypeSource__Sequence *
parc_msgs__msg__RunStatus__get_type_description_sources(
  const rosidl_message_type_support_t * type_support);

/// Initialize array of msg/RunStatus messages.
/**
 * It allocates the memory for the number of elements and calls
 * parc_msgs__msg__RunStatus__init()
 * for each element of the array.
 * \param[in,out] array The allocated array pointer.
 * \param[in] size The size / capacity of the array.
 * \return true if initialization was successful, otherwise false
 * If the array pointer is valid and the size is zero it is guaranteed
 # to return true.
 */
ROSIDL_GENERATOR_C_PUBLIC_parc_msgs
bool
parc_msgs__msg__RunStatus__Sequence__init(parc_msgs__msg__RunStatus__Sequence * array, size_t size);

/// Finalize array of msg/RunStatus messages.
/**
 * It calls
 * parc_msgs__msg__RunStatus__fini()
 * for each element of the array and frees the memory for the number of
 * elements.
 * \param[in,out] array The initialized array pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_parc_msgs
void
parc_msgs__msg__RunStatus__Sequence__fini(parc_msgs__msg__RunStatus__Sequence * array);

/// Create array of msg/RunStatus messages.
/**
 * It allocates the memory for the array and calls
 * parc_msgs__msg__RunStatus__Sequence__init().
 * \param[in] size The size / capacity of the array.
 * \return The pointer to the initialized array if successful, otherwise NULL
 */
ROSIDL_GENERATOR_C_PUBLIC_parc_msgs
parc_msgs__msg__RunStatus__Sequence *
parc_msgs__msg__RunStatus__Sequence__create(size_t size);

/// Destroy array of msg/RunStatus messages.
/**
 * It calls
 * parc_msgs__msg__RunStatus__Sequence__fini()
 * on the array,
 * and frees the memory of the array.
 * \param[in,out] array The initialized array pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_parc_msgs
void
parc_msgs__msg__RunStatus__Sequence__destroy(parc_msgs__msg__RunStatus__Sequence * array);

/// Check for msg/RunStatus message array equality.
/**
 * \param[in] lhs The message array on the left hand size of the equality operator.
 * \param[in] rhs The message array on the right hand size of the equality operator.
 * \return true if message arrays are equal in size and content, otherwise false.
 */
ROSIDL_GENERATOR_C_PUBLIC_parc_msgs
bool
parc_msgs__msg__RunStatus__Sequence__are_equal(const parc_msgs__msg__RunStatus__Sequence * lhs, const parc_msgs__msg__RunStatus__Sequence * rhs);

/// Copy an array of msg/RunStatus messages.
/**
 * This functions performs a deep copy, as opposed to the shallow copy that
 * plain assignment yields.
 *
 * \param[in] input The source array pointer.
 * \param[out] output The target array pointer, which must
 *   have been initialized before calling this function.
 * \return true if successful, or false if either pointer
 *   is null or memory allocation fails.
 */
ROSIDL_GENERATOR_C_PUBLIC_parc_msgs
bool
parc_msgs__msg__RunStatus__Sequence__copy(
  const parc_msgs__msg__RunStatus__Sequence * input,
  parc_msgs__msg__RunStatus__Sequence * output);

#ifdef __cplusplus
}
#endif

#endif  // PARC_MSGS__MSG__DETAIL__RUN_STATUS__FUNCTIONS_H_
