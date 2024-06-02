"""
Initialize module
"""

from plist_helper.helper import PlistHelper
from plist_helper import cli

INFO_TYPE_FILE = PlistHelper.PLIST_INFO_TYPE_FILE
INFO_TYPE_REPRESENTATION = PlistHelper.PLIST_INFO_TYPE_REPRESENTATION
ENTRY_DATA_TYPES = PlistHelper.ENTRY_DATA_TYPES
FILE_FORMATS = PlistHelper.FILE_FORMATS

__all__ = ["cli", "PlistHelper"]
