// generated from rosidl_generator_c/resource/idl__functions.c.em
// with input from parc_msgs:msg/Finish.idl
// generated code does not contain a copyright notice
#include "parc_msgs/msg/detail/finish__functions.h"

#include <assert.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>

#include "rcutils/allocator.h"


// Include directives for member types
// Member `stamp`
#include "builtin_interfaces/msg/detail/time__functions.h"

bool
parc_msgs__msg__Finish__init(parc_msgs__msg__Finish * msg)
{
  if (!msg) {
    return false;
  }
  // stamp
  if (!builtin_interfaces__msg__Time__init(&msg->stamp)) {
    parc_msgs__msg__Finish__fini(msg);
    return false;
  }
  // reason
  return true;
}

void
parc_msgs__msg__Finish__fini(parc_msgs__msg__Finish * msg)
{
  if (!msg) {
    return;
  }
  // stamp
  builtin_interfaces__msg__Time__fini(&msg->stamp);
  // reason
}

bool
parc_msgs__msg__Finish__are_equal(const parc_msgs__msg__Finish * lhs, const parc_msgs__msg__Finish * rhs)
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
  // reason
  if (lhs->reason != rhs->reason) {
    return false;
  }
  return true;
}

bool
parc_msgs__msg__Finish__copy(
  const parc_msgs__msg__Finish * input,
  parc_msgs__msg__Finish * output)
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
  // reason
  output->reason = input->reason;
  return true;
}

parc_msgs__msg__Finish *
parc_msgs__msg__Finish__create(void)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  parc_msgs__msg__Finish * msg = (parc_msgs__msg__Finish *)allocator.allocate(sizeof(parc_msgs__msg__Finish), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(parc_msgs__msg__Finish));
  bool success = parc_msgs__msg__Finish__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
parc_msgs__msg__Finish__destroy(parc_msgs__msg__Finish * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    parc_msgs__msg__Finish__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
parc_msgs__msg__Finish__Sequence__init(parc_msgs__msg__Finish__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  parc_msgs__msg__Finish * data = NULL;

  if (size) {
    data = (parc_msgs__msg__Finish *)allocator.zero_allocate(size, sizeof(parc_msgs__msg__Finish), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = parc_msgs__msg__Finish__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        parc_msgs__msg__Finish__fini(&data[i - 1]);
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
parc_msgs__msg__Finish__Sequence__fini(parc_msgs__msg__Finish__Sequence * array)
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
      parc_msgs__msg__Finish__fini(&array->data[i]);
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

parc_msgs__msg__Finish__Sequence *
parc_msgs__msg__Finish__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  parc_msgs__msg__Finish__Sequence * array = (parc_msgs__msg__Finish__Sequence *)allocator.allocate(sizeof(parc_msgs__msg__Finish__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = parc_msgs__msg__Finish__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
parc_msgs__msg__Finish__Sequence__destroy(parc_msgs__msg__Finish__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    parc_msgs__msg__Finish__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
parc_msgs__msg__Finish__Sequence__are_equal(const parc_msgs__msg__Finish__Sequence * lhs, const parc_msgs__msg__Finish__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!parc_msgs__msg__Finish__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
parc_msgs__msg__Finish__Sequence__copy(
  const parc_msgs__msg__Finish__Sequence * input,
  parc_msgs__msg__Finish__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    const size_t allocation_size =
      input->size * sizeof(parc_msgs__msg__Finish);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    parc_msgs__msg__Finish * data =
      (parc_msgs__msg__Finish *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!parc_msgs__msg__Finish__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          parc_msgs__msg__Finish__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!parc_msgs__msg__Finish__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}
