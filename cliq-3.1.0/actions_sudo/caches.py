import argparse

from arg_parse import ArgParse
from cliq_action_base import CliqActionBase
from cliq_properties import CliqProperties
from graphchain_client.graphchain_client import GraphChainClient


class CachesClear(CliqActionBase):
    def __init__(self, ap: ArgParse):
        super().__init__("caches_clear")

        ap.add_cliq_action(self, "clear internal caches")

    def run(
        self, props: CliqProperties, opts: argparse.Namespace, gc: GraphChainClient
    ):
        gc.clear_caches()
