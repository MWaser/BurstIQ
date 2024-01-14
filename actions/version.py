import argparse

from actions.cliq_action import CliqAction
from cliq_properties import CliqProperties
from consts import VERSION, COPYRIGHT


class Version(CliqAction):
    def __init__(self, aa: argparse.ArgumentParser):
        super().__init__("version")

        aa.add_parser(self.name, help="version number")

    def run(self, opts: argparse.Namespace, props: CliqProperties):
        print(f"\nv{VERSION}\n{COPYRIGHT}")
