"""
datetime:   Used to work with plist date type data.
os.path:    Used to work with os files and pathing.
plistlib:   Provide ability to work with Apple plist files.
tempfile:   Used to manage temporary files for the operating systems.
"""

import datetime as _datetime
import os.path as _os_path
import plistlib as _plistlib
import tempfile as _tempfile
from io import BytesIO as _BytesIO


class PlistHelper:
    """
    Sensible management of Apple plist files.

    Designed to replace the need for the "PlistBuddy", "plutil", and "defaults" utilities.

    This class utilizes the plistlib builtin module to enable management of plist files.

    This class can be instantiated with a string argument that is a file path.
    The file path can be absolute or relative to the current working directory.

    It is also possible to instantiate this class with a bytestring or bytearray
    that represents the content of a plist file.

    Examples:
        from plist_helper import PlistHelper
        PlistHelper('/path/to/a/plist/file.plist')
        PlistHelper('relative/path/to/a/plist/file.plist')
        PlistHelper(b'<plist><dict><key>hello</key><string>world!</string></dict></plist>')

    NOTES:
        This class, as well as the underlying plistlib, is unable to handle plist files
        that contain empty 'bool', 'date', 'integer', or 'real' data entries.

        While using tuple data to represent plist arrays is possible, it is not
        recommended. Using tuple data with insert_entry, insert_array_append, update_entry,
        and upsert_entry can cause issues if that data needs to be changed later.
        For this reason, it is recommended to always represent plist arrays as python
        lists instead of tuples.

    TODO
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
    ENTRY_DATA_TYPES = {
        "array": {"class": list, "otherClasses": [tuple]},
        "bool": {"class": bool, "otherClasses": []},
        "data": {"class": bytes, "otherClasses": [bytearray]},
        "date": {"class": _datetime.datetime, "otherClasses": []},
        "dict": {"class": dict, "otherClasses": []},
        "integer": {"class": int, "otherClasses": []},
        "real": {"class": float, "otherClasses": []},
        "string": {"class": str, "otherClasses": []},
    }

    for key, value in ENTRY_DATA_TYPES.items():
        value["name"] = key

    # pylint: disable=no-member
    FILE_FORMATS = {
        "binary": {
            "type": _plistlib.FMT_BINARY,
        },
        "xml": {
            "type": _plistlib.FMT_XML,
        },
    }
    # pylint: enable=no-member

    for key, value in FILE_FORMATS.items():
        value["name"] = key

    def __init__(
        self,
        plist_info_type: str,
        plist_info: str | bytes | bytearray,
    ):
        # List of instance attributes before initialization
        self.__plist_info_type = None
        self.__plist_info_format = None
        self.__plist_info = None
        self.__plist_data = None

        if plist_info_type not in self.__PLIST_INFO_TYPES:
            raise RuntimeError(
                'Invalid plist_info_type: "' + str(plist_info_type) + '"'
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

    def __str__(self):
        return _plistlib.dumps(self.__plist_data, sort_keys=False).decode()

    def __repr__(self):
        if self.__plist_info_type == self.PLIST_INFO_TYPE_FILE:
            return 'Plist("' + self.__plist_info + '")'

        if self.__plist_info_type == self.PLIST_INFO_TYPE_REPRESENTATION:
            return "Plist(" + repr(self.__plist_info) + ")"

        return None

    @staticmethod
    def __get_variable_value_copy(var):
        """
        Get a copy of a variable as a value copy, not a reference copy.

        TODO
        """

        if hasattr(var, "copy"):
            return var.copy()

        return var

    @classmethod
    def __get_file_format_from_name(cls, file_format: str):
        """
        Get a plist file format specification based on theprovided  file format name.

        TODO
        """

        try:
            result = cls.FILE_FORMATS[file_format.lower()]
        except KeyError as e:
            raise ValueError(
                'Invalid file format specified: "' + file_format + '"'
            ) from e

        return result

    @classmethod
    def __get_entry_data_type_by_name(cls, data_type_name: str):
        """
        Get a plist data type specification based on the provided data type name.

        TODO
        """

        try:
            result = cls.ENTRY_DATA_TYPES[data_type_name.lower()]
        except KeyError as e:
            raise ValueError(
                'Invalid entry data type specified: "' + data_type_name + '"'
            ) from e

        return result

    @classmethod
    def __get_entry_data_type_by_class(cls, data: object):
        """
        Get a plist data type specification based on the data type class of the provided object.

        TODO
        """

        result = [
            spec
            for spec in cls.ENTRY_DATA_TYPES.values()
            if isinstance(data, (spec["class"], tuple(spec["otherClasses"])))
        ]
        num_results = len(result)

        if num_results == 0:
            raise ValueError('Invalid entry data type specified: "' + type(data) + '"')
        if num_results > 1:
            raise OverflowError(
                "Entry data types has duplicate class types, developer action required"
            )

        return result[0]

    @classmethod
    def __parse_bytes(
        cls,
        plist_bytes: bytes | bytearray,
    ):
        """
        Get the parsed plist bytestring data.

        TODO
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
    ):
        """
        Get the parsed plist file data.

        TODO
        """

        if not isinstance(plist_file, str):
            raise TypeError(
                "Invalid type for plist_file, expected str, got "
                + type(plist_file).__name__
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
            raise ValueError("Unable to parse provided plist") from e

        return fmt, plist

    @staticmethod
    def __normalize_path(path: list | tuple | str | int):
        """
        Take a path list/tuple/str/int and make sure it is always a list.

        TODO
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
            if not isinstance(component, (str, int)):
                raise RuntimeError(
                    "Invalid path specified, must be made up of strings or integers"
                )

        return new_path

    @classmethod
    def create_empty_file(
        cls, plist_file: str, output_format: str = "xml", data_type: str = "dict"
    ):
        """
        Create a new, valid plist file with an empty root entry.

        TODO
        """

        file_format_spec = cls.__get_file_format_from_name(output_format)
        entry_data_type_spec = cls.__get_entry_data_type_by_name(data_type)

        if entry_data_type_spec["name"] not in ("bool", "date", "integer", "real"):
            empty_value = entry_data_type_spec["class"]()
        else:
            raise ValueError(
                "Cannot create an empty plist with the "
                + entry_data_type_spec["name"]
                + " root entry data type"
            )

        with open(plist_file, "xb") as fp:
            _plistlib.dump(empty_value, fp, fmt=file_format_spec["type"])

    @classmethod
    def convert_bytes(
        cls,
        plist_bytes: bytes | bytearray,
        output_format: str = "xml",
    ):
        """
        Convert a given plist representation to the specified format.

        TODO
        """

        file_format_spec = cls.__get_file_format_from_name(output_format)

        plist_format, plist_data = cls.__parse_bytes(plist_bytes)

        if plist_format != output_format:
            plist = _plistlib.dumps(
                plist_data, fmt=file_format_spec["type"], sort_keys=False
            )
        else:
            plist = plist_bytes

        return plist

    @classmethod
    def convert_file(
        cls,
        plist_file: str,
        output_format: str = "xml",
    ):
        """
        Convert a given plist file to the specified format.

        TODO
        """

        file_format_spec = cls.__get_file_format_from_name(output_format)

        plist_format, plist_data = cls.__parse_file(plist_file)

        if plist_format != output_format:
            with open(plist_file, "wb") as fp:
                _plistlib.dump(
                    plist_data, fp, fmt=file_format_spec["type"], sort_keys=False
                )

    def get_plist_info_format(
        self,
    ):
        """
        Get the format of the parsed plist_info used to instantiate the class.

        TODO
        """

        return self.__plist_info_format

    def get_plist_info(
        self,
    ):
        """
        Get the plist_info used to instantiate the class.


        TODO
        """

        return self.__plist_info

    def get_data(self):
        """
        Get the parsed plist data.

        Will return None if unable to parse the file.

        TODO
        """

        return self.__get_variable_value_copy(self.__plist_data)

    def is_valid(self):
        """
        Check if a plist file is a valid plist.

        TODO
        """

        return self.__plist_data is not None

    def exists(self, path: list | tuple | str | int = None):
        """
        Check if an entry exists.

        TODO
        """

        path = self.__normalize_path(path)

        try:
            self.__get(self.__plist_data, path)
        except KeyError:
            return False

        return True

    @classmethod
    def __get(cls, plist_data, path: list):
        """
        Get the python data representation of a plist entry.

        TODO
        """

        if not isinstance(path, list):
            raise TypeError("Path must be specified as a list")

        entry = plist_data
        string_path = ""

        for path_part in path:
            if string_path != "":
                string_path += "."
            string_path += str(path_part).replace(".", r"\.")

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
                    path_part = str(path_part)
                    entry = entry[path_part]
                except Exception as e:
                    raise KeyError(key_error_text) from e
            elif isinstance(entry, list):
                try:
                    path_part = int(path_part)
                    entry = entry[path_part]
                except Exception as e:
                    raise KeyError(key_error_text) from e
            else:
                raise KeyError(key_error_text)

        return entry

    def get(self, path: list | tuple | str | int = None):
        """
        Get the python data representation of a plist entry.

        TODO
        """

        path = self.__normalize_path(path)

        entry = self.__get(self.__plist_data, path)

        return self.__get_variable_value_copy(entry)

    def get_type(self, path: list | tuple | str | int = None):
        """
        Get the plist type of the entry.

        TODO
        """

        path = self.__normalize_path(path)

        entry = self.__get(self.__plist_data, path)

        entry_data_type_spec = self.__get_entry_data_type_by_class(entry)

        return entry_data_type_spec["name"]

    def get_dict_keys(self, path: list | tuple | str | int = None):
        """
        Get the keys of the specified dict entry.

        TODO
        """

        path = self.__normalize_path(path)

        entry = self.__get(self.__plist_data, path)

        entry_data_type_spec = self.__get_entry_data_type_by_class(entry)

        if entry_data_type_spec["name"] != "dict":
            raise ValueError("Specified entry is not a dict")

        return tuple(entry.keys())

    def get_array_length(self, path: list | tuple | str | int = None):
        """
        Get the length of the specified array entry.

        TODO
        """

        path = self.__normalize_path(path)

        entry = self.__get(self.__plist_data, path)

        entry_data_type_spec = self.__get_entry_data_type_by_class(entry)

        if entry_data_type_spec["name"] != "array":
            raise ValueError("Specified entry is not an array")

        return len(entry)

    def print(
        self,
        output_format: str = "xml",
        output_sort: bool = False,
        path: list | tuple | str | int = None,
    ):
        """
        Print the plist to the screen formatted in the specified format \
        starting at the specified entry.

        TODO
        """

        if not isinstance(output_sort, bool):
            raise TypeError(
                "Invalid data type for output_sort, expected bool got "
                + type(output_sort).__name__
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
            plist_data, fmt=file_format_spec["type"], sort_keys=output_sort
        )

        if output_format == "xml":
            output = output.decode()

        print(output)

    def write(
        self,
        output_file: str = None,
        output_format: str = None,
        output_sort: bool = False,
        path: list | tuple | str | int = None,
    ):
        """
        Write the plist to the specified file.

        The entire plist will be written to the file unless a path value is
        provided, then that entry down will be used to create the plist file.

        If no output_format is given, then the file will be written in the format
        from which the plist was originally parsed.

        If no output_file is given, this will write to the file used to instantiate
        this object. If a plist representation was used to instantiate this object,
        then a RuntimeError is thrown.


        TODO
        """

        if not isinstance(output_sort, bool):
            raise TypeError(
                "Invalid data type for output_sort, expected bool got "
                + type(output_sort).__name__
            )

        if output_file is None:
            if self.__plist_info_type == self.PLIST_INFO_TYPE_FILE:
                output_file = self.__plist_info
            elif self.__plist_info_type == self.PLIST_INFO_TYPE_REPRESENTATION:
                raise RuntimeError(
                    "Object instantiated from plist representation, value for output_file required"
                )

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
                plist_data, tmp, fmt=file_format_spec["type"], sort_keys=output_sort
            )

            with open(output_file, "wb") as fp:
                # Reset temporary file's read/write position to beginning of file
                tmp.seek(0)
                fp.write(tmp.read())

    def insert(self, path: list | tuple | str | int, value):
        """
        Insert a new entry into the plist

        TODO
        """

        root_data_type_spec = self.__get_entry_data_type_by_class(self.__plist_data)

        if root_data_type_spec["name"] not in ("array", "dict"):
            raise KeyError(
                "Cannot insert into a plist with a root type that is not array or dict"
            )

        path = self.__normalize_path(path)

        if len(path) == 0:
            raise KeyError("Insertion path must be provided")

        try:
            self.__get_entry_data_type_by_class(value)
        except Exception as e:
            raise TypeError("Invalid data type for provided value") from e

        if self.exists(path):
            raise RuntimeError("An entry at this path already exists")

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
                    "Inserting into an array requires an integer path spec"
                ) from e

            if insertion_key > len(parent_entry):
                raise IndexError("Array insertions must be done at the last entry")
        elif parent_entry_data_type_spec["name"] == "dict":
            try:
                insertion_key = str(insertion_key)
            except Exception as e:
                raise ValueError(
                    "Inserting into a dict requires a string path spec"
                ) from e

        try:
            # Have plistlib process the value to see if it is valid
            _plistlib.dumps(value)
        except Exception as e:
            raise TypeError("Value to insert is not valid plist data") from e

        if parent_entry_data_type_spec["name"] == "array":
            parent_entry.insert(insertion_key, value)
        elif parent_entry_data_type_spec["name"] == "dict":
            parent_entry[insertion_key] = value

    def insert_array_append(self, path: list | tuple | str | int, value):
        """
        Insert a value into an array by appending it to the end of the array.

        If the path specified does not exist, an empty array will attempt to be
        created at the specified path. The parent of the specified path must
        already exist for this to work.

        TODO
        """

        root_data_type_spec = self.__get_entry_data_type_by_class(self.__plist_data)

        if root_data_type_spec["name"] not in ("array", "dict"):
            raise KeyError(
                "Cannot insert into a plist with a root type that is not array or dict"
            )

        path = self.__normalize_path(path)

        if len(path) == 0:
            raise KeyError("Insertion path must be provided")

        array_data_type_spec = self.__get_entry_data_type_by_name("array")

        created_target_array = False
        if not self.exists(path):
            self.insert(path, array_data_type_spec["class"]())
            created_target_array = True

        try:
            entry = self.__get(self.__plist_data, path)

            entry_data_type_spec = self.__get_entry_data_type_by_class(entry)

            if entry_data_type_spec["name"] != "array":
                raise RuntimeError("The provided path must specify an array entry")

            path.append(len(entry))

            self.insert(path, value)
        except Exception:
            if created_target_array:
                self.delete(path)

            raise

    def update(self, path: list | tuple | str | int, value):
        """
        Update an existing entry in the plist.

        Updates are allowed to change the data type of the entry.

        TODO
        """

        root_data_type_spec = self.__get_entry_data_type_by_class(self.__plist_data)

        path = self.__normalize_path(path)

        if root_data_type_spec["name"] not in ("array", "dict") and len(path) > 0:
            raise KeyError(
                "Update path cannot be provided for root data types that are not array or dict"
            )

        try:
            self.__get_entry_data_type_by_class(value)
        except Exception as e:
            raise TypeError("Invalid data type for provided value") from e

        if not self.exists(path):
            raise RuntimeError("An entry does not exist at this path")

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
                parent_entry
            )

            if parent_entry_data_type_spec["name"] == "array":
                update_key = int(update_key)
            elif parent_entry_data_type_spec["name"] == "dict":
                update_key = str(update_key)

            parent_entry[update_key] = value

    def delete(self, path: list | tuple | str | int):
        """
        Delete an entry from a plist.

        TODO
        """

        root_data_type_spec = self.__get_entry_data_type_by_class(self.__plist_data)

        if root_data_type_spec["name"] not in ("array", "dict"):
            raise KeyError(
                "Delete cannot be preformed on root data types that are not array or dict"
            )

        path = self.__normalize_path(path)

        if len(path) == 0:
            raise RuntimeError("Cannot delete plist root entry")

        if not self.exists(path):
            raise RuntimeError("An entry does not exist at this path")

        parent_path = list(path)
        delete_key = parent_path.pop()
        parent_entry = self.__get(self.__plist_data, parent_path)

        parent_data_type_spec = self.__get_entry_data_type_by_class(parent_entry)

        if parent_data_type_spec["name"] == "array":
            delete_key = int(delete_key)
        elif parent_data_type_spec["name"] == "dict":
            delete_key = str(delete_key)

        del parent_entry[delete_key]

    def upsert(self, path: list | tuple | str | int, value):
        """
        Insert or update a plist entry depending on if the entry specified
        by the path already exists or not.

        TODO
        """

        path = self.__normalize_path(path)

        if not self.exists(path):
            self.insert(path, value)
        else:
            self.update(path, value)

    def __merge(
        self, source_entry, target_path: list | tuple | str | int, overwrite: bool
    ):
        """
        Recursively merge python data (source_entry) into the current plist.

        TODO
        """

        target_path = self.__normalize_path(target_path)

        ########################################################################
        ## Handle special root update cases
        ########################################################################

        root_data_type_spec = self.__get_entry_data_type_by_class(self.__plist_data)

        if len(target_path) > 0 and root_data_type_spec["name"] not in (
            "array",
            "dict",
        ):
            raise RuntimeError("Cannot merge into child of non-collection root plist")
        if len(target_path) == 0 and root_data_type_spec["name"] not in (
            "array",
            "dict",
        ):
            # Merging into root
            if overwrite:
                # Merging into a non-collection type at the root is the same
                # as updating to the given value. So just do this and be done
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
        source_data_spec = self.__get_entry_data_type_by_class(source_entry)

        if target_data_spec["name"] not in ("array", "dict") or source_data_spec[
            "name"
        ] not in ("array", "dict"):
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
        source_plist_info_type: str,
        source_plist_info: str | bytes | bytearray,
        source_path: list | tuple | str | int = None,
        target_path: list | tuple | str | int = None,
        overwrite: bool = True,
    ):
        """
        Merge in a plist file (or a subset of a plist file) to the current
        plist.

        TODO
        """

        ########################################################################
        ##  Parameter verifications
        ########################################################################

        if not isinstance(overwrite, bool):
            raise TypeError(
                "Invalid overwrite type. Execpted boolean (bool), got "
                + type(overwrite).__name__
            )

        if source_plist_info_type not in self.__PLIST_INFO_TYPES:
            raise RuntimeError(
                'Invalid source_plist_info_type: "' + str(source_plist_info_type) + '"'
            )

        if source_plist_info_type == self.PLIST_INFO_TYPE_REPRESENTATION:
            _, source_plist = self.__parse_bytes(source_plist_info)
        elif source_plist_info_type == self.PLIST_INFO_TYPE_FILE:
            _, source_plist = self.__parse_file(source_plist_info)
        else:
            raise NameError(
                'JML Invalid source_plist_info_type: "'
                + str(source_plist_info_type)
                + '"'
            )

        source_path = self.__normalize_path(source_path)

        try:
            source_entry = self.__get(source_plist, source_path)
        except Exception as e:
            raise RuntimeError("Invalid source_path") from e

        ########################################################################
        ##  Merge
        ########################################################################
        self.__merge(source_entry, target_path, overwrite)
