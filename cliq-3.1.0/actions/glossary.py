import argparse

from arg_parse import ArgParse
from cliq_action_base import CliqActionBase
from cliq_properties import CliqProperties
from graphchain_client.graphchain_client import GraphChainClient
from util import Util


class GlossaryCreate(CliqActionBase):
    def __init__(self, ap: ArgParse):
        super().__init__("glossary_create")

        ap.add_cliq_action(self, "creates glossary metadata from file")

        ap.add_file_arg(self)

    def run(
        self, props: CliqProperties, opts: argparse.Namespace, gc: GraphChainClient
    ):
        Util.pretty_print_json(gc.create_glossary_file(opts.file))
