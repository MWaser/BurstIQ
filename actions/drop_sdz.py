import argparse

from actions.cliq_action import CliqAction
from cliq_properties import CliqProperties


class DropSDZ(CliqAction):
    def __init__(self, aa: argparse.ArgumentParser):
        super().__init__("drop_sdz")

        p = aa.add_parser(
            self.name, help="drop a customer's sdz by short name, BIQ_ADMIN only"
        )
        CliqAction._add_name_arg(p)
        CliqAction._add_sdz_arg(p)

    def run(self, opts: argparse.Namespace, props: CliqProperties):
        # BIG ADMIN
        gc = CliqAction._get_biq_admin(props)
        gc.drop_sdz(opts.name, opts.sdz)
