import argparse
import json

from arg_parse import ArgParse
from cliq_action_base import CliqActionBase
from cliq_properties import CliqProperties
from graphchain_client.graphchain_client import GraphChainClient
from util import Util


class SmartContractCreate(CliqActionBase):
    def __init__(self, ap: ArgParse):
        super().__init__("smart_contract_create")

        ap.add_cliq_action(self, "create a smart contract from file")

        ap.add_system_wallet_id_arg(self)
        ap.add_chain_arg(self)
        ap.add_name_arg(self, "name of the smart contract")
        ap.add_file_arg(self)
        # todo add description and metadata args sometime; this just the basics

    def run(
        self, props: CliqProperties, opts: argparse.Namespace, gc: GraphChainClient
    ):
        # read the required input file
        with open(Util.standardize_file(opts.file), "rt") as f:
            js = f.read()

        Util.pretty_print_json(
            gc.create_smart_contract(opts.chain, opts.name, js, opts.system_wallet_id)
        )


class SmartContractList(CliqActionBase):
    def __init__(self, ap: ArgParse):
        super().__init__("smart_contract_list")

        ap.add_cliq_action(self, "list the smart contracts for the chain")

        ap.add_chain_arg(self)
        ap.add_system_wallet_id_arg(self)

    def run(
        self, props: CliqProperties, opts: argparse.Namespace, gc: GraphChainClient
    ):
        Util.pretty_print_json(
            gc.list_smart_contracts(opts.chain, opts.system_wallet_id)
        )


class SmartContractDelete(CliqActionBase):
    def __init__(self, ap: ArgParse):
        super().__init__("smart_contract_delete")

        ap.add_cliq_action(self, "delete smart contract by id")

        ap.add_system_wallet_id_arg(self)
        ap.add_chain_arg(self)
        ap.add_arg(self, "--id", "-i", "id", "sdo id")

    def run(
        self, props: CliqProperties, opts: argparse.Namespace, gc: GraphChainClient
    ):
        gc.delete_sdo(opts.chain, opts.id, opts.system_wallet_id)


class SmartContractExecute(CliqActionBase):
    def __init__(self, ap: ArgParse):
        super().__init__("smart_contract_execute")

        ap.add_cliq_action(
            self,
            "executes a smart contract",
        )

        ap.add_chain_arg(self)
        ap.add_arg(
            self,
            "--id",
            "-i",
            "sdo_id",
            "the unique SDO ID of the smart contract to execute",
        )
        ap.add_arg(
            self,
            "--func",
            "-f",
            "func",
            "the function name of smart contract to execute",
        )
        ap.add_arg(
            self,
            "--args_file",
            "-a",
            "args_file",
            "the arguments for the function as named attributes in a JSON file; all values must be strings",
            req=False,
        )
        ap.add_system_wallet_id_arg(self)
        ap.add_wait_arg(self)

    def run(
        self, props: CliqProperties, opts: argparse.Namespace, gc: GraphChainClient
    ):
        # read required args file
        args = None
        if opts.args_file:
            with open(Util.standardize_file(opts.args_file), "rt") as f:
                args = json.load(f)

        job_id = gc.execute_smart_contract(
            opts.chain, opts.sdo_id, opts.func, args, opts.system_wallet_id
        )

        if opts.wait:
            Util.wait_status(gc, job_id)
