// generated from rosidl_generator_c/resource/idl__description.c.em
// with input from parc_msgs:msg/StartSignal.idl
// generated code does not contain a copyright notice

#include "parc_msgs/msg/detail/start_signal__functions.h"

ROSIDL_GENERATOR_C_PUBLIC_parc_msgs
const rosidl_type_hash_t *
parc_msgs__msg__StartSignal__get_type_hash(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_type_hash_t hash = {1, {
      0xef, 0x91, 0x29, 0x8b, 0xf4, 0xd0, 0x2d, 0x22,
      0xa0, 0xe4, 0x44, 0xa2, 0x49, 0xe1, 0x72, 0x3d,
      0xd3, 0x27, 0x0a, 0xbb, 0x9e, 0x20, 0x0b, 0x96,
      0x44, 0x3e, 0xba, 0xf5, 0xaa, 0x8e, 0x29, 0x35,
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

static char parc_msgs__msg__StartSignal__TYPE_NAME[] = "parc_msgs/msg/StartSignal";
static char builtin_interfaces__msg__Time__TYPE_NAME[] = "builtin_interfaces/msg/Time";

// Define type names, field names, and default values
static char parc_msgs__msg__StartSignal__FIELD_NAME__stamp[] = "stamp";
static char parc_msgs__msg__StartSignal__FIELD_NAME__method[] = "method";
static char parc_msgs__msg__StartSignal__FIELD_NAME__heard[] = "heard";

static rosidl_runtime_c__type_description__Field parc_msgs__msg__StartSignal__FIELDS[] = {
  {
    {parc_msgs__msg__StartSignal__FIELD_NAME__stamp, 5, 5},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_NESTED_TYPE,
      0,
      0,
      {builtin_interfaces__msg__Time__TYPE_NAME, 27, 27},
    },
    {NULL, 0, 0},
  },
  {
    {parc_msgs__msg__StartSignal__FIELD_NAME__method, 6, 6},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_UINT8,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {parc_msgs__msg__StartSignal__FIELD_NAME__heard, 5, 5},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_STRING,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
};

static rosidl_runtime_c__type_description__IndividualTypeDescription parc_msgs__msg__StartSignal__REFERENCED_TYPE_DESCRIPTIONS[] = {
  {
    {builtin_interfaces__msg__Time__TYPE_NAME, 27, 27},
    {NULL, 0, 0},
  },
};

const rosidl_runtime_c__type_description__TypeDescription *
parc_msgs__msg__StartSignal__get_type_description(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static bool constructed = false;
  static const rosidl_runtime_c__type_description__TypeDescription description = {
    {
      {parc_msgs__msg__StartSignal__TYPE_NAME, 25, 25},
      {parc_msgs__msg__StartSignal__FIELDS, 3, 3},
    },
    {parc_msgs__msg__StartSignal__REFERENCED_TYPE_DESCRIPTIONS, 1, 1},
  };
  if (!constructed) {
    assert(0 == memcmp(&builtin_interfaces__msg__Time__EXPECTED_HASH, builtin_interfaces__msg__Time__get_type_hash(NULL), sizeof(rosidl_type_hash_t)));
    description.referenced_type_descriptions.data[0].fields = builtin_interfaces__msg__Time__get_type_description(NULL)->type_description.fields;
    constructed = true;
  }
  return &description;
}

static char toplevel_type_raw_source[] =
  "# Published once by the team on /parc/start when the robot starts its run.\n"
  "# QoS: reliable, depth 10. The run clock starts when the referee receives it.\n"
  "\n"
  "builtin_interfaces/Time stamp\n"
  "\n"
  "uint8 METHOD_COMMAND = 0   # started by a typed command\n"
  "uint8 METHOD_VOICE   = 1   # started by a spoken start word (bonus)\n"
  "uint8 method\n"
  "\n"
  "# For voice starts: the recognised word (\"go\", \"allez\" or \"vai\"). Empty otherwise.\n"
  "string heard";

static char msg_encoding[] = "msg";

// Define all individual source functions

const rosidl_runtime_c__type_description__TypeSource *
parc_msgs__msg__StartSignal__get_individual_type_description_source(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static const rosidl_runtime_c__type_description__TypeSource source = {
    {parc_msgs__msg__StartSignal__TYPE_NAME, 25, 25},
    {msg_encoding, 3, 3},
    {toplevel_type_raw_source, 419, 419},
  };
  return &source;
}

const rosidl_runtime_c__type_description__TypeSource__Sequence *
parc_msgs__msg__StartSignal__get_type_description_sources(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_runtime_c__type_description__TypeSource sources[2];
  static const rosidl_runtime_c__type_description__TypeSource__Sequence source_sequence = {sources, 2, 2};
  static bool constructed = false;
  if (!constructed) {
    sources[0] = *parc_msgs__msg__StartSignal__get_individual_type_description_source(NULL),
    sources[1] = *builtin_interfaces__msg__Time__get_individual_type_description_source(NULL);
    constructed = true;
  }
  return &source_sequence;
}
