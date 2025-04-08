import argparse
import json
import sys

from arg_parse import ArgParse
from cliq_action_base import CliqActionBase
from cliq_properties import CliqProperties
from graphchain_client.graphchain_client import GraphChainClient
from util import Util


class DataQuery(CliqActionBase):
    def __init__(self, ap: ArgParse):
        super().__init__("data_query")

        ap.add_cliq_action(
            self,
            "queries data with TQL from argument, file, or stdin (default); "
            "plus prints results to stdout or to a file",
        )

        ap.add_arg(
            self,
            "--query",
            "-q",
            "query",
            "the query to execute. ignores -f option",
            req=False,
        )

        ap.add_arg(
            self,
            "--file",
            "-f",
            "file",
            "file path name or stdin/redirect (if both -q and -f are both omitted)",
            arg_type=argparse.FileType("r"),
            req=False,
        )

        ap.add_system_wallet_id_arg(self)
        ap.add_output_arg(self)

    def run(
        self, props: CliqProperties, opts: argparse.Namespace, gc: GraphChainClient
    ):
        if opts.query is not None:
            # user specified the query on the cmd line
            query = opts.query
        elif opts.file is not None:
            # read from a file
            query = opts.file.read()
        else:
            print("enter TQL on command line, type Ctrl-D when done")
            query = sys.stdin.read()

        results = gc.query_plain(query, opts.system_wallet_id)
        if opts.output is None:
            Util.pretty_print_json(results)
        else:
            with open(Util.standardize_file(opts.output), "wt") as f:
                json.dump(results, f, indent=2)


class DataDelete(CliqActionBase):
    def __init__(self, ap: ArgParse):
        super().__init__("data_delete")

        ap.add_cliq_action(self, "delete data (smart data object) by id")

        ap.add_system_wallet_id_arg(self)
        ap.add_chain_arg(self)
        ap.add_list_arg(
            self,
            "--ids",
            "-i",
            "ids",
            "One or many SDO ids to delete for a given chain",
        )

    def run(
        self, props: CliqProperties, opts: argparse.Namespace, gc: GraphChainClient
    ):
        id_count = len(opts.ids)
        count = 1
        for sdoid in opts.ids:
            print(f"{count:03}/{id_count:03} - Deleting {sdoid} from {opts.chain}")
            gc.delete_sdo(opts.chain, sdoid, opts.system_wallet_id)
            count = count + 1


class DataBlobCreate(CliqActionBase):
    def __init__(self, ap: ArgParse):
        super().__init__("data_blob_create")

        ap.add_cliq_action(self, "create blob for data (SDO)")

        ap.add_arg(
            self,
            "--attribute",
            "-a",
            "attribute",
            "the blob attribute",
        )
        ap.add_system_wallet_id_arg(self)
        ap.add_id_arg(self)
        ap.add_chain_arg(self)
        ap.add_file_arg(self, "the blob file")

    def run(
        self, props: CliqProperties, opts: argparse.Namespace, gc: GraphChainClient
    ):
        gc.add_blob(
            opts.chain, opts.id, opts.attribute, opts.file, opts.system_wallet_id
        )


class DataVerificationAdd(CliqActionBase):
    def __init__(self, ap: ArgParse):
        super().__init__("data_verification_add")

        ap.add_cliq_action(self, "add a verification to a SDO by ID")

        ap.add_chain_arg(self)
        ap.add_id_arg(self, "ID of the SDO")
        ap.add_file_arg(self, "JSON verification data file")

    def run(
        self, props: CliqProperties, opts: argparse.Namespace, gc: GraphChainClient
    ):
        with open(Util.standardize_file(opts.file), "rt") as f:
            verification = json.load(f)

        Util.pretty_print_json(gc.add_verification(opts.chain, opts.id, verification))


class DataLoad(CliqActionBase):
    def __init__(self, ap: ArgParse):
        super().__init__("data_load")

        ap.add_cliq_action(self, "loads data file as an async job")

        ap.add_chain_arg(self)
        ap.add_file_arg(self)
        ap.add_arg(
            self,
            "--pipeline",
            "-ip",
            "ingest_pipeline_name",
            "the name of the ingest pipeline to execute",
            req=False,
        )
        ap.add_arg(
            self,
            "--metadata",
            "-d",
            "metadata",
            "JSON string of metadata to store with each SDO created or updated",
            req=False,
        )
        ap.add_list_arg(
            self,
            "--owners",
            "-o",
            "owners",
            "List of owners",
            nargs="+",
        )
        ap.add_list_arg(
            self,
            "--limited_owners",
            "-l",
            "limited_owners",
            "List of limited owners",
            nargs="+",
        )
        ap.add_sheet_arg(self)
        ap.add_threads_arg(self)
        ap.add_system_wallet_id_arg(self)
        ap.add_email_arg(self, "the email to send the results of the job to", False)
        ap.add_wait_arg(self)

    def run(
        self, props: CliqProperties, opts: argparse.Namespace, gc: GraphChainClient
    ):
        job_id = gc.load_data(
            opts.chain,
            opts.file,
            opts.sheet,
            opts.owners,
            opts.limited_owners,
            opts.ingest_pipeline_name,
            opts.email,
            opts.metadata,
            opts.threads,
            opts.system_wallet_id,
        )

        if opts.wait:
            Util.wait_status(gc, job_id)


class DataExport(CliqActionBase):
    def __init__(self, ap: ArgParse):
        super().__init__("data_export")

        ap.add_cliq_action(self, "exports all the data from a chain as JSON")
        ap.add_chain_arg(self)
        ap.add_output_arg(self, req=True)
        ap.add_description_arg(self, req=False)
        ap.add_email_arg(self, req=False)
        ap.add_wait_arg(self)
        ap.add_arg(
            self,
            "--limit",
            "-l",
            "limit",
            "the limit value",
            arg_type=int,
            req=False,
        )
        ap.add_arg(
            self,
            "--skip",
            "-s",
            "skip",
            "the skip value",
            arg_type=int,
            req=False,
        )

    def run(
        self, props: CliqProperties, opts: argparse.Namespace, gc: GraphChainClient
    ):
        job_id = gc.submit_export(
            opts.chain, opts.description, opts.email, opts.limit, opts.skip
        )

        if opts.wait:
            Util.wait_status(gc, job_id)

            cust, sdz = props.get_customer_sdz()
            fn = f"{Util.standardize_file(opts.output)}/{cust}_{sdz}_{opts.chain}.json"
            print(f"saving export JSON file: {fn}")
            with open(fn, "wb") as f:
                gc.download_file(job_id, f)
        else:
            print(f"{job_id}")


class DataDownload(CliqActionBase):
    def __init__(self, ap: ArgParse):
        super().__init__("data_download")

        ap.add_cliq_action(self, "download data from a chain")

        ap.add_output_arg(self, req=True)
        ap.add_description_arg(self, req=False)
        ap.add_email_arg(self, req=False)
        ap.add_wait_arg(self)
        ap.add_arg(
            self,
            "--tql",
            "-t",
            "tql",
            "the tql to execute",
        )
        ap.add_enum_arg(
            self,
            "--fileType",
            "-f",
            "file_type",
            "the type of output file (CSV [default], JSON, XLSX)",
            choices=["CSV", "JSON", "XLSX"],
            req=False,
            default="CSV",
        )

    def run(
        self, props: CliqProperties, opts: argparse.Namespace, gc: GraphChainClient
    ):
        if opts.file_type:
            file_type = opts.file_type.upper()
        else:
            file_type = "CSV"

        job_id = gc.submit_download(opts.tql, file_type, opts.description)

        if opts.wait:
            Util.wait_status(gc, job_id)

            cust, sdz = props.get_customer_sdz()
            fn = f"{Util.standardize_file(opts.output)}/{cust}_{sdz}_download.{file_type.lower()}"
            print(f"saving download file: {fn}")
            with open(fn, "wb") as f:
                gc.download_file(job_id, f)
        else:
            print(f"{job_id}")
