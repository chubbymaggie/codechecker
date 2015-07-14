# -------------------------------------------------------------------------
#                     The CodeChecker Infrastructure
#   This file is distributed under the University of Illinois Open Source
#   License. See LICENSE.TXT for details.
# -------------------------------------------------------------------------

import sys

from codechecker_lib import build_action
from codechecker_lib import logger
from codechecker_lib import option_parser

LOG = logger.get_new_logger('LOG PARSER')


# -----------------------------------------------------------------------------
def parse_compile_commands_json(logfile):
    import json

    actions = []

    logfile.seek(0)
    data = json.load(logfile)

    counter = 0
    for entry in data:
        sourcefile = entry['file']
        lang = option_parser.get_language(sourcefile[sourcefile.rfind('.'):])

        if not lang:
            continue

        action = build_action.BuildAction(counter)

        command = entry['command']
        results = option_parser.parse_options(command)

        action.original_command = command
        action.analyzer_options = results.compile_opts
        action.lang = results.lang
        action.target = results.arch

        if results.action == option_parser.ActionType.COMPILE or \
           results.action == option_parser.ActionType.LINK:
            action.skip = False

        # TODO: check arch
        action.directory = entry['directory']

        action.sources = sourcefile
        action.lang = lang

        actions.append(action)
        del action
        counter += 1

    return actions


# -----------------------------------------------------------------------------
def parse_log(logfilepath):
    LOG.info('Parsing log file: ' + logfilepath)

    actions = []

    with open(logfilepath) as logfile:
        try:
            actions = parse_compile_commands_json(logfile)
        except (ValueError, KeyError) as ex:
            LOG.error('The compile database is not valid.')
            raise ex

    return actions