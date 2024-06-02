"""Command line interface for PlistHelper to provide more universal access to plist management."""

from __future__ import annotations

import argparse as _argparse
import contextlib as _contextlib
import datetime as _datetime
import sys as _sys
import textwrap as _textwrap
import typing as _typing

from plist_helper.helper import PlistHelper as _PlistHelper

__TRUTHY_VALUES = [
    "t",
    "true",
    "y",
    "yes",
    "1",
]

__ALL_ARGUMENTS = {
    "data_type": {
        "args": {"-t", "--data-type"},
        "kwargs": {
            "dest": "value_data_type",
            "help": "The data type of the provided value",
            "choices": _PlistHelper.ENTRY_DATA_TYPES.keys(),
            "default": "dict",
            "required": True,
        },
    },
    "entry": {
        "args": {"-e", "--entry"},
        "kwargs": {
            "dest": "path",
            "help": """The path to the object to print. \
                Can be provided 0-n times to specify root or any child""",
            "action": "append",
            "default": [],
        },
    },
    "format": {
        "args": {"-f", "--format"},
        "kwargs": {
            "dest": "output_format",
            "help": "The format in which to print the plist",
            "choices": _PlistHelper.FILE_FORMATS.keys(),
            "default": "xml",
        },
    },
    "plist": {
        "args": {"-p", "--plist"},
        "kwargs": {
            "dest": "plist",
            "help": "The plist to act upon",
            "type": str,
            "required": True,
        },
    },
    "root_data_type": {
        "args": {"-t", "--data-type"},
        "kwargs": {
            "dest": "data_type",
            "help": "The data type of the root of the plist file",
            "choices": _PlistHelper.ENTRY_DATA_TYPES.keys(),
            "default": "dict",
        },
    },
    "sort": {
        "args": {"-s", "--sort"},
        "kwargs": {
            "dest": "output_sort",
            "help": "Sort keys in alphabetical order",
            "action": "store_true",
        },
    },
    "value": {
        "args": {"-v", "--value"},
        "kwargs": {
            "dest": "value",
            "help": "Data value to use for the action",
        },
    },
}

__GLOBAL_ARGUMENTS = (__ALL_ARGUMENTS["plist"],)

# DONE: convertFile
# DONE: createFile
# DONE: delete
# DONE: exists
# DONE: getArrayLength
# DONE: getDictKeys
# DONE: getType
# DONE: getValue
# TODO(@jlyle): insert - CLI setup, need to test everything here
# TODO(@jlyle): insertArrayAppend
# TODO(@jlyle): merge
# DONE: print
# TODO(@jlyle): update
# TODO(@jlyle): upsert

__ACTIONS = {
    "convertFile": {
        "main_method": _PlistHelper.convert_file,
        "main_method_post": None,
        "action_help": None,
        "argument_definitions": (__ALL_ARGUMENTS["format"],),
    },
    "createFile": {
        "main_method": _PlistHelper.create_empty_file,
        "main_method_post": None,
        "action_help": None,
        "argument_definitions": (
            __ALL_ARGUMENTS["format"],
            __ALL_ARGUMENTS["root_data_type"],
        ),
    },
    "delete": {
        "main_method": _PlistHelper.delete,
        "main_method_post": "write_to_file",
        "action_help": None,
        "argument_definitions": (__ALL_ARGUMENTS["entry"],),
    },
    "exists": {
        "main_method": _PlistHelper.exists,
        "main_method_post": "output_result",
        "action_help": None,
        "argument_definitions": (__ALL_ARGUMENTS["entry"],),
    },
    "getArrayLength": {
        "main_method": _PlistHelper.get_array_length,
        "main_method_post": "output_result",
        "action_help": None,
        "argument_definitions": (__ALL_ARGUMENTS["entry"],),
    },
    "getDictKeys": {
        "main_method": _PlistHelper.get_dict_keys,
        "main_method_post": "output_list",
        "action_help": None,
        "argument_definitions": (__ALL_ARGUMENTS["entry"],),
    },
    "getType": {
        "main_method": _PlistHelper.get_type,
        "main_method_post": "output_result",
        "action_help": None,
        "argument_definitions": (__ALL_ARGUMENTS["entry"],),
    },
    "getValue": {
        "main_method": _PlistHelper.get,
        "main_method_post": "output_result",
        "action_help": None,
        "argument_definitions": (__ALL_ARGUMENTS["entry"],),
    },
    "insert": {
        "main_method": _PlistHelper.insert,
        "main_method_post": "write_to_file",
        "action_help": None,
        "argument_definitions": (
            __ALL_ARGUMENTS["entry"],
            __ALL_ARGUMENTS["data_type"],
            __ALL_ARGUMENTS["value"],
        ),
    },
    "print": {
        "main_method": _PlistHelper.print,
        "main_method_post": None,
        "action_help": None,
        "argument_definitions": (
            __ALL_ARGUMENTS["format"],
            __ALL_ARGUMENTS["sort"],
            __ALL_ARGUMENTS["entry"],
        ),
    },
}


def _f() -> None:
    pass


__TYPES = _argparse.Namespace(
    function=type(_f),
    classmethod=classmethod,
    staticmethod=staticmethod,
)


def __print_message(message: str, file: _typing.TextIO) -> None:
    """Print a message to a file-like object (e.g. an IO stream)."""
    if message:
        file = file or _sys.stdout

        with _contextlib.suppress(AttributeError, OSError):
            file.write(message)


def __exit(status: int = 0, message: str | None = None) -> None:
    """Exit with the specified system code and optionally print out a messsage.

    Will print messages to stdout if exit status = 0.
    Otherwise messages are printed to stderr.
    """
    if message:
        stream = _sys.stdout if status == 0 else _sys.stderr

        __print_message(message, stream)
    _sys.exit(status)


def __get_class_from_method_handle(handle):
    # Extract the qualified name of the method
    qualname = handle.__qualname__

    # Split the qualified name to get the class name
    class_name = qualname.split(".<locals>", 1)[0].rsplit(".", 1)[0]

    # Get the module in which the class is defined
    module = _sys.modules[handle.__module__]

    # Retrieve the class object from the module
    return getattr(module, class_name)


def __get_original_descriptor_from_handle(handle):
    cls = __get_class_from_method_handle(handle)
    for name, member in cls.__dict__.items():
        if getattr(cls, name) == handle:
            return member
    return None


def __setup_argparse() -> _argparse.ArgumentParser:
    """Set up the argparse parser to be used for the plist_helper CLI."""
    parent_parser = _argparse.ArgumentParser(
        prog="plistHelper",
        formatter_class=_argparse.RawDescriptionHelpFormatter,
        description=_textwrap.dedent(_PlistHelper.__doc__),
    )

    child_parser = parent_parser.add_subparsers(
        dest="action_name",
        metavar="action",
        title="Actions",
    )

    for action_name, action in __ACTIONS.items():
        try:
            action_help = action["action_help"]
        except KeyError:
            action_help = None

        if action_help is None:
            # Use the first line of the docstring as the default CLI action help
            action_help = _textwrap.dedent(action["main_method"].__doc__.strip()).split(
                "\n",
                1,
            )[0]

        add_parser = child_parser.add_parser(action_name, help=action_help)

        for global_argument in __GLOBAL_ARGUMENTS:
            add_parser.add_argument(
                *(global_argument["args"]),
                **(global_argument["kwargs"]),
            )

        for argument_definition in action["argument_definitions"]:
            add_parser.add_argument(
                *argument_definition["args"],
                **argument_definition["kwargs"],
            )

    return parent_parser


def __handle_arguments(args: _argparse.Namespace) -> None:
    """Handle the arguments from argparse for the plist_helper CLI."""
    # Setup a dictionary that can be used to call the main function with
    # unpacked args and kwargs
    plist_helper_args = []
    plist_helper_kwargs = vars(args).copy()

    del plist_helper_kwargs["action_name"]
    for global_argument in __GLOBAL_ARGUMENTS:
        del plist_helper_kwargs[global_argument["kwargs"]["dest"]]

    action_spec = __ACTIONS[args.action_name]

    typed_handle = __get_original_descriptor_from_handle(action_spec["main_method"])
    if isinstance(typed_handle, __TYPES.classmethod):
        plist_helper_kwargs["plist_file"] = args.plist
    elif isinstance(typed_handle, __TYPES.function):
        try:
            plist = _PlistHelper(_PlistHelper.PLIST_INFO_TYPE_FILE, args.plist)
        except Exception:
            __exit(status=101, message="Unable to open plist file\n")

        plist_helper_args = [
            plist,
        ]
    else:
        __exit(
            status=123,
            message='Action main method not recognized type: "'
            + type(typed_handle).__name__
            + '"\n',
        )

    if "value_data_type" in plist_helper_kwargs:
        # Verify parameter combinations
        value_specified = "value" in plist_helper_kwargs

        if (
            plist_helper_kwargs["value_data_type"] in ["array", "dict"]
            and value_specified
        ):
            raise RuntimeError(
                "Cannot provide a value when data type is array or dict",
            )  # TODO(@jlyle): Generic error handling needs to be done here

        if (
            plist_helper_kwargs["value_data_type"] not in ["array", "dict"]
            and not value_specified
        ):
            raise RuntimeError(
                "A value must be provided when data type an a simple data type",
            )  # TODO(@jlyle): Generic error handling needs to be done here

        if not value_specified:
            plist_helper_kwargs["value"] = ""

        # Attempt to convert the provided value to the appropriate python type
        # based on the provided data type
        if plist_helper_kwargs["value_data_type"] == "array":
            plist_helper_kwargs["value"] = []
        elif plist_helper_kwargs["value_data_type"] == "bool":
            plist_helper_kwargs["value"] = (
                plist_helper_kwargs["value"].strip().lower() in __TRUTHY_VALUES
            )
        elif plist_helper_kwargs["value_data_type"] == "data":
            plist_helper_kwargs["value"] = plist_helper_kwargs["value"].encode()
        elif plist_helper_kwargs["value_data_type"] == "date":
            try:
                plist_helper_kwargs["value"] = _datetime.datetime.fromisoformat(
                    plist_helper_kwargs["value"],
                )
            except ValueError as e:
                raise e  # TODO(@jlyle): Generic error handling needs to be done here
        if plist_helper_kwargs["value_data_type"] == "dict":
            plist_helper_kwargs["value"] = {}
        elif plist_helper_kwargs["value_data_type"] == "integer":
            try:
                plist_helper_kwargs["value"] = int(plist_helper_kwargs["value"])
            except ValueError as e:
                raise e  # TODO(@jlyle): Generic error handling needs to be done here
        elif plist_helper_kwargs["value_data_type"] == "real":
            try:
                plist_helper_kwargs["value"] = float(plist_helper_kwargs["value"])
            except ValueError as e:
                raise e  # TODO(@jlyle): Generic error handling needs to be done here
        elif plist_helper_kwargs["value_data_type"] == "string":
            pass  # Value will already be a string, nothing to do

        del plist_helper_kwargs["value_data_type"]

    result = None
    execution_exception = None
    try:
        result = action_spec["main_method"](*plist_helper_args, **plist_helper_kwargs)
    except Exception as e:
        execution_exception = e

    if execution_exception is not None:
        raise execution_exception  # TODO(@jlyle): Generic error handling needs to be done here

    if action_spec["main_method_post"] is None:
        pass
    elif action_spec["main_method_post"] == "output_list":
        for entry in result:
            print(entry)
    elif action_spec["main_method_post"] == "output_result":
        if isinstance(result, bool):
            # return inverse int because false = 0 but 0 is successful exit code
            __exit(int(not result))
        elif isinstance(result, (dict, set, tuple, list)):
            raise ValueError(
                "Cannot print collection values",
            )  # TODO(@jlyle): Generic error handling needs to be done here
        else:
            print(result)
    elif action_spec["main_method_post"] == "write_to_file":
        plist.write()


def main() -> None:
    """Run the plistHelper command line interface."""
    parser = __setup_argparse()

    args = parser.parse_args()

    __handle_arguments(args)

    __exit(0)
