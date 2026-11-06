// generated from rosidl_generator_c/resource/idl__functions.c.em
// with input from parc_msgs:msg/TagVisit.idl
// generated code does not contain a copyright notice
#include "parc_msgs/msg/detail/tag_visit__functions.h"

#include <assert.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>

#include "rcutils/allocator.h"


// Include directives for member types
// Member `header`
#include "std_msgs/msg/detail/header__functions.h"
// Member `image`
#include "sensor_msgs/msg/detail/compressed_image__functions.h"

bool
parc_msgs__msg__TagVisit__init(parc_msgs__msg__TagVisit * msg)
{
  if (!msg) {
    return false;
  }
  // header
  if (!std_msgs__msg__Header__init(&msg->header)) {
    parc_msgs__msg__TagVisit__fini(msg);
    return false;
  }
  // tag_id
  // image
  if (!sensor_msgs__msg__CompressedImage__init(&msg->image)) {
    parc_msgs__msg__TagVisit__fini(msg);
    return false;
  }
  return true;
}

void
parc_msgs__msg__TagVisit__fini(parc_msgs__msg__TagVisit * msg)
{
  if (!msg) {
    return;
  }
  // header
  std_msgs__msg__Header__fini(&msg->header);
  // tag_id
  // image
  sensor_msgs__msg__CompressedImage__fini(&msg->image);
}

bool
parc_msgs__msg__TagVisit__are_equal(const parc_msgs__msg__TagVisit * lhs, const parc_msgs__msg__TagVisit * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  // header
  if (!std_msgs__msg__Header__are_equal(
      &(lhs->header), &(rhs->header)))
  {
    return false;
  }
  // tag_id
  if (lhs->tag_id != rhs->tag_id) {
    return false;
  }
  // image
  if (!sensor_msgs__msg__CompressedImage__are_equal(
      &(lhs->image), &(rhs->image)))
  {
    return false;
  }
  return true;
}

bool
parc_msgs__msg__TagVisit__copy(
  const parc_msgs__msg__TagVisit * input,
  parc_msgs__msg__TagVisit * output)
{
  if (!input || !output) {
    return false;
  }
  // header
  if (!std_msgs__msg__Header__copy(
      &(input->header), &(output->header)))
  {
    return false;
  }
  // tag_id
  output->tag_id = input->tag_id;
  // image
  if (!sensor_msgs__msg__CompressedImage__copy(
      &(input->image), &(output->image)))
  {
    return false;
  }
  return true;
}

parc_msgs__msg__TagVisit *
parc_msgs__msg__TagVisit__create(void)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  parc_msgs__msg__TagVisit * msg = (parc_msgs__msg__TagVisit *)allocator.allocate(sizeof(parc_msgs__msg__TagVisit), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(parc_msgs__msg__TagVisit));
  bool success = parc_msgs__msg__TagVisit__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
parc_msgs__msg__TagVisit__destroy(parc_msgs__msg__TagVisit * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    parc_msgs__msg__TagVisit__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
parc_msgs__msg__TagVisit__Sequence__init(parc_msgs__msg__TagVisit__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  parc_msgs__msg__TagVisit * data = NULL;

  if (size) {
    data = (parc_msgs__msg__TagVisit *)allocator.zero_allocate(size, sizeof(parc_msgs__msg__TagVisit), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = parc_msgs__msg__TagVisit__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        parc_msgs__msg__TagVisit__fini(&data[i - 1]);
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
parc_msgs__msg__TagVisit__Sequence__fini(parc_msgs__msg__TagVisit__Sequence * array)
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
      parc_msgs__msg__TagVisit__fini(&array->data[i]);
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

parc_msgs__msg__TagVisit__Sequence *
parc_msgs__msg__TagVisit__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  parc_msgs__msg__TagVisit__Sequence * array = (parc_msgs__msg__TagVisit__Sequence *)allocator.allocate(sizeof(parc_msgs__msg__TagVisit__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = parc_msgs__msg__TagVisit__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
parc_msgs__msg__TagVisit__Sequence__destroy(parc_msgs__msg__TagVisit__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    parc_msgs__msg__TagVisit__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
parc_msgs__msg__TagVisit__Sequence__are_equal(const parc_msgs__msg__TagVisit__Sequence * lhs, const parc_msgs__msg__TagVisit__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!parc_msgs__msg__TagVisit__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
parc_msgs__msg__TagVisit__Sequence__copy(
  const parc_msgs__msg__TagVisit__Sequence * input,
  parc_msgs__msg__TagVisit__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    const size_t allocation_size =
      input->size * sizeof(parc_msgs__msg__TagVisit);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    parc_msgs__msg__TagVisit * data =
      (parc_msgs__msg__TagVisit *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!parc_msgs__msg__TagVisit__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          parc_msgs__msg__TagVisit__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!parc_msgs__msg__TagVisit__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}
