import json

import requests
from cachetools import TTLCache


class JwtCache(object):
    """
    cache is tied to a specific keycloak server
    and entries for tokens are keyed on client id, realm, username, and pw
    """

    _GRANT_TYPE = "password"

    def __init__(self, keycloak_server: str, ttl_secs: int = 10 * 60):
        """
        defaults are:
            max size 10 (can have a couple user, admin, etc.)
            ttl 10 mins (as seconds)
        """
        self._cache = TTLCache(maxsize=10, ttl=ttl_secs)

        self._keycloak_server = keycloak_server

    def get_jwt(self, keycloak_client_id: str, realm: str, un: str, pw: str) -> str:
        """
        a time-based cache for ensuring a jwt is not expired for client operations
        should only fire when missing from cache or expired

        get a JWT from keycloak

        :return: access token (refresh is not returned)
        :raises RuntimeError: if any REST error occurred
        """
        key = f"{keycloak_client_id}/{realm}/{un}/{pw}"

        if key in self._cache:
            return self._cache[key]
        else:
            data = self._request_jwt(keycloak_client_id, realm, un, pw)
            if data:
                # only cache non-null values
                self._cache[key] = data
        return data

    def _request_jwt(self, keycloak_client_id: str, realm: str, un: str, pw: str):
        body = {
            "client_id": keycloak_client_id,
            "grant_type": JwtCache._GRANT_TYPE,
            "username": un,
            "password": pw,
        }

        resp = requests.post(
            f"{self._keycloak_server}/realms/{realm}/protocol/openid-connect/token",
            data=body,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        if resp.status_code != 200:
            raise RuntimeError(
                f"failed to get jwt for {un} at {realm}: {json.dumps(resp.json())}"
            )

        return resp.json()["access_token"]
