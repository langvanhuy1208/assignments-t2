# generated from rosidl_generator_py/resource/_idl.py.em
# with input from ur_dashboard_msgs:srv/DownloadSupportFile.idl
# generated code does not contain a copyright notice


# Import statements for member types

import builtins  # noqa: E402, I100

import rosidl_parser.definition  # noqa: E402, I100


class Metaclass_DownloadSupportFile_Request(type):
    """Metaclass of message 'DownloadSupportFile_Request'."""

    _CREATE_ROS_MESSAGE = None
    _CONVERT_FROM_PY = None
    _CONVERT_TO_PY = None
    _DESTROY_ROS_MESSAGE = None
    _TYPE_SUPPORT = None

    __constants = {
    }

    @classmethod
    def __import_type_support__(cls):
        try:
            from rosidl_generator_py import import_type_support
            module = import_type_support('ur_dashboard_msgs')
        except ImportError:
            import logging
            import traceback
            logger = logging.getLogger(
                'ur_dashboard_msgs.srv.DownloadSupportFile_Request')
            logger.debug(
                'Failed to import needed modules for type support:\n' +
                traceback.format_exc())
        else:
            cls._CREATE_ROS_MESSAGE = module.create_ros_message_msg__srv__download_support_file__request
            cls._CONVERT_FROM_PY = module.convert_from_py_msg__srv__download_support_file__request
            cls._CONVERT_TO_PY = module.convert_to_py_msg__srv__download_support_file__request
            cls._TYPE_SUPPORT = module.type_support_msg__srv__download_support_file__request
            cls._DESTROY_ROS_MESSAGE = module.destroy_ros_message_msg__srv__download_support_file__request

    @classmethod
    def __prepare__(cls, name, bases, **kwargs):
        # list constant names here so that they appear in the help text of
        # the message class under "Data and other attributes defined here:"
        # as well as populate each message instance
        return {
        }


class DownloadSupportFile_Request(metaclass=Metaclass_DownloadSupportFile_Request):
    """Message class 'DownloadSupportFile_Request'."""

    __slots__ = [
        '_target_path',
    ]

    _fields_and_field_types = {
        'target_path': 'string',
    }

    SLOT_TYPES = (
        rosidl_parser.definition.UnboundedString(),  # noqa: E501
    )

    def __init__(self, **kwargs):
        assert all('_' + key in self.__slots__ for key in kwargs.keys()), \
            'Invalid arguments passed to constructor: %s' % \
            ', '.join(sorted(k for k in kwargs.keys() if '_' + k not in self.__slots__))
        self.target_path = kwargs.get('target_path', str())

    def __repr__(self):
        typename = self.__class__.__module__.split('.')
        typename.pop()
        typename.append(self.__class__.__name__)
        args = []
        for s, t in zip(self.__slots__, self.SLOT_TYPES):
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
                    assert fieldstr.startswith('array(')
                    prefix = "array('X', "
                    suffix = ')'
                    fieldstr = fieldstr[len(prefix):-len(suffix)]
            args.append(s[1:] + '=' + fieldstr)
        return '%s(%s)' % ('.'.join(typename), ', '.join(args))

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        if self.target_path != other.target_path:
            return False
        return True

    @classmethod
    def get_fields_and_field_types(cls):
        from copy import copy
        return copy(cls._fields_and_field_types)

    @builtins.property
    def target_path(self):
        """Message field 'target_path'."""
        return self._target_path

    @target_path.setter
    def target_path(self, value):
        if __debug__:
            assert \
                isinstance(value, str), \
                "The 'target_path' field must be of type 'str'"
        self._target_path = value


# Import statements for member types

# already imported above
# import builtins

# already imported above
# import rosidl_parser.definition


class Metaclass_DownloadSupportFile_Response(type):
    """Metaclass of message 'DownloadSupportFile_Response'."""

    _CREATE_ROS_MESSAGE = None
    _CONVERT_FROM_PY = None
    _CONVERT_TO_PY = None
    _DESTROY_ROS_MESSAGE = None
    _TYPE_SUPPORT = None

    __constants = {
    }

    @classmethod
    def __import_type_support__(cls):
        try:
            from rosidl_generator_py import import_type_support
            module = import_type_support('ur_dashboard_msgs')
        except ImportError:
            import logging
            import traceback
            logger = logging.getLogger(
                'ur_dashboard_msgs.srv.DownloadSupportFile_Response')
            logger.debug(
                'Failed to import needed modules for type support:\n' +
                traceback.format_exc())
        else:
            cls._CREATE_ROS_MESSAGE = module.create_ros_message_msg__srv__download_support_file__response
            cls._CONVERT_FROM_PY = module.convert_from_py_msg__srv__download_support_file__response
            cls._CONVERT_TO_PY = module.convert_to_py_msg__srv__download_support_file__response
            cls._TYPE_SUPPORT = module.type_support_msg__srv__download_support_file__response
            cls._DESTROY_ROS_MESSAGE = module.destroy_ros_message_msg__srv__download_support_file__response

    @classmethod
    def __prepare__(cls, name, bases, **kwargs):
        # list constant names here so that they appear in the help text of
        # the message class under "Data and other attributes defined here:"
        # as well as populate each message instance
        return {
        }


class DownloadSupportFile_Response(metaclass=Metaclass_DownloadSupportFile_Response):
    """Message class 'DownloadSupportFile_Response'."""

    __slots__ = [
        '_answer',
        '_success',
        '_support_files_present',
    ]

    _fields_and_field_types = {
        'answer': 'string',
        'success': 'boolean',
        'support_files_present': 'boolean',
    }

    SLOT_TYPES = (
        rosidl_parser.definition.UnboundedString(),  # noqa: E501
        rosidl_parser.definition.BasicType('boolean'),  # noqa: E501
        rosidl_parser.definition.BasicType('boolean'),  # noqa: E501
    )

    def __init__(self, **kwargs):
        assert all('_' + key in self.__slots__ for key in kwargs.keys()), \
            'Invalid arguments passed to constructor: %s' % \
            ', '.join(sorted(k for k in kwargs.keys() if '_' + k not in self.__slots__))
        self.answer = kwargs.get('answer', str())
        self.success = kwargs.get('success', bool())
        self.support_files_present = kwargs.get('support_files_present', bool())

    def __repr__(self):
        typename = self.__class__.__module__.split('.')
        typename.pop()
        typename.append(self.__class__.__name__)
        args = []
        for s, t in zip(self.__slots__, self.SLOT_TYPES):
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
                    assert fieldstr.startswith('array(')
                    prefix = "array('X', "
                    suffix = ')'
                    fieldstr = fieldstr[len(prefix):-len(suffix)]
            args.append(s[1:] + '=' + fieldstr)
        return '%s(%s)' % ('.'.join(typename), ', '.join(args))

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        if self.answer != other.answer:
            return False
        if self.success != other.success:
            return False
        if self.support_files_present != other.support_files_present:
            return False
        return True

    @classmethod
    def get_fields_and_field_types(cls):
        from copy import copy
        return copy(cls._fields_and_field_types)

    @builtins.property
    def answer(self):
        """Message field 'answer'."""
        return self._answer

    @answer.setter
    def answer(self, value):
        if __debug__:
            assert \
                isinstance(value, str), \
                "The 'answer' field must be of type 'str'"
        self._answer = value

    @builtins.property
    def success(self):
        """Message field 'success'."""
        return self._success

    @success.setter
    def success(self, value):
        if __debug__:
            assert \
                isinstance(value, bool), \
                "The 'success' field must be of type 'bool'"
        self._success = value

    @builtins.property
    def support_files_present(self):
        """Message field 'support_files_present'."""
        return self._support_files_present

    @support_files_present.setter
    def support_files_present(self, value):
        if __debug__:
            assert \
                isinstance(value, bool), \
                "The 'support_files_present' field must be of type 'bool'"
        self._support_files_present = value


class Metaclass_DownloadSupportFile(type):
    """Metaclass of service 'DownloadSupportFile'."""

    _TYPE_SUPPORT = None

    @classmethod
    def __import_type_support__(cls):
        try:
            from rosidl_generator_py import import_type_support
            module = import_type_support('ur_dashboard_msgs')
        except ImportError:
            import logging
            import traceback
            logger = logging.getLogger(
                'ur_dashboard_msgs.srv.DownloadSupportFile')
            logger.debug(
                'Failed to import needed modules for type support:\n' +
                traceback.format_exc())
        else:
            cls._TYPE_SUPPORT = module.type_support_srv__srv__download_support_file

            from ur_dashboard_msgs.srv import _download_support_file
            if _download_support_file.Metaclass_DownloadSupportFile_Request._TYPE_SUPPORT is None:
                _download_support_file.Metaclass_DownloadSupportFile_Request.__import_type_support__()
            if _download_support_file.Metaclass_DownloadSupportFile_Response._TYPE_SUPPORT is None:
                _download_support_file.Metaclass_DownloadSupportFile_Response.__import_type_support__()


class DownloadSupportFile(metaclass=Metaclass_DownloadSupportFile):
    from ur_dashboard_msgs.srv._download_support_file import DownloadSupportFile_Request as Request
    from ur_dashboard_msgs.srv._download_support_file import DownloadSupportFile_Response as Response

    def __init__(self):
        raise NotImplementedError('Service classes can not be instantiated')
