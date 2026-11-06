# generated from rosidl_generator_py/resource/_idl.py.em
# with input from parc_msgs:msg/RunStatus.idl
# generated code does not contain a copyright notice

# This is being done at the module level and not on the instance level to avoid looking
# for the same variable multiple times on each instance. This variable is not supposed to
# change during runtime so it makes sense to only look for it once.
from os import getenv

ros_python_check_fields = getenv('ROS_PYTHON_CHECK_FIELDS', default='')


# Import statements for member types

# Member 'tag_order'
# Member 'tags_reported'
import array  # noqa: E402, I100

import builtins  # noqa: E402, I100

import math  # noqa: E402, I100

import rosidl_parser.definition  # noqa: E402, I100


class Metaclass_RunStatus(type):
    """Metaclass of message 'RunStatus'."""

    _CREATE_ROS_MESSAGE = None
    _CONVERT_FROM_PY = None
    _CONVERT_TO_PY = None
    _DESTROY_ROS_MESSAGE = None
    _TYPE_SUPPORT = None

    __constants = {
        'IDLE': 0,
        'ARMED': 1,
        'RUNNING': 2,
        'FINISHED': 3,
        'TIMED_OUT': 4,
        'TERMINATED': 5,
    }

    @classmethod
    def __import_type_support__(cls):
        try:
            from rosidl_generator_py import import_type_support
            module = import_type_support('parc_msgs')
        except ImportError:
            import logging
            import traceback
            logger = logging.getLogger(
                'parc_msgs.msg.RunStatus')
            logger.debug(
                'Failed to import needed modules for type support:\n' +
                traceback.format_exc())
        else:
            cls._CREATE_ROS_MESSAGE = module.create_ros_message_msg__msg__run_status
            cls._CONVERT_FROM_PY = module.convert_from_py_msg__msg__run_status
            cls._CONVERT_TO_PY = module.convert_to_py_msg__msg__run_status
            cls._TYPE_SUPPORT = module.type_support_msg__msg__run_status
            cls._DESTROY_ROS_MESSAGE = module.destroy_ros_message_msg__msg__run_status

            from builtin_interfaces.msg import Time
            if Time.__class__._TYPE_SUPPORT is None:
                Time.__class__.__import_type_support__()

    @classmethod
    def __prepare__(cls, name, bases, **kwargs):
        # list constant names here so that they appear in the help text of
        # the message class under "Data and other attributes defined here:"
        # as well as populate each message instance
        return {
            'IDLE': cls.__constants['IDLE'],
            'ARMED': cls.__constants['ARMED'],
            'RUNNING': cls.__constants['RUNNING'],
            'FINISHED': cls.__constants['FINISHED'],
            'TIMED_OUT': cls.__constants['TIMED_OUT'],
            'TERMINATED': cls.__constants['TERMINATED'],
        }

    @property
    def IDLE(self):
        """Message constant 'IDLE'."""
        return Metaclass_RunStatus.__constants['IDLE']

    @property
    def ARMED(self):
        """Message constant 'ARMED'."""
        return Metaclass_RunStatus.__constants['ARMED']

    @property
    def RUNNING(self):
        """Message constant 'RUNNING'."""
        return Metaclass_RunStatus.__constants['RUNNING']

    @property
    def FINISHED(self):
        """Message constant 'FINISHED'."""
        return Metaclass_RunStatus.__constants['FINISHED']

    @property
    def TIMED_OUT(self):
        """Message constant 'TIMED_OUT'."""
        return Metaclass_RunStatus.__constants['TIMED_OUT']

    @property
    def TERMINATED(self):
        """Message constant 'TERMINATED'."""
        return Metaclass_RunStatus.__constants['TERMINATED']


class RunStatus(metaclass=Metaclass_RunStatus):
    """
    Message class 'RunStatus'.

    Constants:
      IDLE
      ARMED
      RUNNING
      FINISHED
      TIMED_OUT
      TERMINATED
    """

    __slots__ = [
        '_stamp',
        '_state',
        '_elapsed_s',
        '_time_limit_s',
        '_tag_order',
        '_tags_reported',
        '_start_method',
        '_false_start',
        '_check_fields',
    ]

    _fields_and_field_types = {
        'stamp': 'builtin_interfaces/Time',
        'state': 'uint8',
        'elapsed_s': 'float',
        'time_limit_s': 'float',
        'tag_order': 'sequence<uint8>',
        'tags_reported': 'sequence<uint8>',
        'start_method': 'uint8',
        'false_start': 'boolean',
    }

    # This attribute is used to store an rosidl_parser.definition variable
    # related to the data type of each of the components the message.
    SLOT_TYPES = (
        rosidl_parser.definition.NamespacedType(['builtin_interfaces', 'msg'], 'Time'),  # noqa: E501
        rosidl_parser.definition.BasicType('uint8'),  # noqa: E501
        rosidl_parser.definition.BasicType('float'),  # noqa: E501
        rosidl_parser.definition.BasicType('float'),  # noqa: E501
        rosidl_parser.definition.UnboundedSequence(rosidl_parser.definition.BasicType('uint8')),  # noqa: E501
        rosidl_parser.definition.UnboundedSequence(rosidl_parser.definition.BasicType('uint8')),  # noqa: E501
        rosidl_parser.definition.BasicType('uint8'),  # noqa: E501
        rosidl_parser.definition.BasicType('boolean'),  # noqa: E501
    )

    def __init__(self, **kwargs):
        if 'check_fields' in kwargs:
            self._check_fields = kwargs['check_fields']
        else:
            self._check_fields = ros_python_check_fields == '1'
        if self._check_fields:
            assert all('_' + key in self.__slots__ for key in kwargs.keys()), \
                'Invalid arguments passed to constructor: %s' % \
                ', '.join(sorted(k for k in kwargs.keys() if '_' + k not in self.__slots__))
        from builtin_interfaces.msg import Time
        self.stamp = kwargs.get('stamp', Time())
        self.state = kwargs.get('state', int())
        self.elapsed_s = kwargs.get('elapsed_s', float())
        self.time_limit_s = kwargs.get('time_limit_s', float())
        self.tag_order = array.array('B', kwargs.get('tag_order', []))
        self.tags_reported = array.array('B', kwargs.get('tags_reported', []))
        self.start_method = kwargs.get('start_method', int())
        self.false_start = kwargs.get('false_start', bool())

    def __repr__(self):
        typename = self.__class__.__module__.split('.')
        typename.pop()
        typename.append(self.__class__.__name__)
        args = []
        for s, t in zip(self.get_fields_and_field_types().keys(), self.SLOT_TYPES):
            field = getattr(self, s)
            fieldstr = repr(field)
            # We use Python array type for fields that can be directly stored
            # in them, and "normal" sequences for everything else.  If it is
            # a type that we store in an array, strip off the 'array' portion.
            if (
                isinstance(t, rosidl_parser.definition.AbstractSequence) and
                isinstance(t.value_type, rosidl_parser.definition.BasicType) and
                t.value_type.typename in ['float', 'double', 'int8', 'uint8', 'int16', 'uint16', 'int32', 'uint32', 'int64', 'uint64']
            ):
                if len(field) == 0:
                    fieldstr = '[]'
                else:
                    if self._check_fields:
                        assert fieldstr.startswith('array(')
                    prefix = "array('X', "
                    suffix = ')'
                    fieldstr = fieldstr[len(prefix):-len(suffix)]
            args.append(s + '=' + fieldstr)
        return '%s(%s)' % ('.'.join(typename), ', '.join(args))

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        if self.stamp != other.stamp:
            return False
        if self.state != other.state:
            return False
        if self.elapsed_s != other.elapsed_s:
            return False
        if self.time_limit_s != other.time_limit_s:
            return False
        if self.tag_order != other.tag_order:
            return False
        if self.tags_reported != other.tags_reported:
            return False
        if self.start_method != other.start_method:
            return False
        if self.false_start != other.false_start:
            return False
        return True

    @classmethod
    def get_fields_and_field_types(cls):
        from copy import copy
        return copy(cls._fields_and_field_types)

    @builtins.property
    def stamp(self):
        """Message field 'stamp'."""
        return self._stamp

    @stamp.setter
    def stamp(self, value):
        if self._check_fields:
            from builtin_interfaces.msg import Time
            assert \
                isinstance(value, Time), \
                "The 'stamp' field must be a sub message of type 'Time'"
        self._stamp = value

    @builtins.property
    def state(self):
        """Message field 'state'."""
        return self._state

    @state.setter
    def state(self, value):
        if self._check_fields:
            assert \
                isinstance(value, int), \
                "The 'state' field must be of type 'int'"
            assert value >= 0 and value < 256, \
                "The 'state' field must be an unsigned integer in [0, 255]"
        self._state = value

    @builtins.property
    def elapsed_s(self):
        """Message field 'elapsed_s'."""
        return self._elapsed_s

    @elapsed_s.setter
    def elapsed_s(self, value):
        if self._check_fields:
            assert \
                isinstance(value, float), \
                "The 'elapsed_s' field must be of type 'float'"
            assert not (value < -3.402823466e+38 or value > 3.402823466e+38) or math.isinf(value), \
                "The 'elapsed_s' field must be a float in [-3.402823466e+38, 3.402823466e+38]"
        self._elapsed_s = value

    @builtins.property
    def time_limit_s(self):
        """Message field 'time_limit_s'."""
        return self._time_limit_s

    @time_limit_s.setter
    def time_limit_s(self, value):
        if self._check_fields:
            assert \
                isinstance(value, float), \
                "The 'time_limit_s' field must be of type 'float'"
            assert not (value < -3.402823466e+38 or value > 3.402823466e+38) or math.isinf(value), \
                "The 'time_limit_s' field must be a float in [-3.402823466e+38, 3.402823466e+38]"
        self._time_limit_s = value

    @builtins.property
    def tag_order(self):
        """Message field 'tag_order'."""
        return self._tag_order

    @tag_order.setter
    def tag_order(self, value):
        if self._check_fields:
            if isinstance(value, array.array):
                assert value.typecode == 'B', \
                    "The 'tag_order' array.array() must have the type code of 'B'"
                self._tag_order = value
                return
            from collections.abc import Sequence
            from collections.abc import Set
            from collections import UserList
            from collections import UserString
            assert \
                ((isinstance(value, Sequence) or
                  isinstance(value, Set) or
                  isinstance(value, UserList)) and
                 not isinstance(value, str) and
                 not isinstance(value, UserString) and
                 all(isinstance(v, int) for v in value) and
                 all(val >= 0 and val < 256 for val in value)), \
                "The 'tag_order' field must be a set or sequence and each value of type 'int' and each unsigned integer in [0, 255]"
        self._tag_order = array.array('B', value)

    @builtins.property
    def tags_reported(self):
        """Message field 'tags_reported'."""
        return self._tags_reported

    @tags_reported.setter
    def tags_reported(self, value):
        if self._check_fields:
            if isinstance(value, array.array):
                assert value.typecode == 'B', \
                    "The 'tags_reported' array.array() must have the type code of 'B'"
                self._tags_reported = value
                return
            from collections.abc import Sequence
            from collections.abc import Set
            from collections import UserList
            from collections import UserString
            assert \
                ((isinstance(value, Sequence) or
                  isinstance(value, Set) or
                  isinstance(value, UserList)) and
                 not isinstance(value, str) and
                 not isinstance(value, UserString) and
                 all(isinstance(v, int) for v in value) and
                 all(val >= 0 and val < 256 for val in value)), \
                "The 'tags_reported' field must be a set or sequence and each value of type 'int' and each unsigned integer in [0, 255]"
        self._tags_reported = array.array('B', value)

    @builtins.property
    def start_method(self):
        """Message field 'start_method'."""
        return self._start_method

    @start_method.setter
    def start_method(self, value):
        if self._check_fields:
            assert \
                isinstance(value, int), \
                "The 'start_method' field must be of type 'int'"
            assert value >= 0 and value < 256, \
                "The 'start_method' field must be an unsigned integer in [0, 255]"
        self._start_method = value

    @builtins.property
    def false_start(self):
        """Message field 'false_start'."""
        return self._false_start

    @false_start.setter
    def false_start(self, value):
        if self._check_fields:
            assert \
                isinstance(value, bool), \
                "The 'false_start' field must be of type 'bool'"
        self._false_start = value
