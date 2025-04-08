import datetime
import json
import tempfile
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
    _BIQ_SYSTEM_WALLET_ID = "GraphChainClient._BIQ_SYSTEM_WALLET_ID"

    """
    A class that add functions for commonly used REST call to GraphChain Server (LifeGraph)

    This class can continually build out; and should someday be part of a python wheel/dist
    """

    def __init__(self, http_client: HttpClient):
        self._http_client = http_client

    def health_check(self) -> dict:
        _, resp = self._http_client.get("management/health", None, None, None)
        return json.loads(resp)

    def version(self) -> dict:
        _, resp = self._http_client.get("management/info", None, None, None)
        return json.loads(resp)

    def get_customer(self, customer: str) -> dict:
        """
        get a customer by short name (must be done with BIQ ADMIN)
        """
        _, resp = self._http_client.get(f"api/directory/{customer}", None, None, None)
        return json.loads(resp)

    def list_customers(self) -> list[str]:
        """
        get a list of customer short names (must be done with BIQ ADMIN)
        """
        _, resp = self._http_client.get(f"api/directory", None, None, None)

        customers = json.loads(resp)
        short_names = []
        for customer in customers:
            short_names.append(customer["shortName"])
        return short_names

    def list_messages(self, days: str) -> list:
        """
        get a list of messages from the message center
        """
        query = {"daysToReturn": days}
        _, resp = self._http_client.get(f"api/message", None, query, None)

        return json.loads(resp)

    def drop_customer(self, customer: str):
        """
        drop a customer by short name (must be done with BIQ ADMIN)
        """
        self._http_client.delete(f"api/directory/{customer}", None, None, None)

    def update_customer(self, name: str, customer_config: dict):
        """
        update the customer data/configuration (must be done with BIQ ADMIN)
        """
        self._http_client.put(f"api/directory/{name}", None, None, customer_config)

    def create_customer(self, customer_config: dict):
        """
        create the customer data/configuration (must be done with BIQ ADMIN)
        """
        self._http_client.post(f"api/directory", None, None, customer_config)

    def clear_caches(self):
        """
        clear cache (must be done with BIQ ADMIN)
        """
        self._http_client.post(f"api/directory/clearcaches", None, None, None)

    def drop_sdz(self, customer: str, sdz: str):
        """
        drop a customer's sdz by short name (must be done with BIQ ADMIN)
        """
        self._http_client.delete(f"api/directory/{customer}/{sdz}", None, None, None)

    def predict(self, fn: str, sheet: str) -> (dict, dict):
        """
        uses the data filename to get a dictionary and mapping

        :return: dictionary, mapping
        """
        form = {}
        if sheet:
            if sheet.isnumeric():
                form["sheetNum"] = int(sheet)
            else:
                form["sheetName"] = sheet

        code, resp = self._http_client.post_multipart(
            f"api/metadata/dictionary/predict", None, None, {"file": fn}, form
        )
        out = json.loads(resp)
        return out["dictionary"], out["mapping"]

    def update_dict(self, dictionary: dict, email_results: Optional[str]) -> str:
        """
        loads a single dictionary as upsert func
        """
        body = {
            "dictionary": dictionary,
            "emailResultsTo": str(email_results).lower(),
        }

        _, resp = self._http_client.post(f"api/jobs/dictionary", None, None, body)
        resp = json.loads(resp)
        return resp["jobId"]

    def update_user_group(
        self, group_id: str, name: str, group: list, description: Optional[str]
    ) -> dict:
        """
        update a user group
        """
        body = {"name": name, "description": description, "group": group}

        _, resp = self._http_client.put(
            f"api/metadata/usergroup/{group_id}", None, None, body
        )
        return json.loads(resp)

    def list_dicts(self) -> list:
        """
        gets a list of dictionaries
        """
        _, resp = self._http_client.get(f"api/metadata/dictionary", None, None, None)
        out = json.loads(resp)
        dicts = []
        for d in out:
            dicts.append(d["name"])
        return dicts

    def add_verification(self, chain: str, sdo_id: str, verification: dict):
        """
        add a verification
        """
        _, resp = self._http_client.put(
            f"api/graphchain/{chain}/{sdo_id}/verification", None, None, verification
        )
        return json.loads(resp)

    def list_user_groups(self, name: Optional[str], description: Optional[str]) -> list:
        """
        gets a list of user groups
        """
        query = {}
        if name:
            query["name"] = name
        if description:
            query["description"] = description

        _, resp = self._http_client.get(f"api/metadata/usergroup", None, query, None)
        return json.loads(resp)

    def list_user_wallets(self, email: Optional[str], name: Optional[str]) -> list:
        """
        gets a list of user wallets
        """
        query = {}
        if email:
            query["email"] = email
        if name:
            query["fullName"] = name

        _, resp = self._http_client.get(f"api/metadata/user/wallet", None, query, None)
        return json.loads(resp)

    def list_system_wallets(
        self, description: Optional[str], wallet_type: Optional[str]
    ) -> list:
        """
        gets a list of system wallets
        """
        query = {}
        if description:
            query["description"] = description
        if wallet_type:
            query["type"] = wallet_type

        _, resp = self._http_client.get(
            f"api/metadata/system/wallet", None, query, None
        )
        return json.loads(resp)

    def list_consent_contracts(self, chain: str, system_wallet_id: str) -> list:
        """
        list consent contracts
        """
        headers = {}
        if system_wallet_id is not None:
            headers[GraphChainClient._BIQ_SYSTEM_WALLET_ID] = str(system_wallet_id)

        _, resp = self._http_client.get(
            f"api/graphchain/{chain}/query/consentcontracts", headers, None, None
        )
        return json.loads(resp)

    def list_smart_contracts(self, chain: str, system_wallet_id: Optional[str]) -> list:
        """
        list smart contracts
        """
        headers = {}
        if system_wallet_id is not None:
            headers[GraphChainClient._BIQ_SYSTEM_WALLET_ID] = system_wallet_id

        _, resp = self._http_client.get(
            f"api/graphchain/{chain}/query/smartcontracts", headers, None, None
        )
        return json.loads(resp)

    def get_dict(self, chain: str) -> dict:
        """
        gets a list of dictionaries
        """
        _, resp = self._http_client.get(
            f"api/metadata/dictionary/{chain}", None, None, None
        )
        return json.loads(resp)

    def get_user_wallet(self, wallet_id: str) -> dict:
        """
        get a user wallet by id
        """
        _, resp = self._http_client.get(
            f"api/metadata/user/wallet/{wallet_id}", None, None, None
        )
        return json.loads(resp)

    def get_user_group(self, group_id: str) -> dict:
        """
        get a user wallet by id
        """
        _, resp = self._http_client.get(
            f"api/metadata/usergroup/{group_id}", None, None, None
        )
        return json.loads(resp)

    def get_system_wallet(self, wallet_id: str) -> dict:
        """
        get a system wallet by id
        """
        _, resp = self._http_client.get(
            f"api/metadata/system/wallet/{wallet_id}", None, None, None
        )
        return json.loads(resp)

    def delete_dict(self, chain: str):
        """
        delete a dictionary by chain name
        """
        self._http_client.delete(f"api/metadata/dictionary/{chain}", None, None, None)

    def delete_user_group(self, group_id: str):
        """
        get a user group by id
        """
        self._http_client.delete(f"api/metadata/usergroup/{group_id}", None, None, None)

    def delete_user_wallet(self, wallet_id: str):
        """
        get a user wallet by id
        """
        self._http_client.delete(
            f"api/metadata/user/wallet/{wallet_id}", None, None, None
        )

    def delete_system_wallet(self, wallet_id: str):
        """
        get a system wallet by id
        """
        self._http_client.delete(
            f"api/metadata/system/wallet/{wallet_id}", None, None, None
        )

    def delete_sdo(self, chain: str, sdo_id: str, system_wallet_id: Optional[str]):
        """
        delete an any SDO by id.
        """
        headers = {}
        if system_wallet_id is not None:
            headers[GraphChainClient._BIQ_SYSTEM_WALLET_ID] = str(system_wallet_id)

        self._http_client.delete(
            f"api/graphchain/{chain}/{sdo_id}", headers, None, None
        )

    def delete_edge(self, chain: str, edge_id: str, system_wallet_id: Optional[str]):
        """
        delete an edge by id.
        """
        headers = {}
        if system_wallet_id is not None:
            headers[GraphChainClient._BIQ_SYSTEM_WALLET_ID] = str(system_wallet_id)

        self._http_client.delete(
            f"api/graphchain/{chain}/edges/{edge_id}", headers, None, None
        )

    def get_edge(
        self, chain: str, edge_id: str, system_wallet_id: Optional[str]
    ) -> dict:
        """
        get an edge by id.
        """
        headers = {}
        if system_wallet_id is not None:
            headers[GraphChainClient._BIQ_SYSTEM_WALLET_ID] = str(system_wallet_id)

        _, resp = self._http_client.get(
            f"api/graphchain/{chain}/edges/{edge_id}", headers, None, None
        )
        return json.loads(resp)

    def update_edge(
        self,
        chain: str,
        edge_id: str,
        properties: dict,
        system_wallet_id: Optional[str],
    ) -> dict:
        """
        get an edge by id.
        """
        headers = {}
        if system_wallet_id is not None:
            headers[GraphChainClient._BIQ_SYSTEM_WALLET_ID] = str(system_wallet_id)

        body = {"properties": properties}

        _, resp = self._http_client.put(
            f"api/graphchain/{chain}/edges/{edge_id}", headers, None, body
        )
        return json.loads(resp)

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

        _, resp = self._http_client.post_multipart(
            f"api/jobs/dbschema", None, None, files, form
        )
        resp = json.loads(resp)
        return resp["jobId"]

    def add_blob(
        self,
        chain: str,
        sdo_id: str,
        attribute: str,
        blob: str,
        system_wallet_id: Optional[str],
    ) -> str:
        """
        add a blob to an sdo on a chain for a given attribute

        :return: blob sdo
        """
        headers = {}
        if system_wallet_id is not None:
            headers[GraphChainClient._BIQ_SYSTEM_WALLET_ID] = str(system_wallet_id)

        files = {"file": blob}

        _, resp = self._http_client.post_multipart(
            f"api/graphchain/{chain}/{sdo_id}/{attribute}/blobs",
            headers,
            None,
            files,
            None,
        )
        return json.loads(resp)

    def export_dbschema(self) -> str:
        """
        exports the SDZ's metadata (dictionary and edges) as a DbSchema file

        :return:dbschema file contents (xml)
        """
        hdrs = {
            HttpClientConsts.ACCEPT_HEADER.value: HttpClientConsts.XML_CONTENT_TYPE.value
        }

        _, resp = self._http_client.get("api/dbschema", hdrs, None, None)
        return resp

    def export_metadata(self) -> str:
        """
        exports the SDZ's metadata (dictionary and edges) as an Excel file

        :return: temp Excel filename (xlsx)
        """
        with tempfile.NamedTemporaryFile(
            "wb", suffix=".xlsx", delete=False, delete_on_close=False
        ) as f:
            self._http_client.get_octet("api/metadata/export", None, None, f)
        return f.name

    def truncate_chain(self, chain: str, email_results: str) -> str:
        body = {}
        if email_results:
            body["emailResultsTo"] = [email_results]
        _, resp = self._http_client.post(f"api/jobs/{chain}/truncate", None, None, body)
        resp = json.loads(resp)
        return resp["jobId"]

    def drop_chain(self, chain: str, email_results: str) -> str:
        body = {}
        if email_results:
            body["emailResultsTo"] = [email_results]
        _, resp = self._http_client.post(f"api/jobs/{chain}/drop", None, None, body)
        resp = json.loads(resp)
        return resp["jobId"]

    def wipe(self, email_results: str) -> str:
        body = {}
        if email_results:
            body["emailResultsTo"] = [email_results]
        _, resp = self._http_client.post(f"api/jobs/sdz/wipe", None, None, body)
        resp = json.loads(resp)
        return resp["jobId"]

    def reset(self, email_results: str) -> str:
        body = {}
        if email_results:
            body["emailResultsTo"] = [email_results]
        _, resp = self._http_client.post(f"api/jobs/sdz/reset", None, None, body)
        resp = json.loads(resp)
        return resp["jobId"]

    def load_data(
        self,
        chain: str,
        fn: str,
        sheet: str,
        owners: Optional[dict],
        limited_owners: Optional[dict],
        pipeline: Optional[str],
        email_results: Optional[str],
        metadata: Optional[dict],
        threads: Optional[int],
        system_wallet_id: Optional[str],
    ) -> str:
        """
        load a data file via job manager

        :return: job id
        """
        headers = {}
        if system_wallet_id is not None:
            headers[GraphChainClient._BIQ_SYSTEM_WALLET_ID] = str(system_wallet_id)

        files = {"file": fn}

        form = {}

        if threads:
            form["numThreads"] = str(threads)

        if pipeline:
            form["ingestPipelineName"] = pipeline

        if email_results:
            form["emailResultsTo"] = email_results.lower()

        if metadata:
            form["metadata"] = metadata

        if sheet:
            form["sheetName"] = sheet

        if owners:
            form["owners"] = json.dumps(owners)

        if limited_owners:
            form["limitedOwners"] = json.dumps(limited_owners)

        _, resp = self._http_client.post_multipart(
            f"api/jobs/{chain}/upload", headers, None, files, form
        )
        resp = json.loads(resp)
        return resp["jobId"]

    def create_message(self, file: str, title, message_type: str, date: str) -> dict:
        """
        create message in the message center (must be done with BIQ ADMIN)
        """
        files = {"file": file}
        form = {"title": title, "messageType": message_type, "createDate": date}

        _, resp = self._http_client.post_multipart(
            "api/message", None, None, files, form
        )
        return json.loads(resp)

    def delete_message(self, message_id: str):
        """
        delete message in the message center (must be done with BIQ ADMIN)
        """
        self._http_client.delete(f"api/message/{message_id}", None, None, None)

    def query_plain(self, tql: str, system_wallet_id: Optional[str]) -> List[dict]:
        headers = {}
        if system_wallet_id is not None:
            headers[GraphChainClient._BIQ_SYSTEM_WALLET_ID] = str(system_wallet_id)

        _, resp = self._http_client.post_plain_text(
            "api/graphchain/query", headers, None, tql
        )
        return json.loads(resp)

    def upsert(self, chain: str, metadata: Optional[dict], data: dict) -> dict:
        _, resp = self._http_client.put(
            f"api/graphchain/{chain}/{id}",
            None,
            None,
            {"metadata": metadata, "data": data},
        )
        return json.loads(resp)

    def create_smart_contract(self, chain, name, js, system_wallet_id: Optional[str]):
        headers = {}
        if system_wallet_id is not None:
            headers[GraphChainClient._BIQ_SYSTEM_WALLET_ID] = str(system_wallet_id)

        _, resp = self._http_client.post(
            f"api/graphchain/{chain}/smartcontracts",
            headers,
            None,
            {"name": name, "javaScript": js},
        )
        return json.loads(resp)

    def create_system_wallet(
        self, description: str, wallet_type: str, acug: str, write: Optional[str]
    ) -> dict:
        """
        create a system wallet
        """
        body = {
            "description": description,
            "type": wallet_type,
            "accessControlUserGroup": acug,
            "writeUserGroup": write,
        }

        _, resp = self._http_client.post(
            f"api/metadata/system/wallet", None, None, body
        )
        return json.loads(resp)

    def create_consent_contract(
        self,
        chain: str,
        contract: dict,
        metadata: Optional[dict],
        system_wallet_id: Optional[str],
    ):
        headers = {}
        if system_wallet_id is not None:
            headers[GraphChainClient._BIQ_SYSTEM_WALLET_ID] = str(system_wallet_id)

        request = {"consentContract": contract}
        if metadata:
            request["metadata"] = metadata

        _, resp = self._http_client.post(
            f"api/graphchain/{chain}/consentcontracts",
            headers,
            None,
            request,
        )
        return json.loads(resp)

    def create_user_group(
        self, name: str, group: list, description: Optional[str]
    ) -> dict:
        """
        create a user group
        """
        body = {"name": name, "description": description, "group": group}

        _, resp = self._http_client.post(f"api/metadata/usergroup", None, None, body)
        return json.loads(resp)

    def create_user_wallet(self, email: str, name: str) -> dict:
        """
        create a user wallet
        """
        body = {"email": email, "fullName": name}

        _, resp = self._http_client.post(f"api/metadata/user/wallet", None, None, body)
        return json.loads(resp)

    def execute_smart_contract(
        self,
        chain: str,
        sc_id: str,
        func: str,
        args: dict,
        system_wallet_id: Optional[str],
    ) -> str:
        headers = {}
        if system_wallet_id is not None:
            headers[GraphChainClient._BIQ_SYSTEM_WALLET_ID] = str(system_wallet_id)

        _, resp = self._http_client.post_multipart(
            f"api/jobs/{chain}/smartcontracts/{sc_id}/{func}", headers, None, None, args
        )

        resp = json.loads(resp)
        return resp["jobId"]

    def submit_export(
        self,
        chain: str,
        desc: Optional[str],
        email: Optional[str],
        limit: Optional[int],
        skip: Optional[int],
    ) -> str:
        form = {}
        if desc:
            form["description"] = desc

        if email:
            form["emailResultsTo"] = [email]

        if limit:
            form["limit"] = limit

        if skip:
            form["skip"] = skip

        _, resp = self._http_client.post(f"api/jobs/{chain}/export", None, None, form)
        resp = json.loads(resp)
        return resp["jobId"]

    def get_billing(self, email: str):
        query_params = {"email": email}
        self._http_client.get("api/metrics/billing", None, query_params, None)

    def submit_download(self, tql: str, file_type: str, desc: Optional[str]) -> str:
        """
        submits a job for downloading data
        """
        form = {
            "tql": tql,
            "fileType": file_type,
        }

        if desc:
            form["description"] = desc

        _, resp = self._http_client.post(f"api/jobs/download", None, None, form)
        resp = json.loads(resp)
        return resp["jobId"]

    def download_file(self, job_id: str, f: BinaryIO):
        """
        will get a completed download job's file and save directory to file pointer (binary)

        :raises RuntimeError: if job_id does not exist
        """
        self._http_client.get_octet(f"api/jobs/download/{job_id}", None, None, f)

    def create_manual_edge(
        self,
        from_chain: str,
        from_sdo_id: str,
        to_chain: str,
        to_sdo_id: str,
        label: str,
        properties: Optional[dict],
        system_wallet_id: Optional[str],
    ):
        body = {"label": label, "toDict": to_chain, "toSdoId": to_sdo_id}

        if properties:
            body["properties"] = properties

        headers = {}
        if system_wallet_id is not None:
            headers[GraphChainClient._BIQ_SYSTEM_WALLET_ID] = str(system_wallet_id)

        _, resp = self._http_client.post(
            f"api/graphchain/{from_chain}/{from_sdo_id}/edges", headers, None, body
        )
        return json.loads(resp)

    def create_glossary_file(self, fn: str) -> dict:
        """
        load a glossary file as metadata
        """
        files = {"file": fn}

        _, resp = self._http_client.post_multipart(
            f"api/metadata/glossary", None, None, files, None
        )
        resp = json.loads(resp)
        return resp

    def create_ingest_pipeline(self, pipeline: dict):
        """
        load an ingest pipeline as metadata (as new)
        """
        self._http_client.post(f"api/metadata/ingestpipeline", None, None, pipeline)

    def update_ingest_pipeline(self, pipeline: dict, pipeline_id: str):
        """
        update an ingest pipeline as metadata
        """
        self._http_client.put(
            f"api/metadata/ingestpipeline/{pipeline_id}", None, None, pipeline
        )

    def get_ingest_pipeline(self, pipeline_id: str) -> dict:
        """
        get an ingest pipeline
        """
        _, resp = self._http_client.get(
            f"api/metadata/ingestpipeline/{pipeline_id}", None, None, None
        )
        resp = json.loads(resp)
        return resp

    def list_ingest_pipeline(self) -> dict:
        """
        list ingest pipelines
        """
        _, resp = self._http_client.get(
            f"api/metadata/ingestpipeline", None, None, None
        )
        resp = json.loads(resp)
        return resp

    def list_jobs(self) -> dict:
        _, resp = self._http_client.get(f"api/jobs", None, None, None)
        resp = json.loads(resp)
        return resp

    def cancel_job(self, job_id: str) -> dict:
        _, resp = self._http_client.delete(f"api/jobs/{job_id}", None, None, None)
        resp = json.loads(resp)
        return resp

    def delete_ingest_pipeline(self, pipeline_id: str):
        """
        deletes an ingest pipeline
        """
        self._http_client.delete(
            f"api/metadata/ingestpipeline/{pipeline_id}", None, None, None
        )

    def wait(
        self, job_id: str, poll_secs: int = 3, timeout_mins: int = 121
    ) -> (JobStatus, dict):
        """
        will constantly poll for the job id to enter a completed or canceled state OR timeout

        :return: the status of the job, and error results (if status is error)
        :raises RuntimeError: on missing the job id (ie 404)
        """
        first = True
        end_time = datetime.datetime.now() + datetime.timedelta(minutes=timeout_mins)
        while end_time > datetime.datetime.now():
            err, resp = self._http_client.get(f"api/jobs/{job_id}", None, None, None)
            if err >= 400 and first:
                # if we get an error, sleep and try again.  normally it is a 404 and we checked to fast.
                # if still after the first time, then error out.
                first = False
                time.sleep(poll_secs)
                continue

            resp = json.loads(resp)
            if resp["status"] == JobStatus.COMPLETED_SUCCESS.value:
                return JobStatus.COMPLETED_SUCCESS, None
            elif resp["status"] == JobStatus.COMPLETED_ERROR.value:
                return JobStatus.COMPLETED_ERROR, resp
            elif resp["status"] == JobStatus.CANCELLED.value:
                return JobStatus.CANCELLED, None

            time.sleep(poll_secs)

        return JobStatus.TIMEOUT, None
