// generated from rosidl_generator_c/resource/idl__description.c.em
// with input from parc_msgs:msg/RunStatus.idl
// generated code does not contain a copyright notice

#include "parc_msgs/msg/detail/run_status__functions.h"

ROSIDL_GENERATOR_C_PUBLIC_parc_msgs
const rosidl_type_hash_t *
parc_msgs__msg__RunStatus__get_type_hash(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_type_hash_t hash = {1, {
      0xb0, 0xe3, 0x03, 0x6b, 0x72, 0x99, 0x70, 0x45,
      0x41, 0x14, 0x0b, 0x2f, 0x04, 0xa6, 0xe2, 0x94,
      0x36, 0x7d, 0x81, 0x89, 0x74, 0xdd, 0x4e, 0xbb,
      0xd8, 0x13, 0x2a, 0xbd, 0x6d, 0x3c, 0x7a, 0x19,
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

static char parc_msgs__msg__RunStatus__TYPE_NAME[] = "parc_msgs/msg/RunStatus";
static char builtin_interfaces__msg__Time__TYPE_NAME[] = "builtin_interfaces/msg/Time";

// Define type names, field names, and default values
static char parc_msgs__msg__RunStatus__FIELD_NAME__stamp[] = "stamp";
static char parc_msgs__msg__RunStatus__FIELD_NAME__state[] = "state";
static char parc_msgs__msg__RunStatus__FIELD_NAME__elapsed_s[] = "elapsed_s";
static char parc_msgs__msg__RunStatus__FIELD_NAME__time_limit_s[] = "time_limit_s";
static char parc_msgs__msg__RunStatus__FIELD_NAME__tag_order[] = "tag_order";
static char parc_msgs__msg__RunStatus__FIELD_NAME__tags_reported[] = "tags_reported";
static char parc_msgs__msg__RunStatus__FIELD_NAME__start_method[] = "start_method";
static char parc_msgs__msg__RunStatus__FIELD_NAME__false_start[] = "false_start";

static rosidl_runtime_c__type_description__Field parc_msgs__msg__RunStatus__FIELDS[] = {
  {
    {parc_msgs__msg__RunStatus__FIELD_NAME__stamp, 5, 5},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_NESTED_TYPE,
      0,
      0,
      {builtin_interfaces__msg__Time__TYPE_NAME, 27, 27},
    },
    {NULL, 0, 0},
  },
  {
    {parc_msgs__msg__RunStatus__FIELD_NAME__state, 5, 5},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_UINT8,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {parc_msgs__msg__RunStatus__FIELD_NAME__elapsed_s, 9, 9},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_FLOAT,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {parc_msgs__msg__RunStatus__FIELD_NAME__time_limit_s, 12, 12},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_FLOAT,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {parc_msgs__msg__RunStatus__FIELD_NAME__tag_order, 9, 9},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_UINT8_UNBOUNDED_SEQUENCE,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {parc_msgs__msg__RunStatus__FIELD_NAME__tags_reported, 13, 13},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_UINT8_UNBOUNDED_SEQUENCE,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {parc_msgs__msg__RunStatus__FIELD_NAME__start_method, 12, 12},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_UINT8,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {parc_msgs__msg__RunStatus__FIELD_NAME__false_start, 11, 11},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_BOOLEAN,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
};

static rosidl_runtime_c__type_description__IndividualTypeDescription parc_msgs__msg__RunStatus__REFERENCED_TYPE_DESCRIPTIONS[] = {
  {
    {builtin_interfaces__msg__Time__TYPE_NAME, 27, 27},
    {NULL, 0, 0},
  },
};

const rosidl_runtime_c__type_description__TypeDescription *
parc_msgs__msg__RunStatus__get_type_description(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static bool constructed = false;
  static const rosidl_runtime_c__type_description__TypeDescription description = {
    {
      {parc_msgs__msg__RunStatus__TYPE_NAME, 23, 23},
      {parc_msgs__msg__RunStatus__FIELDS, 8, 8},
    },
    {parc_msgs__msg__RunStatus__REFERENCED_TYPE_DESCRIPTIONS, 1, 1},
  };
  if (!constructed) {
    assert(0 == memcmp(&builtin_interfaces__msg__Time__EXPECTED_HASH, builtin_interfaces__msg__Time__get_type_hash(NULL), sizeof(rosidl_type_hash_t)));
    description.referenced_type_descriptions.data[0].fields = builtin_interfaces__msg__Time__get_type_description(NULL)->type_description.fields;
    constructed = true;
  }
  return &description;
}

static char toplevel_type_raw_source[] =
  "# Published by the referee on /parc/run_status at 2 Hz and on every change.\n"
  "# QoS: reliable, transient local, depth 1.\n"
  "# Teams can use it to confirm their start and visits were received, and should\n"
  "# stop the robot when the state is FINISHED, TIMED_OUT or TERMINATED.\n"
  "\n"
  "builtin_interfaces/Time stamp\n"
  "\n"
  "uint8 IDLE       = 0   # no run in progress\n"
  "uint8 ARMED      = 1   # order published, waiting for /parc/start\n"
  "uint8 RUNNING    = 2   # clock running\n"
  "uint8 FINISHED   = 3   # fourth tag reported or /parc/finish received\n"
  "uint8 TIMED_OUT  = 4   # time limit reached\n"
  "uint8 TERMINATED = 5   # ended by a judge (safety stop, contact with a person, loss of control)\n"
  "uint8 state\n"
  "\n"
  "float32 elapsed_s      # seconds since the start signal\n"
  "float32 time_limit_s   # 600\n"
  "\n"
  "uint8[] tag_order      # same as /parc/tag_order\n"
  "uint8[] tags_reported  # tag IDs reported, in the order received (the judges' verdict is separate)\n"
  "\n"
  "uint8 start_method     # StartSignal.METHOD_*, valid once RUNNING\n"
  "bool false_start       # robot moved before the start signal";

static char msg_encoding[] = "msg";

// Define all individual source functions

const rosidl_runtime_c__type_description__TypeSource *
parc_msgs__msg__RunStatus__get_individual_type_description_source(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static const rosidl_runtime_c__type_description__TypeSource source = {
    {parc_msgs__msg__RunStatus__TYPE_NAME, 23, 23},
    {msg_encoding, 3, 3},
    {toplevel_type_raw_source, 1034, 1034},
  };
  return &source;
}

const rosidl_runtime_c__type_description__TypeSource__Sequence *
parc_msgs__msg__RunStatus__get_type_description_sources(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_runtime_c__type_description__TypeSource sources[2];
  static const rosidl_runtime_c__type_description__TypeSource__Sequence source_sequence = {sources, 2, 2};
  static bool constructed = false;
  if (!constructed) {
    sources[0] = *parc_msgs__msg__RunStatus__get_individual_type_description_source(NULL),
    sources[1] = *builtin_interfaces__msg__Time__get_individual_type_description_source(NULL);
    constructed = true;
  }
  return &source_sequence;
}
