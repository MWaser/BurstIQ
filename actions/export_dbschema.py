import argparse

from actions.cliq_action import CliqAction
from cliq_properties import CliqProperties
from util import Util


class ExportDbSchema(CliqAction):
    def __init__(self, aa: argparse.ArgumentParser):
        super().__init__("export_dbschema")

        p = aa.add_parser(self.name, help="exports a dbschema file")
        CliqAction._add_output_arg(p)

    def run(self, opts: argparse.Namespace, props: CliqProperties):
        # SDZ ADMIN
        gc = CliqAction._get_sdz_admin(props)
        dbschema = gc.export_dbschema()

        if opts.output is None:
            print(dbschema)
        else:
            cust, sdz = props.get_graphchain_customer()

            fn = f"{Util.standardize_file(opts.output)}/{cust}_{sdz}.dbs"
            print(f"saving dbschema file: {fn}")
            with open(fn, "wt") as f:
                f.write(dbschema)
