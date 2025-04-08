import argparse
import os
from shutil import copyfile

from arg_parse import ArgParse
from cliq_action_base import CliqActionBase
from cliq_properties import CliqProperties
from graphchain_client.graphchain_client import GraphChainClient
from util import Util


class MetadataExport(CliqActionBase):
    def __init__(self, ap: ArgParse):
        super().__init__("metadata_export")

        ap.add_cliq_action(self, "exports the metadata as Excel")

        ap.add_output_arg(self, desc="path for the file to be saved", req=True)

    def run(
        self, props: CliqProperties, opts: argparse.Namespace, gc: GraphChainClient
    ):
        temp_file = gc.export_metadata()

        cust, sdz = props.get_customer_sdz()
        fn = f"{Util.standardize_file(opts.output)}/{cust}_{sdz}_metadata.xlsx"
        print(f"saving metadata file: {fn}")
        copyfile(temp_file, fn)
        if os.path.exists(temp_file):
            os.remove(temp_file)
