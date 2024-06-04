"""PlistHelper definition."""

from __future__ import annotations

import datetime as _datetime
import os.path as _os_path
import plistlib as _plistlib
import sys as _sys
import tempfile as _tempfile
from io import BytesIO as _BytesIO
from types import MappingProxyType as _MappingProxyType

from plist_helper.helpers import verify


class PlistHelper:
    """Sensible management of Apple plist files.

    Designed to replace the need for the "PlistBuddy", "plutil", and "defaults" utilities.

    This class utilizes the plistlib builtin module to enable management of plist files.

    This class can be instantiated with a string argument that is a file path.
    The file path can be absolute or relative to the current working directory.

    It is also possible to instantiate this class with a bytestring or bytearray
    that represents the content of a plist file.

    Examples
    --------
        from plist_helper import PlistHelper
        PlistHelper('/path/to/a/plist/file.plist')
        PlistHelper('relative/path/to/a/plist/file.plist')
        PlistHelper(b'<plist><dict><key>hello</key><string>world!</string></dict></plist>')

    Notes
    -----
        This class, as well as the underlying plistlib, is unable to handle plist files
        that contain empty 'bool', 'date', 'integer', or 'real' data entries.

        While using tuple data to represent plist arrays is possible, it is not
        recommended. Using tuple data with insert_entry, insert_array_append, update_entry,
        and upsert_entry can cause issues if that data needs to be changed later.
        For this reason, it is recommended to always represent plist arrays as python
        lists instead of tuples.

    TODO(@jlyle)

    """

    PLIST_INFO_TYPE_FILE = "file"
    PLIST_INFO_TYPE_REPRESENTATION = "representation"

    __PLIST_INFO_TYPES = (PLIST_INFO_TYPE_FILE, PLIST_INFO_TYPE_REPRESENTATION)

    """
    Representation of the data types allowed for plist entries.

    name:           The name of the plist entry data type (the xml tag name)
    class:          The default data type class used to represent plist data
                    when parsed from a plist.
    otherClasses:   Other data type classes that can be used when converting
                    python data to a plist.
    """
    # TODO(@jlyle): Create test that makes sure each entry in ENTRY_DATA_TYPES has key = value["name"]
    ENTRY_DATA_TYPES = _MappingProxyType(
        {
            "array": _MappingProxyType(
                {
                    "name": "array",
                    "class": list,
                    "otherClasses": tuple([tuple]),
                },
            ),
            "bool": _MappingProxyType(
                {
                    "name": "bool",
                    "class": bool,
                    "otherClasses": tuple(),
                },
            ),
            "data": _MappingProxyType(
                {
                    "name": "data",
                    "class": bytes,
                    "otherClasses": tuple([bytearray]),
                },
            ),
            "date": _MappingProxyType(
                {
                    "name": "date",
                    "class": _datetime.datetime,
                    "otherClasses": tuple(),
                },
            ),
            "dict": _MappingProxyType(
                {
                    "name": "dict",
                    "class": dict,
                    "otherClasses": tuple(),
                },
            ),
            "integer": _MappingProxyType(
                {
                    "name": "integer",
                    "class": int,
                    "otherClasses": tuple(),
                },
            ),
            "real": _MappingProxyType(
                {
                    "name": "real",
                    "class": float,
                    "otherClasses": tuple(),
                },
            ),
            "string": _MappingProxyType(
                {
                    "name": "string",
                    "class": str,
                    "otherClasses": tuple(),
                },
            ),
        },
    )

    # TODO(@jlyle): Create test that makes sure each entry in FILE_FORMATS has key = value["name"]
    FILE_FORMATS = _MappingProxyType(
        {
            "binary": _MappingProxyType(
                {
                    "name": "binary",
                    "type": _plistlib.FMT_BINARY,
                },
            ),
            "xml": _MappingProxyType(
                {
                    "name": "xml",
                    "type": _plistlib.FMT_XML,
                },
            ),
        },
    )

    def __init__(
        self,
        plist_info_type: str,
        plist_info: str | bytes | bytearray,
    ) -> None:
        """TODO(@jlyle)."""
        # List of instance attributes before initialization
        self.__plist_info_type = None
        self.__plist_info_format = None
        self.__plist_info = None
        self.__plist_data = None

        if plist_info_type not in self.__PLIST_INFO_TYPES:
            raise RuntimeError(
                'Invalid plist_info_type: "' + str(plist_info_type) + '"',
            )

        self.__plist_info_type = plist_info_type
        self.__plist_info = plist_info

        if plist_info_type == self.PLIST_INFO_TYPE_REPRESENTATION:
            self.__plist_info_format, self.__plist_data = self.__parse_bytes(plist_info)
        elif plist_info_type == self.PLIST_INFO_TYPE_FILE:
            plist_info = _os_path.realpath(plist_info)
            if not _os_path.isfile(plist_info):
                raise RuntimeError("Cannot find plist file: " + plist_info)

            self.__plist_info_format, self.__plist_data = self.__parse_file(plist_info)

    def __str__(self) -> str:
        """TODO(@jlyle)."""
        return _plistlib.dumps(self.__plist_data, sort_keys=False).decode()

    def __repr__(self) -> str:
        """TODO(@jlyle)."""
        if self.__plist_info_type == self.PLIST_INFO_TYPE_FILE:
            return 'Plist("' + self.__plist_info + '")'

        if self.__plist_info_type == self.PLIST_INFO_TYPE_REPRESENTATION:
            return "Plist(" + repr(self.__plist_info) + ")"

        return None

    @classmethod
    def __get_file_format_from_name(cls, file_format: str) -> _MappingProxyType:
        """Get a plist file format specification based on the provided  file format name.

        TODO(@jlyle)
        """
        try:
            result = cls.FILE_FORMATS[file_format.lower()]
        except KeyError as e:
            raise ValueError(
                'Invalid file format specified: "' + file_format + '"',
            ) from e

        return result

    @classmethod
    def __get_entry_data_type_by_name(cls, data_type_name: str) -> dict:
        """Get a plist data type specification based on the provided data type name.

        TODO(@jlyle)
        """
        try:
            result = cls.ENTRY_DATA_TYPES[data_type_name.lower()]
        except KeyError as e:
            raise ValueError(
                'Invalid entry data type specified: "' + data_type_name + '"',
            ) from e

        return result.copy()

    @classmethod
    def __get_entry_data_type_by_class(cls, data: object) -> dict:
        """Get a plist data type specification based on the data type class of the provided object.

        TODO(@jlyle)
        """
        result = [
            spec
            for spec in cls.ENTRY_DATA_TYPES.values()
            if isinstance(data, (spec["class"], tuple(spec["otherClasses"])))
        ]
        num_results = len(result)

        verify(
            num_results == 0,
            ValueError('Invalid entry data type specified: "' + type(data) + '"'),
        )

        verify(
            num_results > 1,
            OverflowError(
                "Entry data types has duplicate class types, developer action required",
            ),
        )

        return result[0].copy()

    @classmethod
    def __parse_bytes(
        cls,
        plist_bytes: bytes | bytearray,
    ) -> dict | list | bool | bytes | int | float | str:
        """Get the parsed plist bytestring data.

        TODO(@jlyle)
        """
        try:
            fp = _BytesIO(plist_bytes)
        except Exception as e:
            raise RuntimeError("Unable to load bytes-like object") from e

        try:
            # Attempt to parse the converted bytes
            plist = _plistlib.load(fp)

            # Bytes loaded okay, so determine if it was BINARY or XML
            fp.seek(0)
            header = fp.read(32)

            if header[:8] == b"bplist00":
                fmt = cls.__get_file_format_from_name("binary")
            else:
                fmt = cls.__get_file_format_from_name("xml")
        except Exception as e:
            raise ValueError("Unable to parse provided plist") from e

        return fmt, plist

    @classmethod
    def __parse_file(
        cls,
        plist_file: str,
    ) -> tuple[_MappingProxyType, dict | list | bool | bytes | int | float | str]:
        """Get the parsed plist file data.

        TODO(@jlyle)
        """
        verify(
            isinstance(plist_file, str),
            TypeError(
                "Invalid type for plist_file, expected str, got "
                + type(plist_file).__name__,
            ),
        )

        try:
            with open(plist_file, "rb") as fp:
                # Load the file with plistlib and make sure it loads okay
                plist = _plistlib.load(fp)

                # File loads okay, so determine if it was BINARY or XML
                fp.seek(0)
                header = fp.read(32)

                if header[:8] == b"bplist00":
                    fmt = cls.__get_file_format_from_name("binary")
                else:
                    fmt = cls.__get_file_format_from_name("xml")
        except OSError as e:
            raise ValueError("Unable to open provided file") from e
        except Exception as e:
            raise ValueError("Unable to parse provided file") from e

        return fmt, plist

    @classmethod
    def __normalize_path(cls, path: list | tuple | str | int) -> list:
        """Take a path list/tuple/str/int and make sure it is always a list.

        TODO(@jlyle)
        """
        new_path = None

        if path is None:
            new_path = []
        elif isinstance(path, list):
            new_path = path.copy()
        elif isinstance(path, tuple):
            new_path = list(path)
        elif isinstance(path, str):
            # Do not use list constructor on string, it will split the string
            # into individual characters to make the list
            new_path = [path]
        else:
            # Do not use list constructor on string, it will split the string
            # into individual characters to make the list
            new_path = [str(path)]

        for component in new_path:
            verify(
                isinstance(component, (str, int)),
                ValueError(
                    "Invalid path specified, must be made up of strings or integers",
                ),
            )

        return new_path

    @classmethod
    def create_empty_file(
        cls,
        plist_file: str,
        output_format: str = "xml",
        data_type: str = "dict",
    ) -> None:
        """Create a new, valid plist file with an empty root entry.

        TODO(@jlyle)
        """
        file_format_spec = cls.__get_file_format_from_name(output_format)
        entry_data_type_spec = cls.__get_entry_data_type_by_name(data_type)

        verify(
            entry_data_type_spec["name"] not in ("bool", "date", "integer", "real"),
            ValueError(
                "Cannot create an empty plist with the "
                + entry_data_type_spec["name"]
                + " root entry data type",
            ),
        )

        empty_value = entry_data_type_spec["class"]()

        with open(plist_file, "xb") as fp:
            _plistlib.dump(empty_value, fp, fmt=file_format_spec["type"])

    @classmethod
    def convert_bytes(
        cls,
        plist_bytes: bytes | bytearray,
        output_format: str = "xml",
    ) -> bytes:
        """Convert a given plist representation to the specified format.

        TODO(@jlyle)
        """
        file_format_spec = cls.__get_file_format_from_name(output_format)

        plist_format, plist_data = cls.__parse_bytes(plist_bytes)

        if plist_format != output_format:
            plist = _plistlib.dumps(
                plist_data,
                fmt=file_format_spec["type"],
                sort_keys=False,
            )
        else:
            plist = plist_bytes

        return plist

    @classmethod
    def convert_file(
        cls,
        plist_file: str,
        output_format: str = "xml",
    ) -> None:
        """Convert a given plist file to the specified format.

        TODO(@jlyle)
        """
        file_format_spec = cls.__get_file_format_from_name(output_format)

        plist_format, plist_data = cls.__parse_file(plist_file)

        if plist_format != output_format:
            with open(plist_file, "wb") as fp:
                _plistlib.dump(
                    plist_data,
                    fp,
                    fmt=file_format_spec["type"],
                    sort_keys=False,
                )

    def get_plist_info_format(
        self,
    ) -> _MappingProxyType:
        """Get the format of the parsed plist_info used to instantiate the class.

        TODO(@jlyle)
        """
        return self.__plist_info_format

    def get_plist_info(
        self,
    ) -> str | bytes | bytearray:
        """Get the plist_info used to instantiate the class.

        TODO(@jlyle)
        """
        return self.__plist_info

    def get_data(self) -> dict | list | bool | bytes | int | float | str:
        """Get the parsed plist data.

        Will return None if unable to parse the file.

        TODO(@jlyle)
        """
        data = self.__plist_data

        if hasattr(data, "copy"):
            data = data.copy()

        return data

    def exists(self, path: list | tuple | str | int) -> bool:
        """Check if an entry exists.

        TODO(@jlyle)
        """
        path = self.__normalize_path(path)

        try:
            self.__get(self.__plist_data, path)
        except KeyError:
            return False

        return True

    @classmethod
    def __get(
        cls,
        plist_data: dict | list | bool | bytes | int | float | str,
        path: list,
    ) -> dict | list | bool | bytes | int | float | str:
        """Get the python data representation of a plist entry.

        TODO(@jlyle)
        """
        verify(
            isinstance(path, list),
            TypeError("Path must be specified as a list"),
        )

        entry = plist_data
        string_path = ""

        for path_part in path:
            new_path_part = path_part
            if string_path != "":
                string_path += "."
            string_path += str(new_path_part).replace(".", r"\.")

            entry_data_type_spec = cls.__get_entry_data_type_by_class(entry)

            key_error_text = (
                "("
                + entry_data_type_spec["name"]
                + ') Cannot access "'
                + string_path
                + '"'
            )

            if isinstance(entry, dict):
                try:
                    new_path_part = str(new_path_part)
                    entry = entry[new_path_part]
                except Exception as e:
                    raise KeyError(key_error_text) from e
            elif isinstance(entry, list):
                try:
                    new_path_part = int(new_path_part)
                    entry = entry[new_path_part]
                except Exception as e:
                    raise KeyError(key_error_text) from e
            else:
                raise KeyError(key_error_text)

        return entry

    def get(
        self,
        path: list | tuple | str | int | None = None,
    ) -> dict | list | bool | bytes | int | float | str:
        """Get the python data representation of a plist entry.

        TODO(@jlyle)
        """
        path = self.__normalize_path(path)

        entry = self.__get(self.__plist_data, path)

        if hasattr(entry, "copy"):
            entry = entry.copy()

        return entry

    def get_type(self, path: list | tuple | str | int | None = None) -> str:
        """Get the plist type of the entry.

        TODO(@jlyle)
        """
        path = self.__normalize_path(path)

        entry = self.__get(self.__plist_data, path)

        entry_data_type_spec = self.__get_entry_data_type_by_class(entry)

        return entry_data_type_spec["name"]

    def get_dict_keys(self, path: list | tuple | str | int | None = None) -> tuple:
        """Get the keys of the specified dict entry.

        TODO(@jlyle)
        """
        path = self.__normalize_path(path)

        entry = self.__get(self.__plist_data, path)

        entry_data_type_spec = self.__get_entry_data_type_by_class(entry)

        verify(
            entry_data_type_spec["name"] == "dict",
            ValueError("Specified entry is not a dict"),
        )

        return tuple(entry.keys())

    def get_array_length(self, path: list | tuple | str | int | None = None) -> int:
        """Get the length of the specified array entry.

        TODO(@jlyle)
        """
        path = self.__normalize_path(path)

        entry = self.__get(self.__plist_data, path)

        entry_data_type_spec = self.__get_entry_data_type_by_class(entry)

        verify(
            entry_data_type_spec["name"] == "array",
            ValueError("Specified entry is not an array"),
        )

        return len(entry)

    def print(
        self,
        output_format: str = "xml",
        output_sort: bool = False,
        path: list | tuple | str | int | None = None,
    ) -> None:
        """Print the plist to the screen formatted in the specified format starting at the specified entry.

        TODO(@jlyle)
        """
        verify(
            isinstance(output_sort, bool),
            TypeError(
                "Invalid data type for output_sort, expected bool got "
                + type(output_sort).__name__,
            ),
        )

        path = self.__normalize_path(path)

        if output_format is None:
            output_format = "xml"

        file_format_spec = self.__get_file_format_from_name(output_format)

        plist_data = None
        if path is None:
            plist_data = self.__plist_data
        else:
            plist_data = self.__get(self.__plist_data, path)

        output = _plistlib.dumps(
            plist_data,
            fmt=file_format_spec["type"],
            sort_keys=output_sort,
        )

        if output_format == "xml":
            output = output.decode()

        _sys.stdout.write(str(output) + "\n")

    def write(
        self,
        output_file: str | None = None,
        output_format: str | None = None,
        output_sort: bool | None = False,
        path: list | tuple | str | int | None = None,
    ) -> None:
        """Write the plist to the specified file.

        The entire plist will be written to the file unless a path value is
        provided, then that entry down will be used to create the plist file.

        If no output_format is given, then the file will be written in the format
        from which the plist was originally parsed.

        If no output_file is given, this will write to the file used to instantiate
        this object. If a plist representation was used to instantiate this object,
        then a RuntimeError is thrown.

        TODO(@jlyle)
        """
        verify(
            isinstance(output_sort, bool),
            TypeError(
                "Invalid data type for output_sort, expected bool got "
                + type(output_sort).__name__,
            ),
        )

        if output_file is None:
            verify(
                self.__plist_info_type == self.PLIST_INFO_TYPE_FILE,
                RuntimeError(
                    "Object not instantiated from plist file, value for output_file required",
                ),
            )

            output_file = self.__plist_info

        if output_format is None:
            file_format_spec = self.__plist_info_format
        else:
            file_format_spec = self.__get_file_format_from_name(output_format)

        path = self.__normalize_path(path)

        plist_data = None
        if path is None:
            plist_data = self.__plist_data
        else:
            plist_data = self.__get(self.__plist_data, path)

        # Use a temporary file in case there is any issue converting the data.
        # This prevents the target file from being in a bad state if
        # the plist conversion fails
        with _tempfile.NamedTemporaryFile() as tmp:
            _plistlib.dump(
                plist_data,
                tmp,
                fmt=file_format_spec["type"],
                sort_keys=output_sort,
            )

            with open(output_file, "wb") as fp:
                # Reset temporary file's read/write position to beginning of file
                tmp.seek(0)
                fp.write(tmp.read())

    def insert(
        self,
        path: list | tuple | str | int,
        value: dict | list | bool | bytes | int | float | str,
    ) -> None:
        """Insert a new entry into the plist.

        TODO(@jlyle)
        """
        root_data_type_spec = self.__get_entry_data_type_by_class(self.__plist_data)

        verify(
            root_data_type_spec["name"] not in ("array", "dict"),
            KeyError,
            "Cannot insert into a plist with a root type that is not array or dict",
        )

        path = self.__normalize_path(path)

        verify(
            len(path) == 0,
            KeyError,
            "Insertion path must be provided",
        )

        try:
            self.__get_entry_data_type_by_class(value)
        except Exception as e:
            raise TypeError("Invalid data type for provided value") from e

        verify(
            self.exists(path),
            RuntimeError,
            "An entry at this path already exists",
        )

        parent_path = list(path)
        insertion_key = parent_path.pop()

        try:
            parent_entry = self.__get(self.__plist_data, parent_path)
        except KeyError as e:
            raise KeyError("Cannot get entry parent") from e

        parent_entry_data_type_spec = self.__get_entry_data_type_by_class(parent_entry)

        if parent_entry_data_type_spec["name"] == "array":
            try:
                insertion_key = int(insertion_key)
            except Exception as e:
                raise ValueError(
                    "Inserting into an array requires an integer path spec",
                ) from e

            verify(
                insertion_key <= len(parent_entry),
                IndexError("Array insertions must be done at the last entry"),
            )
        elif parent_entry_data_type_spec["name"] == "dict":
            try:
                insertion_key = str(insertion_key)
            except Exception as e:
                raise ValueError(
                    "Inserting into a dict requires a string path spec",
                ) from e

        try:
            # Have plistlib process the value to see if it is valid
            _plistlib.dumps(value)
        except Exception as e:
            raise ValueError("Value to insert is not valid plist data") from e

        if parent_entry_data_type_spec["name"] == "array":
            parent_entry.insert(insertion_key, value)
        elif parent_entry_data_type_spec["name"] == "dict":
            parent_entry[insertion_key] = value

    def insert_array_append(
        self,
        path: list | tuple | str | int,
        value: dict | list | bool | bytes | int | float | str,
    ) -> None:
        """Insert a value into an array by appending it to the end of the array.

        If the path specified does not exist, an empty array will attempt to be
        created at the specified path. The parent of the specified path must
        already exist for this to work.

        TODO(@jlyle)
        """
        root_data_type_spec = self.__get_entry_data_type_by_class(self.__plist_data)

        verify(
            root_data_type_spec["name"] in ("array", "dict"),
            KeyError(
                "Cannot insert into a plist with a root type that is not array or dict",
            ),
        )

        path = self.__normalize_path(path)

        verify(
            len(path) > 0,
            KeyError("Insertion path must be provided"),
        )

        array_data_type_spec = self.__get_entry_data_type_by_name("array")

        created_target_array = False
        if not self.exists(path):
            self.insert(path, array_data_type_spec["class"]())
            created_target_array = True

        try:
            entry = self.__get(self.__plist_data, path)

            entry_data_type_spec = self.__get_entry_data_type_by_class(entry)

            verify(
                entry_data_type_spec["name"] == "array",
                RuntimeError("The provided path must specify an array entry"),
            )

            path.append(len(entry))

            self.insert(path, value)
        except Exception:
            if created_target_array:
                self.delete(path)

            raise

    def update(
        self,
        path: list | tuple | str | int,
        value: dict | list | bool | bytes | int | float | str,
    ) -> None:
        """Update an existing entry in the plist.

        Updates are allowed to change the data type of the entry.

        TODO(@jlyle)
        """
        root_data_type_spec = self.__get_entry_data_type_by_class(self.__plist_data)

        path = self.__normalize_path(path)

        verify(
            root_data_type_spec["name"] in ("array", "dict") or len(path) == 0,
            KeyError(
                "Update path cannot be provided for root data types that are not array or dict",
            ),
        )

        try:
            self.__get_entry_data_type_by_class(value)
        except Exception as e:
            raise TypeError("Invalid data type for provided value") from e

        verify(
            self.exists(path),
            RuntimeError("An entry does not exist at this path"),
        )

        try:
            # Have plistlib process the value to see if it is valid
            _plistlib.dumps(value)
        except Exception as e:
            raise TypeError("Value to update to is not valid plist data") from e

        if len(path) == 0:
            # Updating root entry of non-collection data type
            self.__plist_data = value
        else:
            parent_path = list(path)
            update_key = parent_path.pop()
            parent_entry = self.__get(self.__plist_data, parent_path)

            parent_entry_data_type_spec = self.__get_entry_data_type_by_class(
                parent_entry,
            )

            if parent_entry_data_type_spec["name"] == "array":
                update_key = int(update_key)
            elif parent_entry_data_type_spec["name"] == "dict":
                update_key = str(update_key)

            parent_entry[update_key] = value

    def delete(self, path: list | tuple | str | int) -> None:
        """Delete an entry from a plist.

        TODO(@jlyle)
        """
        root_data_type_spec = self.__get_entry_data_type_by_class(self.__plist_data)

        verify(
            root_data_type_spec["name"] in ("array", "dict"),
            KeyError(
                "Delete cannot be preformed on root data types that are not array or dict",
            ),
        )

        path = self.__normalize_path(path)

        verify(
            len(path) > 0,
            RuntimeError("Cannot delete plist root entry"),
        )

        verify(
            self.exists(path),
            RuntimeError("An entry does not exist at this path"),
        )

        parent_path = list(path)
        delete_key = parent_path.pop()
        parent_entry = self.__get(self.__plist_data, parent_path)

        parent_data_type_spec = self.__get_entry_data_type_by_class(parent_entry)

        if parent_data_type_spec["name"] == "array":
            delete_key = int(delete_key)
        elif parent_data_type_spec["name"] == "dict":
            delete_key = str(delete_key)

        del parent_entry[delete_key]

    def upsert(
        self,
        path: list | tuple | str | int,
        value: dict | list | bool | bytes | int | float | str,
    ) -> None:
        """Insert or update a plist entry depending on if the entry specified by the path already exists or not.

        TODO(@jlyle)
        """
        path = self.__normalize_path(path)

        if not self.exists(path):
            self.insert(path, value)
        else:
            self.update(path, value)

    def __merge(
        self,
        source_entry: dict | list | bool | bytes | int | float | str,
        target_path: list | tuple | str | int,
        overwrite: bool,
    ) -> None:
        """Recursively merge python data (source_entry) into the current plist.

        TODO(@jlyle)
        """
        target_path = self.__normalize_path(target_path)

        ########################################################################
        ## Handle special root update cases
        ########################################################################

        root_data_type_spec = self.__get_entry_data_type_by_class(self.__plist_data)

        root_type_is_collection = root_data_type_spec["name"] in ("array", "dict")

        verify(
            root_type_is_collection or len(target_path) == 0,
            RuntimeError("Cannot merge into child of non-collection root plist"),
        )

        if not root_type_is_collection and len(target_path) == 0:
            # Merging into root
            if overwrite:
                # Merging into a non-collection type at the root with overwrite
                # is the same as updating to the given value. So just do this
                # and be done
                self.__plist_data = source_entry

            # Root has to exist
            # Root is non-collection type
            # If overwriting, data was set above and there is nothing left to do
            # If not overwriting, then there is nothing to do
            return

        ########################################################################
        ## Merge where target does not exist = simple insert
        ########################################################################

        if not self.exists(target_path):
            self.insert(target_path, source_entry)
            return

        ########################################################################
        ## Merge logic
        ########################################################################
        # At this point, both the source and the target are known to exist.
        # Remaining use cases at this point:
        #   1 - overwrite: no, target_data_type is simple
        #       Nothing to do
        #   2 - overwrite: no, target_data_type is collection, source_data_type is simple
        #       Nothing to do
        #   3 - overwrite: no, target_data_type is collection, source_data_type is collection
        #       Manual merge: values that exist in both collections are not overwritten in target
        #   4 - overwrite: yes, target_data_type is simple
        #       Direct update
        #   5 - overwrite: yes, target_data_type is collection, source_data_type is simple
        #       Direct update
        #   6 - overwrite: yes, target_data_type is collection, source_data_type is collection
        #       Manual merge: values that exist in both collections are overwritten in target

        target_entry = self.__get(self.__plist_data, target_path)
        target_data_spec = self.__get_entry_data_type_by_class(target_entry)
        target_type_is_collection = target_data_spec["name"] in ("array", "dict")

        source_data_spec = self.__get_entry_data_type_by_class(source_entry)
        source_type_is_collection = source_data_spec["name"] in ("array", "dict")

        if not (target_type_is_collection and source_type_is_collection):
            if overwrite:
                # Case 4 or 5
                self.update(target_path, source_entry)

            # Case 1 or 2 (also end of case 4 or 5)
            return

        # Case 3 or 6
        if source_data_spec["name"] == "array":
            for idx, elem in enumerate(source_entry):
                new_target_path = target_path.copy()
                new_target_path.append(idx)
                self.__merge(elem, new_target_path, overwrite)
        elif source_data_spec["name"] == "dict":
            for idx, elem in source_entry.items():
                new_target_path = target_path.copy()
                new_target_path.append(idx)
                self.__merge(elem, new_target_path, overwrite)

    def merge(
        self,
        source_plist_helper: PlistHelper,
        source_path: list | tuple | str | int | None = None,
        target_path: list | tuple | str | int | None = None,
        overwrite: bool = True,
    ) -> None:
        """Merge in a plist file (or a subset of a plist file) to the current plist.

        TODO(@jlyle)
        """
        ########################################################################
        ##  Parameter verifications
        ########################################################################

        verify(
            isinstance(overwrite, bool),
            TypeError(
                "Invalid overwrite type. Execpted boolean (bool), got "
                + type(overwrite).__name__,
            ),
        )

        source_path = self.__normalize_path(source_path)

        try:
            source_entry = source_plist_helper.get(source_path)
        except Exception as e:
            raise RuntimeError("Invalid source_path") from e

        ########################################################################
        ##  Merge
        ########################################################################
        self.__merge(source_entry, target_path, overwrite)
