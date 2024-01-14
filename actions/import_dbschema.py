import argparse

from actions.cliq_action import CliqAction
from cliq_properties import CliqProperties


class ImportDbSchema(CliqAction):
    def __init__(self, aa: argparse.ArgumentParser):
        super().__init__("import_dbschema")

        p = aa.add_parser(self.name, help="upserts a dbschema file as an async job")
        CliqAction._add_file_arg(p)
        CliqAction._add_email_arg(p)
        p.add_argument(
            "--delete",
            dest="delete",
            help="if delete is true any dictionaries in the SDZ not specified in the "
            "DbSchema file will be dropped; default --delete",
            action=argparse.BooleanOptionalAction,
            type=bool,
            default=True,
        )
        CliqAction._add_wait_arg(p)

    def run(self, opts: argparse.Namespace, props: CliqProperties):
        # SDZ ADMIN
        gc = CliqAction._get_sdz_admin(props)
        job_id = gc.import_dbschema(opts.file, opts.email, opts.delete)
        if opts.wait:
            CliqAction._wait(gc, job_id)
