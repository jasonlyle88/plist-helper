"""Initialize module."""

from plist_helper import _exceptions, _plist

PlistHelper = _plist.PlistHelper
INFO_TYPE_FILE = PlistHelper.PLIST_INFO_TYPE_FILE
INFO_TYPE_REPRESENTATION = PlistHelper.PLIST_INFO_TYPE_REPRESENTATION
ENTRY_DATA_TYPES = PlistHelper.ENTRY_DATA_TYPES
FILE_FORMATS = PlistHelper.FILE_FORMATS
PlistHelperError = _exceptions.PlistHelperError
PlistHelperRuntimeError = _exceptions.PlistHelperRuntimeError
PlistHelperTypeError = _exceptions.PlistHelperTypeError
PlistHelperValueError = _exceptions.PlistHelperValueError
PlistHelperKeyError = _exceptions.PlistHelperKeyError

__all__ = [
    "PlistHelper",
    "ENTRY_DATA_TYPES",
    "FILE_FORMATS",
    "INFO_TYPE_FILE",
    "INFO_TYPE_REPRESENTATION",
    "PlistHelperError",
    "PlistHelperRuntimeError",
    "PlistHelperTypeError",
    "PlistHelperValueError",
    "PlistHelperKeyError",
]
