#!/usr/bin/env python3
from actions.consent_contract import (
    ConsentContractList,
    ConsentContractCreate,
    ConsentContractDelete,
)
from actions.data import (
    DataQuery,
    DataDelete,
    DataBlobCreate,
    DataVerificationAdd,
    DataLoad,
    DataExport,
    DataDownload,
)
from actions.dbschema import ImportDbSchema, ExportDbSchema
from actions.dict import DictPredict, DictList, DictGet, DictUpsert, DictDelete
from actions.edge import EdgeGet, EdgeUpdate, EdgeCreate, EdgeDelete
from actions.glossary import GlossaryCreate
from actions.graphchain import (
    GraphChainHealth,
    GraphChainVersion,
    GraphChainTruncate,
    GraphChainDrop,
    GraphChainWipe,
    GraphChainReset,
)
from actions.ingest_pipeline import (
    IngestPipelineList,
    IngestPipelineGet,
    IngestPipelineCreate,
    IngestPipelineUpdate,
    IngestPipelineDelete,
)
from actions.job import JobList, JobCancel
from actions.metadata import MetadataExport
from actions.smart_contract import (
    SmartContractList,
    SmartContractCreate,
    SmartContractDelete,
    SmartContractExecute,
)
from actions.system_wallet import (
    SystemWalletList,
    SystemWalletCreate,
    SystemWalletGet,
    SystemWalletDelete,
)
from actions.user_group import (
    UserGroupList,
    UserGroupGet,
    UserGroupCreate,
    UserGroupUpdate,
    UserGroupDelete,
)
from actions.user_wallet import (
    UserWalletList,
    UserWalletGet,
    UserWalletCreate,
    UserWalletDelete,
)
from arg_parse import ArgParse
from cliq_properties import CliqProperties
from consts import APP_NAME, DESC, COPYRIGHT, VERSION
from graphchain_client.graphchain_client import GraphChainClient
from graphchain_client.http_client import HttpClient
from graphchain_client.jwt_cache import JwtCache

"""
cliq - command line tool for performing many admin-related functions (both biq- and sdz-admin)
    
NOTE: does not use logging, since this is a cmd line (-ish) tool; so just stdout and minimal so scripts
can process the output cleanly
"""


def main():
    try:
        arg_parse = ArgParse(APP_NAME, DESC, f"v{VERSION}\n{COPYRIGHT}")

        # dictionary
        DictList(arg_parse)
        DictGet(arg_parse)
        DictUpsert(arg_parse)
        DictDelete(arg_parse)
        DictPredict(arg_parse)

        # dbschema
        ImportDbSchema(arg_parse)
        ExportDbSchema(arg_parse)

        # general metadata
        MetadataExport(arg_parse)

        # glossary
        GlossaryCreate(arg_parse)

        # ingest pipelines
        IngestPipelineList(arg_parse)
        IngestPipelineGet(arg_parse)
        IngestPipelineCreate(arg_parse)
        IngestPipelineUpdate(arg_parse)
        IngestPipelineDelete(arg_parse)

        # sys wallets
        SystemWalletList(arg_parse)
        SystemWalletGet(arg_parse)
        SystemWalletCreate(arg_parse)
        SystemWalletDelete(arg_parse)

        # user wallets
        UserWalletList(arg_parse)
        UserWalletGet(arg_parse)
        UserWalletCreate(arg_parse)
        UserWalletDelete(arg_parse)

        # user groups
        UserGroupList(arg_parse)
        UserGroupGet(arg_parse)
        UserGroupCreate(arg_parse)
        UserGroupUpdate(arg_parse)
        UserGroupDelete(arg_parse)

        # consent contract
        ConsentContractList(arg_parse)
        ConsentContractCreate(arg_parse)
        ConsentContractDelete(arg_parse)

        # smart contract
        SmartContractList(arg_parse)
        SmartContractCreate(arg_parse)
        SmartContractDelete(arg_parse)
        SmartContractExecute(arg_parse)

        # sdo/asset
        DataQuery(arg_parse)
        DataDelete(arg_parse)
        DataBlobCreate(arg_parse)
        DataVerificationAdd(arg_parse)
        DataLoad(arg_parse)
        DataExport(arg_parse)
        DataDownload(arg_parse)

        # edges
        EdgeGet(arg_parse)
        EdgeCreate(arg_parse)
        EdgeUpdate(arg_parse)
        EdgeDelete(arg_parse)

        # job manager
        JobList(arg_parse)
        JobCancel(arg_parse)

        # general graphchain
        GraphChainHealth(arg_parse)
        GraphChainVersion(arg_parse)
        GraphChainTruncate(arg_parse)
        GraphChainDrop(arg_parse)
        GraphChainWipe(arg_parse)
        GraphChainReset(arg_parse)

        # parse args, get props
        cliq_action, opts = arg_parse.parse_args()

        cliq_properties = CliqProperties(opts, False)

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
