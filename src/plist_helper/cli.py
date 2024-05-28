"""
Command line interface for PlistHelper to more universal access to plist management.
"""

import argparse
# import os
# import sys
import textwrap

from helper import PlistHelper

global_arguments = (
    (
        {'-p', '--plist'},
        {
            'dest':     'plist',
            'help':     "The plist to act upon",
            'type':     str,
            'required': True,
        },
    ),
)

# createFile
# convertFile
# exists
# getType
# getDictKeys
# getArrayLength
# insert
# insertArrayAppend
# update
# upsert
# delete
# merge

actions = (
    {
        'name':                 'print',
        'main_method':          PlistHelper.print,
        'action_help':          None,
        'argument_definitions':  (
            (
                {'-f', '--format'},
                {
                    'dest':     'output_format',
                    'help':     'The format in which to print the plist',
                    'choices':  [fmt['name'] for fmt in PlistHelper.FILE_FORMATS],
                    'default':  'xml'
                },
            ),
            (
                {'-s', '--sort'},
                {
                    'dest':     'output_sort',
                    'help':     'Sort keys in alphabetical order',
                    'action':   'store_true',
                },
            ),
            (
                {'-e', '--entry'},
                {
                    'dest':     'path',
                    'help':     '''The path to the object to print. \
                        Can be provided 0-n times to specify root or any child''',
                    'action':   'append',
                    'default':  [],
                },
            ),
        ),
    },
    # {
    #     'name':                 'printDictKeys',
    #     'main_method':          PlistHelper.get_dict_keys,
    #     'action_help':          None,
    #     'argument_definitions':  (
    #         (
    #             {'-t', '--todo'},
    #             {},
    #         ),
    #     ),
    # },
    # {
    #     'name':                 'PrintArrayLength',
    #     'main_method':          PlistHelper.get_array_length,
    #     'action_help':          None,
    #     'argument_definitions':  {
    #         (
    #             {'-t', '--todo'},
    #             {},
    #         ),
    #     },
    # },
    # TODO
)

def execute_plist_helper_cli():
    """
    Main function for running the plistHelper command line interface.
    """

    parent_parser = argparse.ArgumentParser(
        prog='plistHelper',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=textwrap.dedent(PlistHelper.__doc__)
    )

    child_parser = parent_parser.add_subparsers(
        dest='action_name',
        title='Actions'
    )

    for action in actions:
        action_help = action['action_help']
        if action_help is None:
            # Use the first line of the docstring as the default CLI action help
            action_help = textwrap.dedent(action['main_method'].__doc__).split('\n', 1)[0]

        add_parser = child_parser.add_parser(action['name'], help=action_help)

        for global_argument in global_arguments:
            add_parser.add_argument(*global_argument[0], **global_argument[1])

        for argument_definition in action['argument_definitions']:
            add_parser.add_argument(*argument_definition[0], **argument_definition[1])

    args = parent_parser.parse_args()
    action_name = args.action_name

    try:
        plist = PlistHelper(args.plist)
    except Exception:
        parent_parser.exit(status=101, message="Unable to open plist file\n")

    print('JML: "' + str(args) + '"')

    if action_name == 'print':
        plist.print(
            output_format=args.output_format,
            output_sort=args.output_sort,
            path=args.path,
        )
