import argparse
import json

from arg_parse import ArgParse
from cliq_action_base import CliqActionBase
from cliq_properties import CliqProperties
from graphchain_client.graphchain_client import GraphChainClient
from util import Util


class IngestPipelineList(CliqActionBase):
    def __init__(self, ap: ArgParse):
        super().__init__("ingest_pipeline_list")

        ap.add_cliq_action(self, "list the ingest pipelines in the system")

    def run(
        self, props: CliqProperties, opts: argparse.Namespace, gc: GraphChainClient
    ):
        resp = gc.list_ingest_pipeline()
        Util.pretty_print_json(resp)


class IngestPipelineGet(CliqActionBase):
    def __init__(self, ap: ArgParse):
        super().__init__("ingest_pipeline_get")

        ap.add_cliq_action(self, "gets an ingest pipeline")

        ap.add_id_arg(self, "id of the existing pipeline")

    def run(
        self, props: CliqProperties, opts: argparse.Namespace, gc: GraphChainClient
    ):
        resp = gc.get_ingest_pipeline(opts.id)
        Util.pretty_print_json(resp)


class IngestPipelineCreate(CliqActionBase):
    def __init__(self, ap: ArgParse):
        super().__init__("ingest_pipeline_create")

        ap.add_cliq_action(self, "creates a ingest pipeline JSON metadata file")

        ap.add_file_arg(self)

    def run(
        self, props: CliqProperties, opts: argparse.Namespace, gc: GraphChainClient
    ):
        with open(opts.file, "rb") as f:
            pipeline = json.load(f)

        gc.create_ingest_pipeline(pipeline)


class IngestPipelineUpdate(CliqActionBase):
    def __init__(self, ap: ArgParse):
        super().__init__("ingest_pipeline_update")

        ap.add_cliq_action(self, "updates an ingest pipeline JSON metadata file")

        ap.add_file_arg(self)
        ap.add_id_arg(self, "id of the existing pipeline")

    def run(
        self, props: CliqProperties, opts: argparse.Namespace, gc: GraphChainClient
    ):
        with open(opts.file, "rb") as f:
            pipeline = json.load(f)

        gc.update_ingest_pipeline(pipeline, opts.id)


class IngestPipelineDelete(CliqActionBase):
    def __init__(self, ap: ArgParse):
        super().__init__("ingest_pipeline_delete")

        ap.add_cliq_action(self, "delete an ingest pipeline")

        ap.add_id_arg(self, "id of the existing pipeline")

    def run(
        self, props: CliqProperties, opts: argparse.Namespace, gc: GraphChainClient
    ):
        gc.delete_ingest_pipeline(opts.id)
