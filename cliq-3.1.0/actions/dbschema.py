import argparse

from arg_parse import ArgParse
from cliq_action_base import CliqActionBase
from cliq_properties import CliqProperties
from graphchain_client.graphchain_client import GraphChainClient
from util import Util


class ImportDbSchema(CliqActionBase):
    def __init__(self, ap: ArgParse):
        super().__init__("dbschema_import")

        ap.add_cliq_action(self, "upserts a dbschema file as an async job")

        ap.add_file_arg(self)
        ap.add_email_arg(self, "the email to send the results of the import to", False)
        ap.add_flag_arg(
            self,
            "--delete",
            "delete",
            "if delete is true any dictionaries in the SDZ not specified in the DbSchema file will be dropped; default --delete",
            True,
        )
        ap.add_wait_arg(self)

    def run(
        self, props: CliqProperties, opts: argparse.Namespace, gc: GraphChainClient
    ):
        job_id = gc.import_dbschema(opts.file, opts.email, opts.delete)
        if opts.wait:
            Util.wait_status(gc, job_id)


class ExportDbSchema(CliqActionBase):
    def __init__(self, ap: ArgParse):
        super().__init__("dbschema_export")

        ap.add_cliq_action(self, "exports a dbschema file")

        ap.add_output_arg(self)

    def run(
        self, props: CliqProperties, opts: argparse.Namespace, gc: GraphChainClient
    ):
        dbschema = gc.export_dbschema()

        if opts.output is None:
            print(dbschema)
        else:
            cust, sdz = props.get_customer_sdz()

            fn = f"{Util.standardize_file(opts.output)}/{cust}_{sdz}.dbs"
            print(f"saving dbschema file: {fn}")
            with open(fn, "wt") as f:
                f.write(dbschema)
