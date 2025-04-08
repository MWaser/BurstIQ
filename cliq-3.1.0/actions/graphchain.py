import argparse

from arg_parse import ArgParse
from cliq_action_base import CliqActionBase
from cliq_properties import CliqProperties
from graphchain_client.graphchain_client import GraphChainClient
from util import Util


class GraphChainVersion(CliqActionBase):
    def __init__(self, ap: ArgParse):
        super().__init__("graphchain_version")

        ap.add_cliq_action(self, "graphchain server version")

    def run(
        self, props: CliqProperties, opts: argparse.Namespace, gc: GraphChainClient
    ):
        Util.pretty_print_json(gc.version())


class GraphChainHealth(CliqActionBase):
    def __init__(self, ap: ArgParse):
        super().__init__("graphchain_health")

        ap.add_cliq_action(self, "graphchain server health")

    def run(
        self, props: CliqProperties, opts: argparse.Namespace, gc: GraphChainClient
    ):
        Util.pretty_print_json(gc.health_check())


class GraphChainTruncate(CliqActionBase):
    def __init__(self, ap: ArgParse):
        super().__init__("graphchain_truncate")

        ap.add_cliq_action(self, "truncates a chain by name")

        ap.add_chain_arg(self)
        ap.add_email_arg(
            self, "the email to send the results of the truncate to", False
        )
        ap.add_wait_arg(self)

    def run(
        self, props: CliqProperties, opts: argparse.Namespace, gc: GraphChainClient
    ):
        job_id = gc.truncate_chain(opts.chain, opts.email)
        if opts.wait:
            Util.wait_status(gc, job_id)


class GraphChainDrop(CliqActionBase):
    def __init__(self, ap: ArgParse):
        super().__init__("graphchain_drop")

        ap.add_cliq_action(
            self,
            "drop a chain by name; includes metadata (dictionary and edge defs) plus all data and edges",
        )

        ap.add_chain_arg(self)
        ap.add_email_arg(self, "the email to send the results of the drop to", False)
        ap.add_wait_arg(self)

    def run(
        self, props: CliqProperties, opts: argparse.Namespace, gc: GraphChainClient
    ):
        job_id = gc.drop_chain(opts.chain, opts.email)
        if opts.wait:
            Util.wait_status(gc, job_id)


class GraphChainWipe(CliqActionBase):
    def __init__(self, ap: ArgParse):
        super().__init__("graphchain_wipe")

        ap.add_cliq_action(
            self,
            "wipe an sdz; WARNING: removes all data (assets, edges, ccs, scs, etc); does NOT remove metadata (dictionary and edge defs)",
        )

        ap.add_email_arg(self, "the email to send the results of the wipe", False)
        ap.add_wait_arg(self)

    def run(
        self, props: CliqProperties, opts: argparse.Namespace, gc: GraphChainClient
    ):
        job_id = gc.wipe(opts.email)
        if opts.wait:
            Util.wait_status(gc, job_id)


class GraphChainReset(CliqActionBase):
    def __init__(self, ap: ArgParse):
        super().__init__("graphchain_reset")

        ap.add_cliq_action(
            self,
            "reset an sdz (to original state); WARNING: removes all data (assets, edges, ccs, scs, etc) AND all metadata (dictionary and edge defs)",
        )

        ap.add_email_arg(self, "the email to send the results of the reset", False)
        ap.add_wait_arg(self)

    def run(
        self, props: CliqProperties, opts: argparse.Namespace, gc: GraphChainClient
    ):
        job_id = gc.reset(opts.email)
        if opts.wait:
            Util.wait_status(gc, job_id)
