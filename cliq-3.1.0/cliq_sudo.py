#!/usr/bin/env python3
from actions.graphchain import GraphChainHealth
from actions_sudo.caches import CachesClear
from actions_sudo.customer import (
    CustomerCreate,
    CustomerGet,
    CustomerDrop,
    CustomerUpdate,
    CustomerList,
)
from actions_sudo.message import MessageCreate, MessageDelete, MessageList
from actions_sudo.metrics import MetricsBilling
from actions_sudo.sdz import SDZDrop
from arg_parse import ArgParse
from cliq_properties import CliqProperties
from consts import COPYRIGHT, SUDO_APP_NAME, SUDO_DESC, VERSION
from graphchain_client.graphchain_client import GraphChainClient
from graphchain_client.http_client import HttpClient
from graphchain_client.jwt_cache import JwtCache

"""
cliq_sudo - the sudo'er version of cliq for biq_admin functions

NOTE: does not use logging, since this is a cmd line (-ish) tool; so just stdout and minimal so scripts
can process the output cleanly
"""


def main():
    try:
        # build actions and args
        arg_parse = ArgParse(SUDO_APP_NAME, SUDO_DESC, f"v{VERSION}\n{COPYRIGHT}")

        # customer commands
        CustomerCreate(arg_parse)
        CustomerGet(arg_parse)
        CustomerDrop(arg_parse)
        CustomerUpdate(arg_parse)
        CustomerList(arg_parse)

        # message commands
        MessageCreate(arg_parse)
        MessageList(arg_parse)
        MessageDelete(arg_parse)

        # sdz commands
        SDZDrop(arg_parse)

        # cache commands
        CachesClear(arg_parse)

        # misc
        GraphChainHealth(arg_parse)
        MetricsBilling(arg_parse)

        # parse args, get props, graphchain and run action
        cliq_action, opts = arg_parse.parse_args()

        # SUDO difference!!
        # for cliq_sudo the customer/sdz is hard-coded,
        # and creds should only be in env vars or file or cmd line args

        cliq_properties = CliqProperties(opts, True)

        # create jwt cache and http client and graph chain client
        jwt_cache = JwtCache(cliq_properties.get_keycloak_server())

        biq_std_hdrs = {
            "BIQ_CUSTOMER_NAME": cliq_properties.get_customer_sdz()[0],
            "BIQ_SDZ_NAME": cliq_properties.get_customer_sdz()[1],
        }

        http_client = HttpClient(
            cliq_properties.get_graphchain_server(),
            jwt_cache,
            cliq_properties.get_username(),
            cliq_properties.get_password(),
            biq_std_hdrs,
            cliq_properties.get_keycloak_client_id(),
            cliq_properties.get_customer_sdz()[
                0
            ],  # actually realm, but same as customer
        )

        gc = GraphChainClient(http_client)

        # execute the action
        cliq_action.run(cliq_properties, opts, gc)
    except SystemExit as err:
        # allow system exit of 0 (success) to pass cleanly; log everything else
        if err.code != 0:
            raise SystemExit(err)
    except BaseException as err:
        raise SystemExit(err)


if __name__ == "__main__":
    main()
