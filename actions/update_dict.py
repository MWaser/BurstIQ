import argparse
import json

from actions.cliq_action import CliqAction
from cliq_properties import CliqProperties
from util import Util


class UpdateDict(CliqAction):
    def __init__(self, aa: argparse.ArgumentParser):
        super().__init__("update_dict")

        p = aa.add_parser(
            self.name, help="upserts a dictionary JSON configuration file"
        )
        CliqAction._add_file_arg(p)

    def run(self, opts: argparse.Namespace, props: CliqProperties):
        # read required input file
        with open(Util.standardize_file(opts.file), "rt") as f:
            dictionary = json.load(f)

            # SDZ ADMIN
            gc = CliqAction._get_sdz_admin(props)
            gc.update_dict(dictionary)
