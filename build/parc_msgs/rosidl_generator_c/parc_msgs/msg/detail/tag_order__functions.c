// generated from rosidl_generator_c/resource/idl__functions.c.em
// with input from parc_msgs:msg/TagOrder.idl
// generated code does not contain a copyright notice
#include "parc_msgs/msg/detail/tag_order__functions.h"

#include <assert.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>

#include "rcutils/allocator.h"


// Include directives for member types
// Member `stamp`
#include "builtin_interfaces/msg/detail/time__functions.h"
// Member `tag_ids`
#include "rosidl_runtime_c/primitives_sequence_functions.h"

bool
parc_msgs__msg__TagOrder__init(parc_msgs__msg__TagOrder * msg)
{
  if (!msg) {
    return false;
  }
  // stamp
  if (!builtin_interfaces__msg__Time__init(&msg->stamp)) {
    parc_msgs__msg__TagOrder__fini(msg);
    return false;
  }
  // tag_ids
  if (!rosidl_runtime_c__uint8__Sequence__init(&msg->tag_ids, 0)) {
    parc_msgs__msg__TagOrder__fini(msg);
    return false;
  }
  return true;
}

void
parc_msgs__msg__TagOrder__fini(parc_msgs__msg__TagOrder * msg)
{
  if (!msg) {
    return;
  }
  // stamp
  builtin_interfaces__msg__Time__fini(&msg->stamp);
  // tag_ids
  rosidl_runtime_c__uint8__Sequence__fini(&msg->tag_ids);
}

bool
parc_msgs__msg__TagOrder__are_equal(const parc_msgs__msg__TagOrder * lhs, const parc_msgs__msg__TagOrder * rhs)
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
  // tag_ids
  if (!rosidl_runtime_c__uint8__Sequence__are_equal(
      &(lhs->tag_ids), &(rhs->tag_ids)))
  {
    return false;
  }
  return true;
}

bool
parc_msgs__msg__TagOrder__copy(
  const parc_msgs__msg__TagOrder * input,
  parc_msgs__msg__TagOrder * output)
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
  // tag_ids
  if (!rosidl_runtime_c__uint8__Sequence__copy(
      &(input->tag_ids), &(output->tag_ids)))
  {
    return false;
  }
  return true;
}

parc_msgs__msg__TagOrder *
parc_msgs__msg__TagOrder__create(void)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  parc_msgs__msg__TagOrder * msg = (parc_msgs__msg__TagOrder *)allocator.allocate(sizeof(parc_msgs__msg__TagOrder), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(parc_msgs__msg__TagOrder));
  bool success = parc_msgs__msg__TagOrder__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
parc_msgs__msg__TagOrder__destroy(parc_msgs__msg__TagOrder * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    parc_msgs__msg__TagOrder__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
parc_msgs__msg__TagOrder__Sequence__init(parc_msgs__msg__TagOrder__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  parc_msgs__msg__TagOrder * data = NULL;

  if (size) {
    data = (parc_msgs__msg__TagOrder *)allocator.zero_allocate(size, sizeof(parc_msgs__msg__TagOrder), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = parc_msgs__msg__TagOrder__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        parc_msgs__msg__TagOrder__fini(&data[i - 1]);
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
parc_msgs__msg__TagOrder__Sequence__fini(parc_msgs__msg__TagOrder__Sequence * array)
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
      parc_msgs__msg__TagOrder__fini(&array->data[i]);
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

parc_msgs__msg__TagOrder__Sequence *
parc_msgs__msg__TagOrder__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  parc_msgs__msg__TagOrder__Sequence * array = (parc_msgs__msg__TagOrder__Sequence *)allocator.allocate(sizeof(parc_msgs__msg__TagOrder__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = parc_msgs__msg__TagOrder__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
parc_msgs__msg__TagOrder__Sequence__destroy(parc_msgs__msg__TagOrder__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    parc_msgs__msg__TagOrder__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
parc_msgs__msg__TagOrder__Sequence__are_equal(const parc_msgs__msg__TagOrder__Sequence * lhs, const parc_msgs__msg__TagOrder__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!parc_msgs__msg__TagOrder__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
parc_msgs__msg__TagOrder__Sequence__copy(
  const parc_msgs__msg__TagOrder__Sequence * input,
  parc_msgs__msg__TagOrder__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    const size_t allocation_size =
      input->size * sizeof(parc_msgs__msg__TagOrder);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    parc_msgs__msg__TagOrder * data =
      (parc_msgs__msg__TagOrder *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!parc_msgs__msg__TagOrder__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          parc_msgs__msg__TagOrder__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!parc_msgs__msg__TagOrder__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}
