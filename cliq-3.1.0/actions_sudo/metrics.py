import argparse

from arg_parse import ArgParse
from cliq_action_base import CliqActionBase
from cliq_properties import CliqProperties
from graphchain_client.graphchain_client import GraphChainClient


class MetricsBilling(CliqActionBase):
    def __init__(self, ap: ArgParse):
        super().__init__("metrics_billing")

        ap.add_cliq_action(
            self,
            "get the XLSX file of current customer/sdz usage for billing purposes via email (async)",
        )

        ap.add_email_arg(self, req=True)

    def run(
        self, props: CliqProperties, opts: argparse.Namespace, gc: GraphChainClient
    ):
        gc.get_billing(opts.email)
