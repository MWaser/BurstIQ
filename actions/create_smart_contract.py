import argparse

from actions.cliq_action import CliqAction
from cliq_properties import CliqProperties
from util import Util


class CreateSmartContract(CliqAction):
    def __init__(self, aa: argparse.ArgumentParser):
        super().__init__("create_smart")

        p = aa.add_parser(
            self.name,
            help="create a smart contract from file",
        )
        CliqAction._add_chain_arg(p)
        CliqAction._add_name_arg(p, desc="name of the smart contract")
        CliqAction._add_file_arg(p)
        # todo add description and metadata args sometime; this just the basics

    def run(self, opts: argparse.Namespace, props: CliqProperties):
        # read required input file
        with open(Util.standardize_file(opts.file), "rt") as f:
            js = f.read()

        # SDZ ADMIN
        gc = CliqAction._get_sdz_admin(props)
        gc.create_smart_contract(opts.chain, opts.name, js)
