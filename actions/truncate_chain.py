import argparse

from actions.cliq_action import CliqAction
from cliq_properties import CliqProperties


class TruncateChain(CliqAction):
    def __init__(self, aa: argparse.ArgumentParser):
        super().__init__("truncate_chain")

        p = aa.add_parser(self.name, help="truncates a chain by name")
        CliqAction._add_chain_arg(p)

    def run(self, opts: argparse.Namespace, props: CliqProperties):
        # SDZ ADMIN
        gc = CliqAction._get_sdz_admin(props)
        gc.truncate_chain(opts.chain)
