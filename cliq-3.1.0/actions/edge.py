import argparse
import json

from arg_parse import ArgParse
from cliq_action_base import CliqActionBase
from cliq_properties import CliqProperties
from graphchain_client.graphchain_client import GraphChainClient
from util import Util


class EdgeGet(CliqActionBase):
    def __init__(self, ap: ArgParse):
        super().__init__("edge_get")

        ap.add_cliq_action(self, "get edge by chain and edge id")

        ap.add_system_wallet_id_arg(self)
        ap.add_chain_arg(self)
        ap.add_id_arg(self, "edge id", True)

    def run(
        self, props: CliqProperties, opts: argparse.Namespace, gc: GraphChainClient
    ):
        Util.pretty_print_json(gc.get_edge(opts.chain, opts.id, opts.system_wallet_id))


class EdgeCreate(CliqActionBase):
    def __init__(self, ap: ArgParse):
        super().__init__("edge_create")

        ap.add_cliq_action(self, "create a manual edge")

        ap.add_system_wallet_id_arg(self)
        ap.add_arg(
            self,
            "--fromChain",
            "-fc",
            "from_chain",
            "from chain",
        )
        ap.add_arg(
            self,
            "--fromSdoId",
            None,
            "from_sdo_id",
            "SDO ID in the from chain",
        )
        ap.add_arg(self, "--toChain", "-t", "to_chain", "to chain")
        ap.add_arg(
            self,
            "--toSdoId",
            None,
            "to_sdo_id",
            "SDO ID in the to chain",
        )
        ap.add_arg(
            self,
            "--label",
            "-l",
            "label",
            "edge label",
        )
        ap.add_arg(
            self,
            "--properties",
            "-p",
            "properties",
            "edge properties (JSON)",
            req=False,
        )

    def run(
        self, props: CliqProperties, opts: argparse.Namespace, gc: GraphChainClient
    ):
        properties_json = None
        if opts.properties:
            properties_json = json.loads(opts.properties)

        Util.pretty_print_json(
            gc.create_manual_edge(
                opts.from_chain,
                opts.from_sdo_id,
                opts.to_chain,
                opts.to_sdo_id,
                opts.label,
                properties_json,
                opts.system_wallet_id,
            )
        )


class EdgeUpdate(CliqActionBase):
    def __init__(self, ap: ArgParse):
        super().__init__("edge_update")

        ap.add_cliq_action(self, "update edge by chain and edge id")

        ap.add_system_wallet_id_arg(self)
        ap.add_chain_arg(self, desc='the FROM chain name for the edge')
        ap.add_id_arg(self, "edge id", True)
        ap.add_arg(
            self,
            "--properties",
            "-p",
            "properties",
            "edge properties (JSON)",
        )

    def run(
        self, props: CliqProperties, opts: argparse.Namespace, gc: GraphChainClient
    ):
        properties_json = None
        if opts.properties:
            properties_json = json.loads(opts.properties)

        Util.pretty_print_json(
            gc.update_edge(opts.chain, opts.id, properties_json, opts.system_wallet_id)
        )


class EdgeDelete(CliqActionBase):
    def __init__(self, ap: ArgParse):
        super().__init__("edge_delete")

        ap.add_cliq_action(self, "delete edge by chain and edge id")

        ap.add_system_wallet_id_arg(self)
        ap.add_chain_arg(self)
        ap.add_list_arg(
            self,
            "--ids",
            "-i",
            "ids",
            "One or many edge ids to delete for a given chain",
        )

    def run(
        self, props: CliqProperties, opts: argparse.Namespace, gc: GraphChainClient
    ):
        id_count = len(opts.ids)
        count = 1
        for i in opts.ids:
            print(f"{count:03}/{id_count:03} - Deleting edge {i} from {opts.chain}")
            gc.delete_edge(opts.chain, i, opts.system_wallet_id)
            count = count + 1
