import argparse
import json

from actions.cliq_action import CliqAction
from cliq_properties import CliqProperties
from util import Util


class ExecuteSmartContract(CliqAction):
    def __init__(self, aa: argparse.ArgumentParser):
        super().__init__("execute_smart")

        p = aa.add_parser(
            self.name,
            help="executes a smart contract",
        )
        CliqAction._add_chain_arg(p)
        p.add_argument(
            "--id",
            "-i",
            dest="sdo_id",
            help="the unique SDO ID of the smart contract to execute",
            type=str,
            required=True,
        )
        p.add_argument(
            "--func",
            "-f",
            dest="func",
            help="the function name of smart contract to execute",
            type=str,
            required=True,
        )
        p.add_argument(
            "--args_file",
            "-a",
            dest="args_file",
            help="the arguments for the function as named attributes in a JSON file; all values must be strings",
            type=str,
            required=False,
        )
        CliqAction._add_wait_arg(p)

    def run(self, opts: argparse.Namespace, props: CliqProperties):
        # read required args file
        with open(Util.standardize_file(opts.args_file), "rt") as f:
            args = json.load(f)

        # SDZ ADMIN
        gc = CliqAction._get_sdz_admin(props)
        job_id = gc.execute_smart_contract(opts.chain, opts.sdo_id, opts.func, args)

        if opts.wait:
            CliqAction._wait(gc, job_id)
