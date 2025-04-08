import argparse
import json

from arg_parse import ArgParse
from cliq_action_base import CliqActionBase
from cliq_properties import CliqProperties
from graphchain_client.graphchain_client import GraphChainClient
from util import Util


class CustomerCreate(CliqActionBase):
    def __init__(self, ap: ArgParse):
        super().__init__("customer_create")

        ap.add_cliq_action(
            self,
            "create a customer JSON configuration file",
        )

        ap.add_file_arg(self)

    def run(
        self, props: CliqProperties, opts: argparse.Namespace, gc: GraphChainClient
    ):
        # read a required input file
        with open(Util.standardize_file(opts.file), "rt") as f:
            cust_info = json.load(f)

        gc.create_customer(cust_info)


class CustomerList(CliqActionBase):
    def __init__(self, ap: ArgParse):
        super().__init__("customer_list")

        ap.add_cliq_action(self, "list the customer")

    def run(
        self, props: CliqProperties, opts: argparse.Namespace, gc: GraphChainClient
    ):
        for c in gc.list_customers():
            print(f"{c}")


class CustomerGet(CliqActionBase):
    def __init__(self, ap: ArgParse):
        super().__init__("customer_get")

        ap.add_cliq_action(self, "get a customer by short name")

        ap.add_name_arg(self)

    def run(
        self, props: CliqProperties, opts: argparse.Namespace, gc: GraphChainClient
    ):
        cust = gc.get_customer(opts.name)
        Util.pretty_print_json(cust)


class CustomerUpdate(CliqActionBase):
    def __init__(self, ap: ArgParse):
        super().__init__("customer_update")

        ap.add_cliq_action(
            self,
            "upserts a customer JSON configuration file",
        )
        ap.add_name_arg(self)
        ap.add_file_arg(self)

    def run(
        self, props: CliqProperties, opts: argparse.Namespace, gc: GraphChainClient
    ):
        # read a required input file
        with open(Util.standardize_file(opts.file), "rt") as f:
            cust_info = json.load(f)

        cust_info["shortName"] = opts.name

        gc.update_customer(opts.name, cust_info)


class CustomerDrop(CliqActionBase):
    def __init__(self, ap: ArgParse):
        super().__init__("customer_drop")

        ap.add_cliq_action(self, "drop a customer by short name")

        ap.add_name_arg(self)

    def run(
        self, props: CliqProperties, opts: argparse.Namespace, gc: GraphChainClient
    ):
        gc.drop_customer(opts.name)
