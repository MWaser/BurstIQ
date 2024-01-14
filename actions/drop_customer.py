import argparse

from actions.cliq_action import CliqAction
from cliq_properties import CliqProperties


class DropCustomer(CliqAction):
    def __init__(self, aa: argparse.ArgumentParser):
        super().__init__("drop_customer")

        p = aa.add_parser(
            self.name, help="drop a customer by short name, BIQ_ADMIN only"
        )
        CliqAction._add_name_arg(p)

    def run(self, opts: argparse.Namespace, props: CliqProperties):
        # BIG ADMIN
        gc = CliqAction._get_biq_admin(props)
        gc.drop_customer(opts.name)
