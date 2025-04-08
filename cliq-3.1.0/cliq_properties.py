import os
from argparse import Namespace

import yaml

from util import Util


class CliqProperties(object):
    # standard PROD keycloak and client
    _KEYCLOAK_DEFAULT_SERVER = "https://auth.burstiq.com"
    _KEYCLOAK_DEFAULT_CLIENT_ID = "burst"

    # standard PROD graphchain server
    _GRAPHCHAIN_DEFAULT_SERVER = "https://api.burstiq.com"

    # private places for a username and pw to exist
    _CLIQ_USERNAME_ENV_VAR = "CLIQ_USERNAME"
    _CLIQ_PASSWORD_ENV_VAR = "CLIQ_PASSWORD"
    _CLIQ_CREDS_FILE = ".cliq.yml"

    _BIQ_MASTER = "biq_master"
    _MASTER_SDZ = "master_sdz"

    def __init__(self, opts: Namespace, sudo: bool) -> None:
        """
        set defaults

        if a props file is present, read that

        if there is a CREDS env var use that for user:pw or pw
        if there is a CREDS file use that for user:pw or pw
        """

        # defaults
        self._keycloak_server = CliqProperties._KEYCLOAK_DEFAULT_SERVER
        self._keycloak_client_id = CliqProperties._KEYCLOAK_DEFAULT_CLIENT_ID

        self._graphchain_server = CliqProperties._GRAPHCHAIN_DEFAULT_SERVER

        self._username = None
        self._password = None
        self._customer = None
        self._sdz = None

        # set and/or override based on props file
        props_file = Util.standardize_file(opts.props_file)
        if props_file and os.path.exists(props_file) and os.path.isfile(props_file):
            with open(props_file, "rt") as f:
                props = yaml.safe_load(f)

                self._keycloak_server = props.get(
                    "keycloak_server", self._keycloak_server
                )
                self._graphchain_server = props.get(
                    "graphchain_server", self._graphchain_server
                )

                self._username = props.get("username", self._username)
                self._password = props.get("password", self._password)
                self._customer = props.get("customer", self._customer)
                self._sdz = props.get("sdz", self._sdz)

        # for sudo need to hard-code the customer/sdz; also never accept
        # username/pw in the standard props file only from one of the
        # secret places
        if sudo:
            self._username = None
            self._password = None
            self._customer = CliqProperties._BIQ_MASTER
            self._sdz = CliqProperties._MASTER_SDZ

        # 1. process env variable for creds
        un = os.environ.get(CliqProperties._CLIQ_USERNAME_ENV_VAR)
        if un:
            self._username = un

        pw = os.environ.get(CliqProperties._CLIQ_PASSWORD_ENV_VAR)
        if un:
            self._password = pw

        # 2. process the secrets file for creds
        if os.path.exists(CliqProperties._CLIQ_CREDS_FILE) and os.path.isfile(
            CliqProperties._CLIQ_CREDS_FILE
        ):
            with open(CliqProperties._CLIQ_CREDS_FILE, "rt") as f:
                creds = yaml.safe_load(f)
                self._username = creds.get("username", self._username)
                self._password = creds.get("password", self._password)

        # 3. if the cmd line had creds they take precedence
        if opts.username:
            self._username = opts.username

        if opts.password:
            self._password = opts.password

        if opts.customer:
            self._customer = opts.customer

        if opts.sdz:
            self._sdz = opts.sdz

        # validate required properties
        if not self._keycloak_server:
            raise ValueError("No keycloak server defined")

        if not self._keycloak_client_id:
            raise ValueError("No keycloak client id defined")

        if not self._graphchain_server:
            raise ValueError("No graphchain server defined")

        if not self._username:
            raise ValueError("No username defined")

        if not self._password:
            raise ValueError("No password defined")

        if not self._customer:
            raise ValueError("No customer defined")

        if not self._sdz:
            raise ValueError("No sdz defined")

    def get_keycloak_server(self) -> str:
        return self._keycloak_server

    def get_keycloak_client_id(self) -> str:
        return self._keycloak_client_id

    def get_graphchain_server(self) -> str:
        return self._graphchain_server

    def get_username(self) -> str:
        return self._username

    def get_password(self) -> str:
        return self._password

    def get_customer_sdz(self) -> (str, str):
        return self._customer, self._sdz
