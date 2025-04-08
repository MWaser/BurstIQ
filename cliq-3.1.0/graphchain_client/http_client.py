import copy
import ntpath
import shutil
from enum import Enum
from typing import Optional, IO

import requests
from clint.textui.progress import Bar as ProgressBar
from requests import Response
from requests.adapters import HTTPAdapter
from requests_toolbelt import MultipartEncoder, MultipartEncoderMonitor

from graphchain_client.jwt_cache import JwtCache


class HttpClientConsts(Enum):
    """
    HTTP Client constants
    """

    AUTH_HEADER = "Authorization"

    CONTENT_TYPE_HEADER = "Content-Type"
    ACCEPT_HEADER = "Accept"

    JSON_CONTENT_TYPE = "application/json"
    XML_CONTENT_TYPE = "application/xml"
    OCTET_CONTENT_TYPE = "application/octet-stream"
    URLENCODED_CONTENT_TYPE = "application/x-www-form-urlencoded"


class HttpClient(object):
    """
    Hides details of connecting to a http endpoint
    """

    def __init__(
        self,
        base_url: str,
        jwt_cache: JwtCache,
        username: str,
        password: str,
        addl_hdrs: dict,
        keycloak_client_id: str,
        realm: str,
        raise_error: bool = True,
    ):
        # create session pool
        # 15 min timeout; for large upload/download requests
        self._adapter = HTTPAdapter(10, 10, 3, True)
        self._adapter.timeout = 15 * 60

        self._session = requests.sessions.Session()
        self._session.mount("https://", self._adapter)

        # update headers
        self._session.headers.update(addl_hdrs)
        self._session.headers.update(
            {
                HttpClientConsts.CONTENT_TYPE_HEADER.value: HttpClientConsts.JSON_CONTENT_TYPE.value,
            }
        )

        # keep args
        self._base_url = base_url
        self._jwt_cache = jwt_cache
        self._username = username
        self._password = password
        self._keycloak_client_id = keycloak_client_id
        self._realm = realm
        self._raise_error = raise_error

    def __del__(self):
        self._session.close()
        self._session = None

    def post(
        self,
        path: str,
        addl_headers: Optional[dict],
        query_params: Optional[dict],
        body: Optional[dict],
    ) -> (int, str):
        self._set_jwt()

        resp = self._session.post(
            self._create_path(path),
            headers=addl_headers,
            params=query_params,
            json=body,
        )
        return self._process_response(resp)

    def post_plain_text(
        self,
        path: str,
        addl_headers: Optional[dict],
        query_params: Optional[dict],
        body: str,
    ) -> (int, str):
        self._set_jwt()

        if addl_headers is None:
            addl_headers = {}
        addl_headers[HttpClientConsts.CONTENT_TYPE_HEADER.value] = "text/plain"

        resp = self._session.post(
            self._create_path(path),
            headers=addl_headers,
            params=query_params,
            data=body,
        )
        return self._process_response(resp)

    def post_urlencoded(
        self,
        path: str,
        addl_headers: Optional[dict],
        query_params: Optional[dict],
        body: Optional[dict],
    ) -> (int, str):
        self._set_jwt()

        # override any preset content (ie JSON)
        hdrs = HttpClient._merge_headers(
            addl_headers,
            {
                HttpClientConsts.CONTENT_TYPE_HEADER.value: HttpClientConsts.URLENCODED_CONTENT_TYPE.value
            },
        )

        resp = self._session.post(
            self._create_path(path), headers=hdrs, params=query_params, data=body
        )
        return self._process_response(resp)

    def put(
        self,
        path: str,
        addl_headers: Optional[dict],
        query_params: Optional[dict],
        body: Optional[dict],
    ) -> (int, str):
        self._set_jwt()

        resp = self._session.put(
            self._create_path(path),
            headers=addl_headers,
            params=query_params,
            json=body,
        )
        return self._process_response(resp)

    def put_multipart(
        self,
        path: str,
        addl_headers: Optional[dict],
        query_params: Optional[dict],
        files: Optional[dict],
        form: Optional[dict],
    ) -> (int, str):
        self._set_jwt()

        monitored, content_type = HttpClient._create_monitored_data(files, form)

        # override any preset content (ie JSON)
        hdrs = HttpClient._merge_headers(
            addl_headers,
            {
                "Prefer": "respond-async",
                HttpClientConsts.CONTENT_TYPE_HEADER.value: content_type,
            },
        )

        resp = self._session.put(
            self._create_path(path), headers=hdrs, params=query_params, data=monitored
        )
        return self._process_response(resp)

    def get(
        self,
        path: str,
        addl_headers: Optional[dict],
        query_params: Optional[dict],
        body: Optional[dict],
    ) -> (int, str):
        self._set_jwt()

        resp = self._session.get(
            self._create_path(path),
            headers=addl_headers,
            params=query_params,
            json=body,
        )
        return self._process_response(resp)

    def delete(
        self,
        path: str,
        addl_headers: Optional[dict],
        query_params: Optional[dict],
        body: Optional[dict],
    ) -> (int, str):
        self._set_jwt()

        resp = self._session.delete(
            self._create_path(path),
            headers=addl_headers,
            params=query_params,
            json=body,
        )
        return self._process_response(resp)

    def post_multipart(
        self,
        path: str,
        addl_headers: Optional[dict],
        query_params: Optional[dict],
        files: Optional[dict],
        form: Optional[dict],
    ) -> (int, str):
        self._set_jwt()

        monitored, content_type = HttpClient._create_monitored_data(files, form)

        hdrs = {
            "Prefer": "respond-async",
            HttpClientConsts.CONTENT_TYPE_HEADER.value: content_type,
        }

        resp = self._session.post(
            self._create_path(path),
            headers=HttpClient._merge_headers(addl_headers, hdrs),
            params=query_params,
            data=monitored,
        )
        return self._process_response(resp)

    def get_octet(
        self,
        path: str,
        addl_headers: Optional[dict],
        query_params: Optional[dict],
        f: IO,
    ):
        """
        save an octet stream Accept endpoint as a binary file

        no graceful error on non-200; will raise HTTPError
        """

        self._set_jwt()

        # set the accept header for octet stream
        if addl_headers is None:
            addl_headers = {}

        addl_headers[HttpClientConsts.ACCEPT_HEADER.value] = (
            HttpClientConsts.OCTET_CONTENT_TYPE.value
        )

        with self._session.get(
            self._create_path(path),
            headers=addl_headers,
            params=query_params,
            stream=True,
        ) as resp:
            resp.raise_for_status()
            shutil.copyfileobj(resp.raw, f)

    def _set_jwt(self):
        bearer_token = self._jwt_cache.get_jwt(
            self._keycloak_client_id, self._realm, self._username, self._password
        )
        self._session.headers.update(
            {HttpClientConsts.AUTH_HEADER.value: f"Bearer {bearer_token}"}
        )

    def _create_path(self, path: str) -> str:
        return f"{self._base_url}/{path}"

    def _process_response(self, response: Response) -> (int, str):
        if 200 <= response.status_code < 300:
            return response.status_code, response.text
        else:
            if self._raise_error:
                raise RuntimeError(
                    f"error {response.status_code}: resp: {response.text}"
                )
            else:
                return response.status_code, response.text

    @staticmethod
    def _merge_headers(hdr1: Optional[dict], hdr2: Optional[dict]) -> dict:
        if hdr1 is None and hdr2 is None:
            return {}
        elif hdr1 is not None and hdr2 is None:
            return copy.deepcopy(hdr1)
        elif hdr1 is None and hdr2 is not None:
            return copy.deepcopy(hdr2)
        else:
            hdr = copy.deepcopy(hdr1)
            hdr.update(hdr2)
            return hdr

    @staticmethod
    def _create_monitored_data(
        files: Optional[dict], form: Optional[dict]
    ) -> (MultipartEncoderMonitor, str):
        # create a mixed type multipart form; start with simple form data
        form_data = {}
        if form is not None:
            form_data = copy.deepcopy(form)

        # add binary files
        if files is not None:
            for k, v in files.items():
                if v is not None and v != "":
                    form_data[k] = (
                        ntpath.basename(v),
                        open(v, "rb"),
                        HttpClientConsts.OCTET_CONTENT_TYPE.value,
                    )

        # use this encoder for streaming large files in the form
        encoded = MultipartEncoder(form_data)

        # create progress bar for the monitor callback (uncomment if you want a chui progress bar)
        bar = ProgressBar(
            expected_size=encoded.len, label="Progress", filled_char="*", empty_char="."
        )
        return (
            MultipartEncoderMonitor(encoded, lambda m: bar.show(m.bytes_read)),
            encoded.content_type,
        )  # return MultipartEncoderMonitor(encoded), encoded.content_type
