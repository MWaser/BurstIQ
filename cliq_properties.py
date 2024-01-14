import json
import os

import yaml

from graphchain_client.http_client import HttpClient


class CliqProperties(object):
    @staticmethod
    def _get_token(base_url: str, client_id: str, realm: str, un: str, pw: str) -> str:
        """
        get a JWT from keycloak
        """
        body = {
            "client_id": client_id,
            "grant_type": "password",
            "username": un,
            "password": pw,
        }

        keycloak_client = HttpClient(base_url, None, None, raise_error=True)
        code, resp = keycloak_client.post_urlencoded(
            f"realms/{realm}/protocol/openid-connect/token", None, None, body
        )
        resp = json.loads(resp)
        return resp["access_token"]

    def __init__(self, props_file: str):
        if os.path.isdir(props_file):
            raise ValueError(
                f"Error: properties file path {props_file} is a directory, must be a file path"
            )

        # load from file, check required, add defaults
        with open(props_file, "rt") as f:
            props = yaml.safe_load(f)

        # depending on the necessary action may not need all the configuration sections!
        self._biq_admin = props.get("biq_admin")
        self._sdz_admin = props.get("sdz_admin")
        self._graphchain = props.get("graphchain")

    def get_client(self, token: str) -> HttpClient:
        return HttpClient(
            self._graphchain["server"],
            self._graphchain["customer"],
            self._graphchain["sdz"],
            token,
            raise_error=True,
        )

    def get_biq_admin_token(self) -> str:
        return CliqProperties._get_token(
            self._biq_admin["server"],
            self._biq_admin["client_id"],
            self._biq_admin["realm"],
            self._biq_admin["username"],
            self._biq_admin["password"],
        )

    def get_sdz_admin_token(self) -> str:
        return CliqProperties._get_token(
            self._sdz_admin["server"],
            self._sdz_admin["client_id"],
            self._sdz_admin["realm"],
            self._sdz_admin["username"],
            self._sdz_admin["password"],
        )

    def get_graphchain(self) -> str:
        return self._graphchain["server"]

    def get_graphchain_customer(self) -> (str, str):
        return (
            self._graphchain["customer"],
            self._graphchain["sdz"],
        )
