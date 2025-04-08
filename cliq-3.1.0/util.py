import json
import os

from graphchain_client.graphchain_client import GraphChainClient, JobStatus


class Util(object):
    @staticmethod
    def standardize_file(fn: str) -> None | str:
        if fn:
            fn = os.path.expanduser(fn)
            fn = os.path.expandvars(fn)
            fn = os.path.abspath(fn)
            return fn
        else:
            return None

    @staticmethod
    def pretty_print_json(j):
        print(json.dumps(j, indent=2))

    @staticmethod
    def wait_status(gc: GraphChainClient, job_id: str):
        status, err = gc.wait(job_id)
        match status:
            case JobStatus.COMPLETED_ERROR:
                Util.pretty_print_json(err)
            case JobStatus.CANCELLED:
                print(f"CANCELLED {job_id}")
            case JobStatus.TIMEOUT:
                print(f"TIMEOUT {job_id}")
