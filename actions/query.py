import argparse
import json

from actions.cliq_action import CliqAction
from cliq_properties import CliqProperties
from util import Util


class Query(CliqAction):
    def __init__(self, aa: argparse.ArgumentParser):
        super().__init__("query")

        p = aa.add_parser(
            self.name,
            help="queries data with command line query or query from file; "
            "plus prints results to stdout or to a file",
        )
        p.add_argument(
            "--query",
            "-q",
            dest="query",
            help="the query to execute; --file or --query is required",
            type=str,
            required=False,
        )
        CliqAction._add_file_arg(p, req=False)
        CliqAction._add_output_arg(p)

    def run(self, opts: argparse.Namespace, props: CliqProperties):
        # SDZ ADMIN
        if opts.file is None and opts.query is None:
            raise ValueError("-q or -f must be specified")

        if opts.file is not None and opts.query is not None:
            raise ValueError("only -q or -f can be specified")

        if opts.query is None:
            # read the query file and store in the query option
            with open(Util.standardize_file(opts.file)) as f:
                query = f.read()
        else:
            # user specified the query on the cmd line
            query = opts.query

        gc = CliqAction._get_sdz_admin(props)
        results = gc.query(query)
        if opts.output is None:
            print(json.dumps(results, indent=2))
        else:
            with open(Util.standardize_file(opts.output), "wt") as f:
                json.dump(results, f, indent=2)
