import argparse
import json
from abc import ABC, abstractmethod

from cliq_properties import CliqProperties
from graphchain_client.graphchain_client import GraphChainClient, JobStatus


class CliqAction(ABC):
    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def run(self, opts: argparse.Namespace, props: CliqProperties):
        raise NotImplementedError()

    @staticmethod
    def _add_name_arg(
        parser: argparse.ArgumentParser, desc: str = "the short name of the customer"
    ):
        """
        consistent setup for customer name argument
        """
        parser.add_argument(
            "--name", "-n", dest="name", help=desc, type=str, required=True
        )

    @staticmethod
    def _add_sdz_arg(
        parser: argparse.ArgumentParser, desc: str = "the short name of the sdz"
    ):
        """
        consistent setup for sdz argument
        """
        parser.add_argument(
            "--sdz", "-s", dest="sdz", help=desc, type=str, required=True
        )

    @staticmethod
    def _add_chain_arg(
        parser: argparse.ArgumentParser, desc: str = "the chain name for the data"
    ):
        """
        consistent setup for chain argument
        """
        parser.add_argument(
            "--chain", "-c", dest="chain", help=desc, type=str, required=True
        )

    @staticmethod
    def _add_file_arg(
        parser: argparse.ArgumentParser,
        desc: str = "the file path for the input",
        req: bool = True,
    ):
        """
        consistent setup for file argument
        """
        parser.add_argument(
            "--file", "-f", dest="file", help=desc, type=str, required=req
        )

    @staticmethod
    def _add_output_arg(
        parser: argparse.ArgumentParser,
        desc: str = "the output path; optional, default is stdout",
    ):
        """
        consistent setup for output argument
        """
        parser.add_argument(
            "--output", "-o", dest="output", help=desc, type=str, required=False
        )

    @staticmethod
    def _add_email_arg(
        parser: argparse.ArgumentParser,
        desc: str = "the email to send the results of the job to",
    ):
        """
        consistent setup for output argument
        """
        parser.add_argument(
            "--email", "-e", dest="email", help=desc, type=str, required=False
        )

    @staticmethod
    def _add_wait_arg(
        parser: argparse.ArgumentParser,
        desc: str = "should the tool wait (and poll) for the results of the async job; default --no-wait",
    ):
        """
        consistent setup for wait argument
        """
        parser.add_argument(
            "--wait",
            dest="wait",
            help=desc,
            action=argparse.BooleanOptionalAction,
            type=bool,
            default=False,
        )

    @staticmethod
    def _get_biq_admin(props: CliqProperties) -> GraphChainClient:
        return GraphChainClient(
            props.get_graphchain(),
            props.get_biq_admin_token(),
            GraphChainClient.MASTER_CUSTOMER,
            GraphChainClient.MASTER_SDZ,
        )

    @staticmethod
    def _get_sdz_admin(props: CliqProperties) -> GraphChainClient:
        cust, sdz = props.get_graphchain_customer()
        return GraphChainClient(
            props.get_graphchain(), props.get_sdz_admin_token(), cust, sdz
        )

    @staticmethod
    def _wait(gc: GraphChainClient, job_id: str):
        status, err = gc.wait(job_id)
        match status:
            case JobStatus.COMPLETED_ERROR:
                print(f"ERROR {job_id}:\n{json.dumps(err, indent=2)}")
            case JobStatus.CANCELLED:
                print(f"CANCELLED {job_id}")
            case JobStatus.TIMEOUT:
                print(f"TIMEOUT {job_id}")
