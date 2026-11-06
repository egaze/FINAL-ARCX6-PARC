// generated from rosidl_generator_c/resource/idl__description.c.em
// with input from parc_msgs:msg/Finish.idl
// generated code does not contain a copyright notice

#include "parc_msgs/msg/detail/finish__functions.h"

ROSIDL_GENERATOR_C_PUBLIC_parc_msgs
const rosidl_type_hash_t *
parc_msgs__msg__Finish__get_type_hash(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_type_hash_t hash = {1, {
      0x63, 0xb3, 0x20, 0x98, 0xc6, 0xbb, 0x50, 0x50,
      0x8f, 0x5d, 0x6f, 0x45, 0x18, 0x42, 0xfb, 0xe1,
      0xf5, 0x15, 0xcf, 0x9e, 0x60, 0x71, 0x30, 0xe1,
      0xa0, 0xaa, 0xcd, 0xcc, 0x05, 0x58, 0x52, 0x08,
    }};
  return &hash;
}

#include <assert.h>
#include <string.h>

// Include directives for referenced types
#include "builtin_interfaces/msg/detail/time__functions.h"

// Hashes for external referenced types
#ifndef NDEBUG
static const rosidl_type_hash_t builtin_interfaces__msg__Time__EXPECTED_HASH = {1, {
    0xb1, 0x06, 0x23, 0x5e, 0x25, 0xa4, 0xc5, 0xed,
    0x35, 0x09, 0x8a, 0xa0, 0xa6, 0x1a, 0x3e, 0xe9,
    0xc9, 0xb1, 0x8d, 0x19, 0x7f, 0x39, 0x8b, 0x0e,
    0x42, 0x06, 0xce, 0xa9, 0xac, 0xf9, 0xc1, 0x97,
  }};
#endif

static char parc_msgs__msg__Finish__TYPE_NAME[] = "parc_msgs/msg/Finish";
static char builtin_interfaces__msg__Time__TYPE_NAME[] = "builtin_interfaces/msg/Time";

// Define type names, field names, and default values
static char parc_msgs__msg__Finish__FIELD_NAME__stamp[] = "stamp";
static char parc_msgs__msg__Finish__FIELD_NAME__reason[] = "reason";

static rosidl_runtime_c__type_description__Field parc_msgs__msg__Finish__FIELDS[] = {
  {
    {parc_msgs__msg__Finish__FIELD_NAME__stamp, 5, 5},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_NESTED_TYPE,
      0,
      0,
      {builtin_interfaces__msg__Time__TYPE_NAME, 27, 27},
    },
    {NULL, 0, 0},
  },
  {
    {parc_msgs__msg__Finish__FIELD_NAME__reason, 6, 6},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_UINT8,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
};

static rosidl_runtime_c__type_description__IndividualTypeDescription parc_msgs__msg__Finish__REFERENCED_TYPE_DESCRIPTIONS[] = {
  {
    {builtin_interfaces__msg__Time__TYPE_NAME, 27, 27},
    {NULL, 0, 0},
  },
};

const rosidl_runtime_c__type_description__TypeDescription *
parc_msgs__msg__Finish__get_type_description(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static bool constructed = false;
  static const rosidl_runtime_c__type_description__TypeDescription description = {
    {
      {parc_msgs__msg__Finish__TYPE_NAME, 20, 20},
      {parc_msgs__msg__Finish__FIELDS, 2, 2},
    },
    {parc_msgs__msg__Finish__REFERENCED_TYPE_DESCRIPTIONS, 1, 1},
  };
  if (!constructed) {
    assert(0 == memcmp(&builtin_interfaces__msg__Time__EXPECTED_HASH, builtin_interfaces__msg__Time__get_type_hash(NULL), sizeof(rosidl_type_hash_t)));
    description.referenced_type_descriptions.data[0].fields = builtin_interfaces__msg__Time__get_type_description(NULL)->type_description.fields;
    constructed = true;
  }
  return &description;
}

static char toplevel_type_raw_source[] =
  "# Published by the team on /parc/finish to end the run early, e.g. after\n"
  "# skipping a tag. Not needed if all four tags are reported: the referee ends\n"
  "# the run automatically after the fourth report.\n"
  "# QoS: reliable, depth 10.\n"
  "\n"
  "builtin_interfaces/Time stamp\n"
  "\n"
  "uint8 REASON_COMPLETED = 0   # the robot has done everything it is going to do\n"
  "uint8 REASON_GAVE_UP   = 1   # the robot cannot continue\n"
  "uint8 reason";

static char msg_encoding[] = "msg";

// Define all individual source functions

const rosidl_runtime_c__type_description__TypeSource *
parc_msgs__msg__Finish__get_individual_type_description_source(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static const rosidl_runtime_c__type_description__TypeSource source = {
    {parc_msgs__msg__Finish__TYPE_NAME, 20, 20},
    {msg_encoding, 3, 3},
    {toplevel_type_raw_source, 407, 407},
  };
  return &source;
}

const rosidl_runtime_c__type_description__TypeSource__Sequence *
parc_msgs__msg__Finish__get_type_description_sources(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_runtime_c__type_description__TypeSource sources[2];
  static const rosidl_runtime_c__type_description__TypeSource__Sequence source_sequence = {sources, 2, 2};
  static bool constructed = false;
  if (!constructed) {
    sources[0] = *parc_msgs__msg__Finish__get_individual_type_description_source(NULL),
    sources[1] = *builtin_interfaces__msg__Time__get_individual_type_description_source(NULL);
    constructed = true;
  }
  return &source_sequence;
}
