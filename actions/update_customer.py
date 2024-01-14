import argparse
import json

from actions.cliq_action import CliqAction
from cliq_properties import CliqProperties
from util import Util


class UpdateCustomer(CliqAction):
    def __init__(self, aa: argparse.ArgumentParser):
        super().__init__("update_customer")

        p = aa.add_parser(
            self.name, help="upserts a customer JSON configuration file, BIQ_ADMIN only"
        )
        CliqAction._add_file_arg(p)

    def run(self, opts: argparse.Namespace, props: CliqProperties):
        # read required input file
        with open(Util.standardize_file(opts.file), "rt") as f:
            cust_info = json.load(f)

        # BIG ADMIN
        gc = CliqAction._get_biq_admin(props)
        gc.update_customer(cust_info)
