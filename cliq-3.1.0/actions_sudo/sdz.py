import argparse

from arg_parse import ArgParse
from cliq_action_base import CliqActionBase
from cliq_properties import CliqProperties
from graphchain_client.graphchain_client import GraphChainClient


class SDZDrop(CliqActionBase):
    def __init__(self, ap: ArgParse):
        super().__init__("sdz_drop")

        ap.add_cliq_action(self, "drop a customer's sdz by short name")
        ap.add_name_arg(self)
        ap.add_sdz_arg(self)

    def run(
        self, props: CliqProperties, opts: argparse.Namespace, gc: GraphChainClient
    ):
        gc.drop_sdz(opts.name, opts.sdz)
