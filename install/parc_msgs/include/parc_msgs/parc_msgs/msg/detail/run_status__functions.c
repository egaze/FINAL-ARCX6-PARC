// generated from rosidl_generator_c/resource/idl__functions.c.em
// with input from parc_msgs:msg/RunStatus.idl
// generated code does not contain a copyright notice
#include "parc_msgs/msg/detail/run_status__functions.h"

#include <assert.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>

#include "rcutils/allocator.h"


// Include directives for member types
// Member `stamp`
#include "builtin_interfaces/msg/detail/time__functions.h"
// Member `tag_order`
// Member `tags_reported`
#include "rosidl_runtime_c/primitives_sequence_functions.h"

bool
parc_msgs__msg__RunStatus__init(parc_msgs__msg__RunStatus * msg)
{
  if (!msg) {
    return false;
  }
  // stamp
  if (!builtin_interfaces__msg__Time__init(&msg->stamp)) {
    parc_msgs__msg__RunStatus__fini(msg);
    return false;
  }
  // state
  // elapsed_s
  // time_limit_s
  // tag_order
  if (!rosidl_runtime_c__uint8__Sequence__init(&msg->tag_order, 0)) {
    parc_msgs__msg__RunStatus__fini(msg);
    return false;
  }
  // tags_reported
  if (!rosidl_runtime_c__uint8__Sequence__init(&msg->tags_reported, 0)) {
    parc_msgs__msg__RunStatus__fini(msg);
    return false;
  }
  // start_method
  // false_start
  return true;
}

void
parc_msgs__msg__RunStatus__fini(parc_msgs__msg__RunStatus * msg)
{
  if (!msg) {
    return;
  }
  // stamp
  builtin_interfaces__msg__Time__fini(&msg->stamp);
  // state
  // elapsed_s
  // time_limit_s
  // tag_order
  rosidl_runtime_c__uint8__Sequence__fini(&msg->tag_order);
  // tags_reported
  rosidl_runtime_c__uint8__Sequence__fini(&msg->tags_reported);
  // start_method
  // false_start
}

bool
parc_msgs__msg__RunStatus__are_equal(const parc_msgs__msg__RunStatus * lhs, const parc_msgs__msg__RunStatus * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  // stamp
  if (!builtin_interfaces__msg__Time__are_equal(
      &(lhs->stamp), &(rhs->stamp)))
  {
    return false;
  }
  // state
  if (lhs->state != rhs->state) {
    return false;
  }
  // elapsed_s
  if (lhs->elapsed_s != rhs->elapsed_s) {
    return false;
  }
  // time_limit_s
  if (lhs->time_limit_s != rhs->time_limit_s) {
    return false;
  }
  // tag_order
  if (!rosidl_runtime_c__uint8__Sequence__are_equal(
      &(lhs->tag_order), &(rhs->tag_order)))
  {
    return false;
  }
  // tags_reported
  if (!rosidl_runtime_c__uint8__Sequence__are_equal(
      &(lhs->tags_reported), &(rhs->tags_reported)))
  {
    return false;
  }
  // start_method
  if (lhs->start_method != rhs->start_method) {
    return false;
  }
  // false_start
  if (lhs->false_start != rhs->false_start) {
    return false;
  }
  return true;
}

bool
parc_msgs__msg__RunStatus__copy(
  const parc_msgs__msg__RunStatus * input,
  parc_msgs__msg__RunStatus * output)
{
  if (!input || !output) {
    return false;
  }
  // stamp
  if (!builtin_interfaces__msg__Time__copy(
      &(input->stamp), &(output->stamp)))
  {
    return false;
  }
  // state
  output->state = input->state;
  // elapsed_s
  output->elapsed_s = input->elapsed_s;
  // time_limit_s
  output->time_limit_s = input->time_limit_s;
  // tag_order
  if (!rosidl_runtime_c__uint8__Sequence__copy(
      &(input->tag_order), &(output->tag_order)))
  {
    return false;
  }
  // tags_reported
  if (!rosidl_runtime_c__uint8__Sequence__copy(
      &(input->tags_reported), &(output->tags_reported)))
  {
    return false;
  }
  // start_method
  output->start_method = input->start_method;
  // false_start
  output->false_start = input->false_start;
  return true;
}

parc_msgs__msg__RunStatus *
parc_msgs__msg__RunStatus__create(void)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  parc_msgs__msg__RunStatus * msg = (parc_msgs__msg__RunStatus *)allocator.allocate(sizeof(parc_msgs__msg__RunStatus), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(parc_msgs__msg__RunStatus));
  bool success = parc_msgs__msg__RunStatus__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
parc_msgs__msg__RunStatus__destroy(parc_msgs__msg__RunStatus * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    parc_msgs__msg__RunStatus__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
parc_msgs__msg__RunStatus__Sequence__init(parc_msgs__msg__RunStatus__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  parc_msgs__msg__RunStatus * data = NULL;

  if (size) {
    data = (parc_msgs__msg__RunStatus *)allocator.zero_allocate(size, sizeof(parc_msgs__msg__RunStatus), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = parc_msgs__msg__RunStatus__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        parc_msgs__msg__RunStatus__fini(&data[i - 1]);
      }
      allocator.deallocate(data, allocator.state);
      return false;
    }
  }
  array->data = data;
  array->size = size;
  array->capacity = size;
  return true;
}

void
parc_msgs__msg__RunStatus__Sequence__fini(parc_msgs__msg__RunStatus__Sequence * array)
{
  if (!array) {
    return;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();

  if (array->data) {
    // ensure that data and capacity values are consistent
    assert(array->capacity > 0);
    // finalize all array elements
    for (size_t i = 0; i < array->capacity; ++i) {
      parc_msgs__msg__RunStatus__fini(&array->data[i]);
    }
    allocator.deallocate(array->data, allocator.state);
    array->data = NULL;
    array->size = 0;
    array->capacity = 0;
  } else {
    // ensure that data, size, and capacity values are consistent
    assert(0 == array->size);
    assert(0 == array->capacity);
  }
}

parc_msgs__msg__RunStatus__Sequence *
parc_msgs__msg__RunStatus__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  parc_msgs__msg__RunStatus__Sequence * array = (parc_msgs__msg__RunStatus__Sequence *)allocator.allocate(sizeof(parc_msgs__msg__RunStatus__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = parc_msgs__msg__RunStatus__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
parc_msgs__msg__RunStatus__Sequence__destroy(parc_msgs__msg__RunStatus__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    parc_msgs__msg__RunStatus__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
parc_msgs__msg__RunStatus__Sequence__are_equal(const parc_msgs__msg__RunStatus__Sequence * lhs, const parc_msgs__msg__RunStatus__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!parc_msgs__msg__RunStatus__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
parc_msgs__msg__RunStatus__Sequence__copy(
  const parc_msgs__msg__RunStatus__Sequence * input,
  parc_msgs__msg__RunStatus__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    const size_t allocation_size =
      input->size * sizeof(parc_msgs__msg__RunStatus);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    parc_msgs__msg__RunStatus * data =
      (parc_msgs__msg__RunStatus *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!parc_msgs__msg__RunStatus__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          parc_msgs__msg__RunStatus__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!parc_msgs__msg__RunStatus__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}
