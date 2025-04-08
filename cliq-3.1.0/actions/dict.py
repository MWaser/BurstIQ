import argparse
import json

from arg_parse import ArgParse
from cliq_action_base import CliqActionBase
from cliq_properties import CliqProperties
from graphchain_client.graphchain_client import GraphChainClient
from util import Util


class DictList(CliqActionBase):
    def __init__(self, ap: ArgParse):
        super().__init__("dict_list")

        ap.add_cliq_action(self, "list the dictionaries in the system")

    def run(
        self, props: CliqProperties, opts: argparse.Namespace, gc: GraphChainClient
    ):
        for d in gc.list_dicts():
            print(f"{d}")


class DictGet(CliqActionBase):
    def __init__(self, ap: ArgParse):
        super().__init__("dict_get")

        ap.add_cliq_action(self, "get a dictionary by chain name")

        ap.add_chain_arg(self)

    def run(
        self, props: CliqProperties, opts: argparse.Namespace, gc: GraphChainClient
    ):
        Util.pretty_print_json(gc.get_dict(opts.chain))


class DictUpsert(CliqActionBase):
    def __init__(self, ap: ArgParse):
        super().__init__("dict_upsert")

        ap.add_cliq_action(self, "upserts a dictionary JSON configuration file")

        ap.add_file_arg(self)
        ap.add_email_arg(self, "the email to send the results of the import to", False)
        ap.add_wait_arg(self)

    def run(
        self, props: CliqProperties, opts: argparse.Namespace, gc: GraphChainClient
    ):
        # read the required input file
        with open(Util.standardize_file(opts.file), "rt") as f:
            dictionary = json.load(f)

        job_id = gc.update_dict(dictionary, opts.email)
        if opts.wait:
            Util.wait_status(gc, job_id)


class DictDelete(CliqActionBase):
    def __init__(self, ap: ArgParse):
        super().__init__("dict_delete")

        ap.add_cliq_action(self, "deletes a dictionary by chain")

        ap.add_chain_arg(self)

    def run(
        self, props: CliqProperties, opts: argparse.Namespace, gc: GraphChainClient
    ):
        # read required input file
        gc.delete_dict(opts.chain)


class DictPredict(CliqActionBase):
    def __init__(self, ap: ArgParse):
        super().__init__("dict_predict")

        ap.add_cliq_action(
            self, "uses a data file to predict the dictionary and mapping"
        )

        ap.add_sheet_arg(self)
        ap.add_file_arg(self)
        ap.add_output_arg(self)

    def run(
        self, props: CliqProperties, opts: argparse.Namespace, gc: GraphChainClient
    ):
        dictionary, mapping = gc.predict(opts.file, opts.sheet)

        if opts.output is None:
            print("dictionary:\n")
            Util.pretty_print_json(dictionary)

            print(f"\nmapping:\n")
            Util.pretty_print_json(mapping)
        else:
            print(f"saving dictionary and mapping files: {opts.output}/{opts.name}*")

            with open(f"{opts.output}/{opts.name}_dict.json", "wt") as f:
                json.dump(dictionary, f, indent=2)

            with open(f"{opts.output}/{opts.name}_mapping.json", "wt") as f:
                json.dump(mapping, f, indent=2)
