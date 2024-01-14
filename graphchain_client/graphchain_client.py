import datetime
import json
import time
from enum import StrEnum
from typing import Optional, BinaryIO, List

from graphchain_client.http_client import HttpClient, HttpClientConsts


class JobStatus(StrEnum):
    COMPLETED_SUCCESS = "COMPLETED_SUCCESS"
    COMPLETED_ERROR = "COMPLETED_ERROR"
    CANCELLED = "CANCELLED"
    TIMEOUT = "TIMEOUT"


class GraphChainClient(object):
    """
    A class that add functions for commonly used REST call to GraphChain Server (LifeGraph)

    This class can continually build out; and should someday be part of a python wheel/dist
    """

    KEYCLOAK_BASE = "https://keycloak.app.burstiq.com/auth"
    KEYCLOAK_CLIENT_ID = "burst"

    MASTER_CUSTOMER = "biq_internal"
    MASTER_SDZ = "master_sdz"

    @staticmethod
    def get_token(
        realm: str,
        un: str,
        pw: str,
        keycloak_server: str = KEYCLOAK_BASE,
        keycloak_client_id: str = KEYCLOAK_CLIENT_ID,
    ) -> str:
        """
        get a JWT from keycloak

        :return: access token (refresh is not returned)
        :raises RuntimeError: if any REST error occurred
        """

        body = {
            "client_id": keycloak_client_id,
            "grant_type": "password",
            "username": un,
            "password": pw,
        }

        keycloak_client = HttpClient(keycloak_server, None, None, None, True)
        code, resp = keycloak_client.post_urlencoded(
            f"realms/{realm}/protocol/openid-connect/token", None, None, body
        )
        resp = json.loads(resp)
        return resp["access_token"]

    def __init__(
        self, graphchain_server: str, access_token: str, customer: str, sdz: str
    ):
        """
        connects to the graphchain server for the specific customer/sdz and access token
        """
        self._hc = HttpClient(graphchain_server, customer, sdz, access_token, True)

    def health_check(self) -> dict:
        _, resp = self._hc.get("management/info", None, None, None)
        return json.loads(resp)

    def drop_customer(self, customer: str):
        """
        drop a customer by short name (must be done with BIQ ADMIN)
        """
        self._hc.delete(f"api/directory/{customer}", None, None, None)

    def update_customer(self, customer_config: dict):
        """
        update the customer data/configuration (must be done with BIQ ADMIN)
        """
        self._hc.put(f"api/directory", None, None, customer_config)

    def drop_sdz(self, customer: str, sdz: str):
        """
        drop a customer's sdz by short name (must be done with BIQ ADMIN)
        """
        self._hc.delete(f"api/directory/{customer}/{sdz}", None, None, None)

    def predict(self, fn: str) -> (dict, dict):
        """
        uses the data filename to get a dictionary and mapping

        :return: dictionary, mapping
        """
        code, resp = self._hc.post_multipart(
            f"api/metadata/dictionary/predict", None, None, {"file": fn}, None
        )
        out = json.loads(resp)
        return out["dictionary"], out["mapping"]

    def update_dict(self, dictionary: dict):
        """
        loads a single dictionary
        todo move this to the JobManager version and return a job it
        """
        self._hc.put(f"api/metadata/dictionary", None, None, dictionary)

    def import_dbschema(
        self, dbschema_fn: str, email_results: Optional[str], delete: bool = True
    ) -> str:
        """
        import an entire dbschema; will be uploaded via job manager

        :return: job id
        """
        files = {"file": dbschema_fn}
        form = {
            "delete": str(delete).lower(),
            "emailResultsTo": str(email_results).lower(),
        }

        _, resp = self._hc.post_multipart(f"api/jobs/dbschema", None, None, files, form)
        resp = json.loads(resp)
        return resp["jobId"]

    def export_dbschema(self) -> str:
        """
        exports the SDZ's metadata (dictionary and edges) as a DbSchema file

        :return:dbschema file contents (xml)
        """
        hdrs = {
            HttpClientConsts.ACCEPT_HEADER.value: HttpClientConsts.XML_CONTENT_TYPE.value
        }

        _, resp = self._hc.get("api/dbschema", hdrs, None, None)
        return resp

    def truncate_chain(self, chain: str):
        self._hc.delete(f"api/graphchain/{chain}/truncate", None, None, None)

    def load_data(
        self,
        chain: str,
        fn: str,
        mapping: Optional[dict],
        transform: Optional[str],
        email_results: Optional[str],
    ) -> str:
        """
        load a data file via job manager

        :return: job id
        """
        files = {"file": fn, "map": mapping, "transform": transform}
        form = {"emailResultsTo": str(email_results).lower()}

        _, resp = self._hc.post_multipart(
            f"api/jobs/{chain}/upload", None, None, files, form
        )
        resp = json.loads(resp)
        return resp["jobId"]

    def query(self, tql: str) -> List[dict]:
        _, resp = self._hc.post("api/graphchain/query", None, None, {"query": tql})
        return json.loads(resp)

    def upsert(self, chain: str, metadata: Optional[dict], data: dict) -> dict:
        _, resp = self._hc.put(
            f"api/graphchain/{chain}/{id}",
            None,
            None,
            {"metadata": metadata, "data": data},
        )
        return json.loads(resp)

    def create_smart_contract(self, chain, name, js):
        _, resp = self._hc.post(
            f"api/graphchain/{chain}/smartcontracts",
            None,
            None,
            {"name": name, "javaScript": js},
        )
        return json.loads(resp)

    def execute_smart_contract(
        self, chain: str, sc_id: str, func: str, args: dict
    ) -> str:
        _, resp = self._hc.post_multipart(
            f"api/jobs/{chain}/smartcontracts/{sc_id}/{func}", None, None, None, args
        )

        resp = json.loads(resp)
        return resp["jobId"]

    def submit_download(self, chain: str, tql: str) -> str:
        """
        submits a job for downloading data
        todo - add things like email results, threads, col defs, etc

        :param chain:
        :param tql:

        :return: the job id
        """
        _, resp = self._hc.post_multipart(
            f"api/jobs/{chain}/download", None, None, None, {"tql": tql}
        )
        resp = json.loads(resp)
        return resp["jobId"]

    def download_file(self, job_id: str, f: BinaryIO):
        """
        will get a completed download job's file and save directory to file pointer (binary)

        :raises RuntimeError: if job_id does not exist
        """
        self._hc.get_octet(f"api/jobs/download/{job_id}", None, None, f)

    def wait(
        self, job_id: str, poll_secs: int = 3, timeout_mins: int = 10
    ) -> (JobStatus, dict):
        """
        will constantly poll for the job id to enter a completed or cancelled state OR timeout

        :return: the status of the job, and error results (if status is error)
        :raises RuntimeError: on missing job id (ie 404)
        """
        end_time = datetime.datetime.now() + datetime.timedelta(minutes=timeout_mins)
        while end_time > datetime.datetime.now():
            _, resp = self._hc.get(f"api/jobs/{job_id}", None, None, None)
            resp = json.loads(resp)
            if resp["status"] == JobStatus.COMPLETED_SUCCESS.value:
                return JobStatus.COMPLETED_SUCCESS, None
            elif resp["status"] == JobStatus.COMPLETED_ERROR.value:
                return JobStatus.COMPLETED_ERROR, resp
            elif resp["status"] == JobStatus.CANCELLED.value:
                return JobStatus.CANCELLED, None

            time.sleep(poll_secs)

        return JobStatus.TIMEOUT, None
