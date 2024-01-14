#!/usr/bin/env python3

import argparse
import os

from actions.create_smart_contract import CreateSmartContract
from actions.drop_customer import DropCustomer
from actions.drop_sdz import DropSDZ
from actions.execute_smart_contract import ExecuteSmartContract
from actions.export_dbschema import ExportDbSchema
from actions.import_dbschema import ImportDbSchema
from actions.load_data import LoadData
from actions.predict import Predict
from actions.query import Query
from actions.truncate_chain import TruncateChain
from actions.update_customer import UpdateCustomer
from actions.update_dict import UpdateDict
from actions.version import Version
from cliq_properties import CliqProperties
from consts import APP_NAME, DESC, COPYRIGHT
from util import Util

"""
cliq2 - the second coming

command line tool for performing many admin-related functions (both biq- and sdz-admin)
    
NOTE: does not use logging, since this is a cmd line (-ish) tool; so just stdout and minimal so scripts
can process the output cleanly
"""


def main():
    cwd = os.getcwd()

    # create the top-level parser
    parser = argparse.ArgumentParser(prog=APP_NAME, description=DESC, epilog=COPYRIGHT)

    parser.add_argument(
        "-p",
        "--props",
        dest="props_file",
        help="filename of properties file; defaults to ./cliq2.yml",
        default=f"{cwd}/cliq2.yml",
    )

    # create the sub-parser
    subparsers = parser.add_subparsers(
        dest="action",
        help='type "<cmd> --help" for help on specific command',
    )

    # build action list (which also builds the parser out)
    actions = [
        Version(subparsers),
        # BIQ ADMIN
        DropCustomer(subparsers),
        DropSDZ(subparsers),
        UpdateCustomer(subparsers),
        # SDZ ADMIN
        Predict(subparsers),
        UpdateDict(subparsers),
        ImportDbSchema(subparsers),
        ExportDbSchema(subparsers),
        TruncateChain(subparsers),
        LoadData(subparsers),
        Query(subparsers),
        # ANY ONE
        CreateSmartContract(subparsers),
        ExecuteSmartContract(subparsers),
    ]

    # parse args
    opts = parser.parse_args()

    if opts.action is None:
        print("--help or <action> is required\n")
        parser.print_help()
        exit(-1)
    elif opts.action == actions[0].name:
        # properties file is not required for Version action
        props = None
    else:
        # read the properties file
        props = CliqProperties(Util.standardize_file(opts.props_file))

    # find the action in our list, and run it
    for a in actions:
        if a.name == opts.action:
            a.run(opts, props)
            exit(0)

    # action was not found, so error
    raise RuntimeError(f"the action {opts.action} is not supported")


if __name__ == "__main__":
    try:
        main()
    except SystemExit as err:
        # allow system exit of 0 (success) to pass cleanly; log everything else
        if err.code != 0:
            raise SystemExit(err)
    except BaseException as err:
        raise SystemExit(err)
