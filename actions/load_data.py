import argparse

from actions.cliq_action import CliqAction
from cliq_properties import CliqProperties


class LoadData(CliqAction):
    def __init__(self, aa: argparse.ArgumentParser):
        super().__init__("load")

        p = aa.add_parser(self.name, help="loads data file as an async job")
        CliqAction._add_chain_arg(p)
        CliqAction._add_file_arg(p)
        p.add_argument(
            "--map",
            "-m",
            dest="map_file",
            help="the map file path for the mapping data file to dictionary",
            type=str,
            required=False,
        )
        p.add_argument(
            "--transform",
            "-t",
            dest="xform_file",
            help="the transform file path for JS transform function to modify data to dictionary",
            type=str,
            required=False,
        )
        CliqAction._add_email_arg(p)
        CliqAction._add_wait_arg(p)

    def run(self, opts: argparse.Namespace, props: CliqProperties):
        # SDZ ADMIN
        gc = CliqAction._get_sdz_admin(props)
        job_id = gc.load_data(
            opts.chain, opts.file, opts.map_file, opts.xform_file, opts.email
        )
        if opts.wait:
            CliqAction._wait(gc, job_id)
