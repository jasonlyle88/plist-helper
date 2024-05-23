"""
datetime:   Used to work with plist date type data.
os.path:    Used to work with os files and pathing.
plistlib:   Provide ability to work with Apple plist files.
tempfile:   Used to manage temporary files for the operating systems.
"""
import datetime
import os.path
import plistlib
import tempfile

class PlistHelper:
    """
    Sensible management of Apple plist files.

    Designed to replace the need for the "PlistBuddy", "plutil", and "defaults" utilities.

    This class utilizes the plistlib builtin module to enable management of plist files.

    This class can be instantiated with a string argument that is a file path.
    The file path can be absolute or relative to the current working directory.

    It is also possible to instantiate this class with a bytestring that represents
    the content of a plist file.

    NOTES:
        This class, as well as the underlying plistlib, is unable to handle plist files
        that contain empty 'bool', 'date', 'integer', or 'real' data elements.

    TODO
    """

    __INFO_TYPE_FILE = 'file'
    __INFO_TYPE_REPRESENTATION = 'representation'

    ENTRY_DATA_TYPES = (
        {'name': 'array',   'class': list},
        {'name': 'bool',    'class': bool},
        {'name': 'data',    'class': bytes},
        {'name': 'date',    'class': datetime.datetime},
        {'name': 'dict',    'class': dict},
        {'name': 'integer', 'class': int},
        {'name': 'real',    'class': float},
        {'name': 'string',  'class': str}
    )

    FILE_FORMATS = (
        {'name': 'binary',  'type': plistlib.FMT_BINARY},
        {'name': 'xml',     'type': plistlib.FMT_XML}
    )

    def __init__(
        self,
        plist_info: str | bytes
    ):
        # List of instance attributes before initialization
        self.__plist_info_type = None
        self.__plist_info = None
        self.__plist_data = None

        if not isinstance(plist_info, (str, bytes)):
            raise TypeError(
                'Invalid plist_info type. Execpted string (str) or bytestring (bytes), got '
                + type(plist_info)
            )

        if isinstance(plist_info, bytes):
            self.__plist_info_type = self.__INFO_TYPE_REPRESENTATION
        if isinstance(plist_info, str):
            self.__plist_info_type = self.__INFO_TYPE_FILE

            plist_info = os.path.realpath(plist_info)
            if not os.path.isfile(plist_info):
                raise RuntimeError('Cannot find plist file: ' + plist_info)

        self.__plist_info = plist_info
        self.__plist_data = self.__parse(plist_info)


    def __str__(
        self
    ):
        return plistlib.dumps(self.__plist_data).decode()


    def __repr__(
        self
    ):
        if self.__plist_info_type == self.__INFO_TYPE_FILE:
            return 'Plist("' + self.__plist_info + '")'
        elif self.__plist_info_type == self.__INFO_TYPE_REPRESENTATION:
            return 'Plist(b"' + self.__plist_info.replace('"', r'\"') + '")'


    @staticmethod
    def __get_variable_value_copy(
        var
    ):
        """
        Get a copy of a variable as a value copy, not a reference copy

        TODO
        """

        if hasattr(var, 'copy'):
            return var.copy()
        else:
            return var


    @classmethod
    def __get_file_format(
        cls,
        file_format: str
    ):
        """
        Get a plist file format specification based on theprovided  file format name.

        TODO
        """

        result = [
            item for item in cls.FILE_FORMATS
            if item['name'].lower() == file_format.lower()
        ]
        num_results = len(result)

        if num_results == 0:
            raise ValueError('Invalid file format specified: "' + file_format + '"')
        if num_results > 1:
            raise OverflowError('File formats has duplicate names, developer action required')

        return result[0]


    @classmethod
    def __get_entry_data_type_name(
        cls,
        data_type_name: str
    ):
        """
        Get a plist data type specification based on the provided data type name

        TODO
        """

        result = [
            item for item in cls.ENTRY_DATA_TYPES
            if item['name'].lower() == data_type_name.lower()
        ]
        num_results = len(result)

        if num_results == 0:
            raise ValueError('Invalid entry data type specified: "' + data_type_name + '"')
        if num_results > 1:
            raise OverflowError('Entry data types has duplicate names, developer action required')

        return result[0]


    @classmethod
    def __get_entry_data_type_class(
        cls,
        data: object
    ):
        """
        Get a plist data type specification based on the data type class of the provided object.

        TODO
        """

        result = [
            item for item in cls.ENTRY_DATA_TYPES
            if isinstance(data, item['class'])
        ]
        num_results = len(result)

        if num_results == 0:
            raise ValueError('Invalid entry data type specified: "' + type(data) + '"')
        if num_results > 1:
            raise OverflowError(
                'Entry data types has duplicate class types, developer action required'
            )

        return result[0]


    @staticmethod
    def __parse_bytestring(
        plist_bytestring: bytes
    ):
        """
        Get the parsed plist bytestring data.

        TODO
        """

        if not isinstance(plist_bytestring, bytes):
            raise TypeError(
                'Invalid type for plist_bytestring, expected bytes, got ' + type(plist_bytestring)
            )

        try:
            return plistlib.loads(plist_bytestring)
        except Exception as e:
            raise ValueError('Unable to parse provided plist') from e


    @staticmethod
    def __parse_file(
        plist_file: str
    ):
        """
        Get the parsed plist file data.

        TODO
        """

        if not isinstance(plist_file, str):
            raise TypeError('Invalid type for plist_file, expected str, got ' + type(plist_file))

        try:
            with open(plist_file, 'rb') as fp:
                return plistlib.load(fp)
        except OSError as e:
            raise ValueError('Unable to open provided file') from e
        except Exception as e:
            raise ValueError('Unable to parse provided plist') from e


    def __parse(
        self,
        plist: str | bytes
    ):
        """
        Get the parsed plist data from a bytestring or a file.

        TODO
        """

        if self.__plist_info_type == self.__INFO_TYPE_REPRESENTATION:
            return self.__parse_bytestring(plist)
        if self.__plist_info_type == self.__INFO_TYPE_FILE:
            return self.__parse_file(plist)

        raise RuntimeError('Unknown info type, developer intervention required')


    @staticmethod
    def __normalize_path(
        path: list | tuple | str | int
    ):
        """
        Take a path list/tuple/str/int and make sure it is always a list

        TODO
        """

        new_path = None

        if path is None:
            new_path = list()
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
                raise RuntimeError('Invalid path specified, must be made up of strings or integers')

        return new_path


    @classmethod
    def create_empty_file(
        cls,
        plist_file: str,
        output_file_format: str = 'xml',
        root_entry_data_type: str = 'dict'
    ):
        """
        Create a new, valid plist file with an empty root entry

        TODO
        """

        file_format_spec = cls.__get_file_format(output_file_format)
        entry_data_type_spec = cls.__get_entry_data_type_name(root_entry_data_type)

        if entry_data_type_spec['name'] not in ('bool', 'date', 'integer', 'real'):
            empty_value = entry_data_type_spec['class']()
        else:
            raise ValueError(
                'Cannot create an empty plist with the ' +
                entry_data_type_spec['name'] + ' root entry data type'
            )

        with open(plist_file, 'xb') as fp:
            plistlib.dump(empty_value, fp, fmt=file_format_spec['type'])


    @classmethod
    def convert_file(
        cls,
        plist_file: str,
        converted_file_format: str = 'xml'
    ):
        """
        Convert a given plist to the specified format.

        TODO
        """
        file_format_spec = cls.__get_file_format(converted_file_format)

        plist_data = cls.__parse_file(plist_file)

        with open(plist_file, 'wb') as fp:
            plistlib.dump(plist_data, fp, fmt=file_format_spec['type'])


    def get_plist_info(
        self
    ):
        """
        Get the plist_info used to instantiate the class.


        TODO
        """

        return self.__plist_info


    def get_data(
        self
    ):
        """
        Get the parsed plist data.

        Will return None if unable to parse the file.

        TODO
        """

        return self.__get_variable_value_copy(self.__plist_data)


    def is_valid(
        self
    ):
        """
        Check if a plist file is a valid plist

        TODO
        """

        return self.__plist_data is not None


    def entry_exists(
        self,
        path: list | tuple | str | int = None
    ):
        """
        Check if an entry exists

        TODO
        """

        path = self.__normalize_path(path)

        try:
            self.__get_entry(path)
        except KeyError:
            return False

        return True


    def __get_entry(
        self,
        path: list
    ):
        """
        Get the python data representation of a plist entry

        TODO
        """

        if not isinstance(path, list):
            raise TypeError('Path must be specified as a list')

        entry = self.__plist_data
        string_path = ''

        for path_part in path:
            if string_path != '':
                string_path += '.'
            string_path += str(path_part).replace('.', r'\.')

            entry_data_type_spec = self.__get_entry_data_type_class(entry)

            key_error_text = '('+entry_data_type_spec['name']+') Cannot access "'+string_path+'"'

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


    def get_entry(
        self,
        path: list | tuple | str | int = None
    ):
        """
        Get the python data representation of a plist entry

        TODO
        """

        path = self.__normalize_path(path)

        entry = self.__get_entry(path)

        return self.__get_variable_value_copy(entry)


    def get_entry_type(
        self,
        path: list | tuple | str | int = None
    ):
        """
        Get the plist type of the entry.

        TODO
        """

        path = self.__normalize_path(path)

        entry = self.__get_entry(path)

        entry_data_type_spec = self.__get_entry_data_type_class(entry)

        return entry_data_type_spec['name']


    def get_dict_keys(
        self,
        path: list | tuple | str | int = None
    ):
        """
        Get the keys of the specified dict entry

        TODO
        """

        path = self.__normalize_path(path)

        entry = self.__get_entry(path)

        entry_data_type_spec = self.__get_entry_data_type_class(entry)

        if entry_data_type_spec['name'] != 'dict':
            raise ValueError('Specified entry is not a dict')

        return tuple(entry.keys())


    def get_array_length(
        self,
        path: list | tuple | str | int = None
    ):
        """
        Get the length of the specified array entry

        TODO
        """

        path = self.__normalize_path(path)

        entry = self.__get_entry(path)

        entry_data_type_spec = self.__get_entry_data_type_class(entry)

        if entry_data_type_spec['name'] != 'array':
            raise ValueError('Specified entry is not an array')

        return len(entry)


    def print(
        self,
        output_format: str = 'xml',
        path: list | tuple | str | int = None
    ):
        """
        Print the plist to the screen formatted in the specified format and
        starting at the specified entry

        TODO
        """

        path = self.__normalize_path(path)

        file_format_spec = self.__get_file_format(output_format)

        plist_data = None
        if path is None:
            plist_data = self.__plist_data
        else:
            plist_data = self.__get_entry(path)

        output = plistlib.dumps(plist_data, fmt=file_format_spec['type'])

        if output_format == 'xml':
            output = output.decode()

        print(output)


    def write(
        self,
        output_file: str = None,
        output_format: str = 'xml',
        path: list | tuple | str | int = None
    ):
        """
        Write the plist to the specified file.

        The entire plist will be written to the file unless a path value is
        provided, then that entry down will be used to create the plist file.

        If no output file is given, this will write to the file used to instantiate
        this object. If a plist representation was used to instantiate this object,
        then a RuntimeError is thrown.


        TODO
        """

        if output_file is None:
            if self.__plist_info_type == self.__INFO_TYPE_FILE:
                output_file = self.__plist_info
            elif self.__plist_info_type == self.__INFO_TYPE_REPRESENTATION:
                raise RuntimeError(
                    'Object instantiated from plist representation, value for output_file required'
                )

        file_format_spec = self.__get_file_format(output_format)

        path = self.__normalize_path(path)

        plist_data = None
        if path is None:
            plist_data = self.__plist_data
        else:
            plist_data = self.__get_entry(path)

        # Use a temporary file in case there is any issue converting the data.
        # This prevents the target file from being in a bad state if
        # the plist conversion fails
        with tempfile.NamedTemporaryFile() as tmp:
            plistlib.dump(plist_data, tmp, fmt=file_format_spec['type'])

            with open(output_file, 'wb') as fp:
                # Reset temporary file's read/write position to beginning of file
                tmp.seek(0)
                fp.write(tmp.read())


    def insert_entry(
        self,
        path: list | tuple | str | int,
        value
    ):
        """
        Insert a new entry into the plist

        TODO
        """

        root_data_type_spec = self.__get_entry_data_type_class(self.__plist_data)

        if root_data_type_spec['name'] not in ('array', 'dict'):
            raise KeyError(
                'Cannot insert into a plist with a root type that is not array or dict'
            )

        path = self.__normalize_path(path)

        if len(path) == 0:
            raise KeyError('Insertion path must be provided')

        try:
            value_data_type_spec = self.__get_entry_data_type_class(value)
        except Exception as e:
            raise TypeError('Invalid data type for provided value') from e

        if self.entry_exists(path):
            raise RuntimeError('An entry at this path already exists')

        parent_path=list(path)
        insertion_key_name = parent_path.pop()

        try:
            parent_entry = self.__get_entry(parent_path)
        except KeyError as e:
            raise KeyError('Cannot get entry parent') from e

        parent_entry_backup = parent_entry.copy()

        parent_entry_data_type_spec = self.__get_entry_data_type_class(parent_entry)

        if parent_entry_data_type_spec['name'] not in ('dict', 'array'):
            raise RuntimeError('Cannot insert into entry that is not an array or dict')

        if parent_entry_data_type_spec['name'] == 'array':
            try:
                insertion_key_name = int(insertion_key_name)
            except Exception as e:
                raise ValueError('Inserting into an array requires an integer path spec') from e

            if insertion_key_name > len(parent_entry):
                raise IndexError('Array insertions must be done at the last element')
        elif parent_entry_data_type_spec['name'] == 'dict':
            try:
                insertion_key_name = str(insertion_key_name)
            except Exception as e:
                raise ValueError('Inserting into a dict requires a string path spec') from e

        try:
            if value_data_type_spec['name'] in ('array', 'dict'):
                parent_entry[insertion_key_name] = value_data_type_spec['class']()
                if len(value) > 0:
                    if value_data_type_spec['name'] == 'dict':
                        for attr in value:
                            new_path = list(path)
                            new_path.append(attr)
                            new_value = value[attr]
                            self.insert_entry(new_path, new_value)
                    if value_data_type_spec['name'] == 'array':
                        for idx, attr in enumerate(value):
                            new_path = list(path)
                            new_path.append(idx)
                            new_value = attr
                            self.insert_entry(new_path, new_value)
            else:
                if parent_entry_data_type_spec['name'] == 'array':
                    parent_entry.insert(insertion_key_name, value)
                elif parent_entry_data_type_spec['name'] == 'dict':
                    parent_entry[insertion_key_name] = value
        except Exception:
            # Undo any changes since an error occurred
            if parent_entry_data_type_spec['name'] in ['array', 'dict']:
                parent_entry.clear()

                if parent_entry_data_type_spec['name'] == 'array':
                    parent_entry.extend(parent_entry_backup)
                elif parent_entry_data_type_spec['name'] == 'dict':
                    parent_entry.update(parent_entry_backup)

            raise


    def insert_array_append(
        self,
        path: list | tuple | str | int,
        value
    ):
        """
        Insert a value into an array by appending it to the end of the array.

        If the path specified does not exist, an empty array will attempt to be
        created at the specified path. The parent of the specified path must
        already exist for this to work.

        TODO
        """

        root_data_type_spec = self.__get_entry_data_type_class(self.__plist_data)

        if root_data_type_spec['name'] not in ('array', 'dict'):
            raise KeyError(
                'Cannot insert into a plist with a root type that is not array or dict'
            )

        path = self.__normalize_path(path)

        if len(path) == 0:
            raise KeyError('Insertion path must be provided')

        array_data_type_spec = self.__get_entry_data_type_name('array')

        created_target_array=False
        if not self.entry_exists(path):
            self.insert_entry(path, array_data_type_spec['class']())
            created_target_array=True

        try:
            entry = self.__get_entry(path)

            entry_data_type_spec = self.__get_entry_data_type_class(entry)

            if entry_data_type_spec['name'] != 'array':
                raise RuntimeError('The provided path must specify an array entry')

            path.append(len(entry))

            self.insert_entry(path, value)
        except Exception:
            if created_target_array:
                pass # TODO: call delete_entry on the `path`

            raise


    def update_entry(
        self,
        path: list | tuple | str | int,
        value
    ):
        """
        Update an existing entry in the plist.

        Updates are allowed to change the data type of the entry.

        TODO
        """

        root_data_type_spec = self.__get_entry_data_type_class(self.__plist_data)

        path = self.__normalize_path(path)

        if root_data_type_spec['name'] not in ('array', 'dict') and len(path) > 0:
            raise KeyError(
                'Update path cannot be provided for root data types that are not array or dict'
            )

        if root_data_type_spec['name'] in ('array', 'dict') and len(path) == 0:
            raise KeyError(
                'Update path must be provided for root data types thata re array or dict'
            )

        try:
            value_data_type_spec = self.__get_entry_data_type_class(value)
        except Exception as e:
            raise TypeError('Invalid data type for provided value') from e

        if self.entry_exists(path):
            raise RuntimeError('An entry at this path already exists')
