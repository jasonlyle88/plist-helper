"""Command line interface for PlistHelper to provide more universal access to plist management."""

from __future__ import annotations

import argparse as _argparse
import contextlib as _contextlib
import datetime as _datetime
import sys as _sys
import textwrap as _textwrap
import typing as _typing
from types import MappingProxyType as _MappingProxyType

from plist_helper._exceptions import (
    PlistHelperError,
    PlistHelperRuntimeError,
    PlistHelperTypeError,
    PlistHelperValueError,
)
from plist_helper._plist import PlistHelper as _PlistHelper

__TRUTHY_VALUES = (
    "t",
    "true",
    "y",
    "yes",
    "1",
)

__ALL_ARGUMENTS = _MappingProxyType(
    {
        "data_type": _MappingProxyType(
            {
                "args": {"-t", "--data-type"},
                "kwargs": _MappingProxyType(
                    {
                        "dest": "value_data_type",
                        "help": "The data type of the provided value",
                        "choices": _PlistHelper.ENTRY_DATA_TYPES.keys(),
                        "default": "dict",
                        "required": True,
                    },
                ),
            },
        ),
        "entry": _MappingProxyType(
            {
                "args": {"-e", "--entry"},
                "kwargs": _MappingProxyType(
                    {
                        "dest": "path",
                        "help": """
                                The path to the target plist entry
                                Can be provided 0-n times to specify the root or any child
                                """,
                        "action": "append",
                        "default": [],
                    },
                ),
            },
        ),
        "format": _MappingProxyType(
            {
                "args": {"-f", "--format"},
                "kwargs": _MappingProxyType(
                    {
                        "dest": "output_format",
                        "help": "The format in which to print the plist",
                        "choices": _PlistHelper.FILE_FORMATS.keys(),
                        "default": "xml",
                    },
                ),
            },
        ),
        "overwrite": _MappingProxyType(
            {
                "args": {"-o", "--overwrite"},
                "kwargs": _MappingProxyType(
                    {
                        "dest": "overwrite",
                        "help": "Overwrite existing entries in target plist with entries from the source plist",
                        "action": "store_true",
                    },
                ),
            },
        ),
        "plist_source": _MappingProxyType(
            {
                "args": {"-P", "--plist-source"},
                "kwargs": _MappingProxyType(
                    {
                        "dest": "plist_source",
                        "help": "The source plist to pull data from to merge",
                        "type": str,
                        "required": True,
                    },
                ),
            },
        ),
        "plist_target": _MappingProxyType(
            {
                "args": {"-p", "--plist"},
                "kwargs": _MappingProxyType(
                    {
                        "dest": "plist_target",
                        "help": "The target plist to act upon",
                        "type": str,
                        "required": True,
                    },
                ),
            },
        ),
        "root_data_type": _MappingProxyType(
            {
                "args": {"-t", "--data-type"},
                "kwargs": _MappingProxyType(
                    {
                        "dest": "data_type",
                        "help": "The data type of the root of the plist file",
                        "choices": _PlistHelper.ENTRY_DATA_TYPES.keys(),
                        "default": "dict",
                    },
                ),
            },
        ),
        "sort": _MappingProxyType(
            {
                "args": {"-s", "--sort"},
                "kwargs": _MappingProxyType(
                    {
                        "dest": "output_sort",
                        "help": "Sort keys in alphabetical order",
                        "action": "store_true",
                    },
                ),
            },
        ),
        "source_path": _MappingProxyType(
            {
                "args": {"-E", "--entry-source"},
                "kwargs": _MappingProxyType(
                    {
                        "dest": "source_path",
                        "help": """
                                The path to the source plist entry
                                Can be provided 0-n times to specify the root or any child
                                """,
                        "action": "append",
                        "default": [],
                    },
                ),
            },
        ),
        "target_path": _MappingProxyType(
            {
                "args": {"-e", "--entry-target"},
                "kwargs": _MappingProxyType(
                    {
                        "dest": "target_path",
                        "help": """
                                The path to the target plist entry
                                Can be provided 0-n times to specify the root or any child
                                """,
                        "action": "append",
                        "default": [],
                    },
                ),
            },
        ),
        "value": _MappingProxyType(
            {
                "args": {"-v", "--value"},
                "kwargs": _MappingProxyType(
                    {
                        "dest": "value",
                        "help": "Data value to use for the action",
                    },
                ),
            },
        ),
    },
)

__GLOBAL_ARGUMENTS = (__ALL_ARGUMENTS["plist_target"],)

# DONE: convertFile
# DONE: createFile
# DONE: delete
# DONE: exists
# DONE: getArrayLength
# DONE: getDictKeys
# DONE: getType
# DONE: getValue
# DONE: insert
# DONE: insertArrayAppend
# DONE: merge
# DONE: print
# DONE: update
# DONE: upsert

__ACTIONS = {
    "convertFile": _MappingProxyType(
        {
            "main_method": _PlistHelper.convert_file,
            "main_method_post": None,
            "action_help": None,
            "argument_definitions": (__ALL_ARGUMENTS["format"],),
        },
    ),
    "createFile": _MappingProxyType(
        {
            "main_method": _PlistHelper.create_empty_file,
            "main_method_post": None,
            "action_help": None,
            "argument_definitions": (
                __ALL_ARGUMENTS["format"],
                __ALL_ARGUMENTS["root_data_type"],
            ),
        },
    ),
    "delete": _MappingProxyType(
        {
            "main_method": _PlistHelper.delete,
            "main_method_post": "write_to_file",
            "action_help": None,
            "argument_definitions": (__ALL_ARGUMENTS["entry"],),
        },
    ),
    "exists": _MappingProxyType(
        {
            "main_method": _PlistHelper.exists,
            "main_method_post": "output_simple_result",
            "action_help": None,
            "argument_definitions": (__ALL_ARGUMENTS["entry"],),
        },
    ),
    "getArrayLength": _MappingProxyType(
        {
            "main_method": _PlistHelper.get_array_length,
            "main_method_post": "output_simple_result",
            "action_help": None,
            "argument_definitions": (__ALL_ARGUMENTS["entry"],),
        },
    ),
    "getDictKeys": _MappingProxyType(
        {
            "main_method": _PlistHelper.get_dict_keys,
            "main_method_post": "output_list",
            "action_help": None,
            "argument_definitions": (__ALL_ARGUMENTS["entry"],),
        },
    ),
    "getType": _MappingProxyType(
        {
            "main_method": _PlistHelper.get_type,
            "main_method_post": "output_simple_result",
            "action_help": None,
            "argument_definitions": (__ALL_ARGUMENTS["entry"],),
        },
    ),
    "getValue": _MappingProxyType(
        {
            "main_method": _PlistHelper.get,
            "main_method_post": "output_simple_result",
            "action_help": None,
            "argument_definitions": (__ALL_ARGUMENTS["entry"],),
        },
    ),
    "insert": _MappingProxyType(
        {
            "main_method": _PlistHelper.insert,
            "main_method_post": "write_to_file",
            "action_help": None,
            "argument_definitions": (
                __ALL_ARGUMENTS["entry"],
                __ALL_ARGUMENTS["data_type"],
                __ALL_ARGUMENTS["value"],
            ),
        },
    ),
    "insertArrayAppend": _MappingProxyType(
        {
            "main_method": _PlistHelper.insert_array_append,
            "main_method_post": "write_to_file",
            "action_help": None,
            "argument_definitions": (
                __ALL_ARGUMENTS["entry"],
                __ALL_ARGUMENTS["data_type"],
                __ALL_ARGUMENTS["value"],
            ),
        },
    ),
    "merge": _MappingProxyType(
        {
            "main_method": _PlistHelper.merge,
            "main_method_post": "write_to_file",
            "action_help": None,
            "argument_definitions": (
                __ALL_ARGUMENTS["target_path"],
                __ALL_ARGUMENTS["plist_source"],
                __ALL_ARGUMENTS["source_path"],
                __ALL_ARGUMENTS["overwrite"],
            ),
        },
    ),
    "print": _MappingProxyType(
        {
            "main_method": _PlistHelper.print,
            "main_method_post": None,
            "action_help": None,
            "argument_definitions": (
                __ALL_ARGUMENTS["format"],
                __ALL_ARGUMENTS["sort"],
                __ALL_ARGUMENTS["entry"],
            ),
        },
    ),
    "update": _MappingProxyType(
        {
            "main_method": _PlistHelper.update,
            "main_method_post": "write_to_file",
            "action_help": None,
            "argument_definitions": (
                __ALL_ARGUMENTS["entry"],
                __ALL_ARGUMENTS["data_type"],
                __ALL_ARGUMENTS["value"],
            ),
        },
    ),
    "upsert": _MappingProxyType(
        {
            "main_method": _PlistHelper.upsert,
            "main_method_post": "write_to_file",
            "action_help": None,
            "argument_definitions": (
                __ALL_ARGUMENTS["entry"],
                __ALL_ARGUMENTS["data_type"],
                __ALL_ARGUMENTS["value"],
            ),
        },
    ),
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


def __get_class_from_method_handle(handle: object) -> object:
    # Extract the qualified name of the method
    qualname = handle.__qualname__

    # Split the qualified name to get the class name
    class_name = qualname.split(".<locals>", 1)[0].rsplit(".", 1)[0]

    # Get the module in which the class is defined
    module = _sys.modules[handle.__module__]

    # Retrieve the class object from the module
    return getattr(module, class_name)


def __get_original_descriptor_from_handle(handle: object) -> object | None:
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


def __handle_arguments(args: _argparse.Namespace) -> dict:
    """Handle the arguments from argparse for the plist_helper CLI."""
    # Setup a dictionary that can be used to call the main function with
    # unpacked args and kwargs
    main_method_args = []
    main_method_kwargs = vars(args).copy()

    # Placeholder for the parsed plist
    plist_target = None

    # Action name is just for the CLI handler, not the main_method, so remove it
    del main_method_kwargs["action_name"]

    # Remove any global arguments from kwargs
    for global_argument in __GLOBAL_ARGUMENTS:
        del main_method_kwargs[global_argument["kwargs"]["dest"]]

    # Get the action definition based on the action name
    action_spec = __ACTIONS[args.action_name]

    # Get the type of the main method (static method, class method, or function)
    # Based on the type of the main method, setup args and kwargs appropriately
    typed_handle = __get_original_descriptor_from_handle(action_spec["main_method"])
    if isinstance(typed_handle, __TYPES.classmethod):
        main_method_kwargs["plist_file"] = args.plist_target
    elif isinstance(typed_handle, __TYPES.function):
        try:
            plist_target = _PlistHelper(_PlistHelper.PLIST_INFO_TYPE_FILE, args.plist_target)
        except Exception:
            __exit(status=101, message="ERROR: Unable to open target plist file\n")

        main_method_args = [
            plist_target,
        ]
    else:
        __exit(
            status=123,
            message='ERROR: Action main method not recognized type: "'
            + type(typed_handle).__name__
            + '"\n',
        )

    if "value_data_type" in main_method_kwargs:
        # Verify parameter combinations
        value_specified = \
            "value" in main_method_kwargs \
            and main_method_kwargs["value"] is not None

        if (
            main_method_kwargs["value_data_type"] in ["array", "dict"]
            and value_specified
        ):
            raise PlistHelperRuntimeError(
                "Cannot provide a value when data type is array or dict",
            )

        if (
            main_method_kwargs["value_data_type"] not in ["array", "dict"]
            and not value_specified
        ):
            raise PlistHelperRuntimeError(
                "A value must be provided when the data type is a simple data type",
            )

    if "value" in main_method_kwargs and main_method_kwargs["value"] is None:
        del main_method_kwargs["value"]

    if "plist_source" in main_method_kwargs:
        try:
            source_plist_helper = _PlistHelper(_PlistHelper.PLIST_INFO_TYPE_FILE, main_method_kwargs["plist_source"])
        except Exception:
            __exit(status=101, message="ERROR: Unable to open source plist file\n")

        del main_method_kwargs["plist_source"]
        main_method_kwargs["source_plist_helper"] = source_plist_helper

    return {
        "action_spec": action_spec,
        "main_method_args": main_method_args,
        "main_method_kwargs": main_method_kwargs,
        "plist_target": plist_target,
    }


def __convert_provided_value_to_data_type(  # noqa: C901,PLR0912
    argument_results: dict,
) -> None:
    main_method_kwargs = argument_results["main_method_kwargs"]

    # Check if there is anything to convert.
    # If there is nothing to convert, then just exit
    if "value_data_type" not in argument_results["main_method_kwargs"]:
        return

    # Value data type is just for the CLI to know how to convert.
    # Since this is where the conversion is done, store it locally and remove
    # from the kwargs
    value_data_type = main_method_kwargs["value_data_type"]
    del main_method_kwargs["value_data_type"]

    # Check value against provided data type
    if value_data_type in ("array", "dict") and "value" in main_method_kwargs:
        raise PlistHelperRuntimeError("Value cannot be provided for collection types")

    if value_data_type not in ("array", "dict"):
        if "value" not in main_method_kwargs:
            raise PlistHelperRuntimeError("Value must be provided for simple types")

        if not isinstance(main_method_kwargs["value"], str):
            raise PlistHelperTypeError("Expected to convert str")

    # Attempt to convert the provided value to the appropriate python type
    # based on the provided data type
    if value_data_type == "array":
        main_method_kwargs["value"] = []

    elif value_data_type == "bool":
        main_method_kwargs["value"] = (
            main_method_kwargs["value"].strip().lower() in __TRUTHY_VALUES
        )

    elif value_data_type == "data":
        main_method_kwargs["value"] = main_method_kwargs["value"].encode()

    elif value_data_type == "date":
        try:
            main_method_kwargs["value"] = _datetime.datetime.fromisoformat(
                main_method_kwargs["value"],
            )
        except ValueError as e:
            raise PlistHelperValueError(*(e.args)) from e

    elif value_data_type == "dict":
        main_method_kwargs["value"] = {}

    elif value_data_type == "integer":
        try:
            main_method_kwargs["value"] = int(main_method_kwargs["value"])
        except ValueError as e:
            raise PlistHelperValueError(*(e.args)) from e

    elif value_data_type == "real":
        try:
            main_method_kwargs["value"] = float(main_method_kwargs["value"])
        except ValueError as e:
            raise PlistHelperValueError(*(e.args)) from e

    elif value_data_type == "string":
        pass # Value data type is already a string, nothing to do

    else:
        raise PlistHelperValueError(
            f"Unexpected data type '{value_data_type}'",
        )


def __execute_main_method(argument_results: dict) -> None:
    action_spec = argument_results["action_spec"]
    main_method_args = argument_results["main_method_args"]
    main_method_kwargs = argument_results["main_method_kwargs"]
    plist_target = argument_results["plist_target"]

    result = None
    execution_exception = None
    try:
        result = action_spec["main_method"](*main_method_args, **main_method_kwargs)
    except Exception as e:
        execution_exception = e

    if execution_exception is not None:
        raise execution_exception

    if action_spec["main_method_post"] is None:
        pass
    elif action_spec["main_method_post"] == "output_list":
        for entry in result:
            _sys.stdout.write(str(entry) + "\n")
    elif action_spec["main_method_post"] == "output_simple_result":
        if isinstance(result, bool):
            # return inverse int value because false = 0 but in the shell,
            # 0 is successful exit code
            __exit(int(not result))
        elif isinstance(result, (dict, set, tuple, list)):
            raise PlistHelperValueError(
                "Cannot print collection values",
            )
        else:
            _sys.stdout.write(str(result) + "\n")
    elif action_spec["main_method_post"] == "write_to_file":
        plist_target.write()


def main() -> None:
    """Run the plistHelper command line interface."""
    try:
        parser = __setup_argparse()

        args = parser.parse_args()

        argument_results = __handle_arguments(args)

        __convert_provided_value_to_data_type(argument_results)

        __execute_main_method(argument_results)

        __exit(0)
    except PlistHelperError as e:
        _sys.stderr.write("ERROR: " + str(e) + "\n")
        __exit(1)
