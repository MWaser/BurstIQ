import argparse

from arg_parse import ArgParse
from cliq_action_base import CliqActionBase
from cliq_properties import CliqProperties
from graphchain_client.graphchain_client import GraphChainClient
from util import Util


class JobList(CliqActionBase):
    def __init__(self, ap: ArgParse):
        super().__init__("job_list")

        ap.add_cliq_action(self, "list the jobs in the system")

    def run(
        self, props: CliqProperties, opts: argparse.Namespace, gc: GraphChainClient
    ):
        Util.pretty_print_json(gc.list_jobs())


class JobCancel(CliqActionBase):
    def __init__(self, ap: ArgParse):
        super().__init__("job_cancel")

        ap.add_cliq_action(self, "cancels a job in the system")

        ap.add_id_arg(self, "job id", True)

    def run(
        self, props: CliqProperties, opts: argparse.Namespace, gc: GraphChainClient
    ):
        gc.cancel_job(opts.id)
