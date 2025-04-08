import argparse
import datetime

from arg_parse import ArgParse
from cliq_action_base import CliqActionBase
from cliq_properties import CliqProperties
from graphchain_client.graphchain_client import GraphChainClient
from util import Util


class ConsentContractList(CliqActionBase):
    def __init__(self, ap: ArgParse):
        super().__init__("consent_contract_list")

        ap.add_cliq_action(self, "list the consent contracts for the chain")

        ap.add_system_wallet_id_arg(self)
        ap.add_chain_arg(self)

    def run(
        self, props: CliqProperties, opts: argparse.Namespace, gc: GraphChainClient
    ):
        Util.pretty_print_json(
            gc.list_consent_contracts(opts.chain, opts.system_wallet_id)
        )


class ConsentContractCreate(CliqActionBase):
    def __init__(self, ap: ArgParse):
        super().__init__("consent_contract_create")

        ap.add_cliq_action(self, "create a consent contract")

        ap.add_chain_arg(self)
        ap.add_system_wallet_id_arg(self)
        ap.add_list_arg(
            self,
            "--to",
            "-t",
            "to",
            "list of user wallet ids, a user group id, * from everyone",
        )
        ap.add_arg(
            self,
            "--when",
            "-w",
            "when",
            "when should a SDO be shared",
            req=False,
        )
        ap.add_list_arg(
            self,
            "--only",
            "-o",
            "only",
            "only consent these attribute",
        )
        ap.add_arg(
            self,
            "--start",
            "-s",
            "start",
            "start date of contract (YYYY-MM-DD hh:mm:ss)",
            lambda s: str(
                datetime.datetime.strptime(s, CliqActionBase.ARGUMENT_DATE_FORMAT)
            ),
            req=False,
        )
        ap.add_arg(
            self,
            "--until",
            "-u",
            "until",
            "end date of contract (YYYY-MM-DD hh:mm:ss)",
            lambda s: str(
                datetime.datetime.strptime(s, CliqActionBase.ARGUMENT_DATE_FORMAT)
            ),
            req=False,
        )
        ap.add_description_arg(self, "description of consent contract", False)

    def run(
        self, props: CliqProperties, opts: argparse.Namespace, gc: GraphChainClient
    ):
        contract = {"to": opts.to}

        if opts.when:
            contract["when"] = opts.when
        if opts.only:
            contract["only"] = opts.only
        if opts.start:
            contract["start"] = opts.start
        if opts.until:
            contract["until"] = opts.until
        if opts.description:
            contract["description"] = opts.description

        resp = gc.create_consent_contract(
            opts.chain, contract, None, opts.system_wallet_id
        )
        Util.pretty_print_json(resp)


class ConsentContractDelete(CliqActionBase):
    def __init__(self, ap: ArgParse):
        super().__init__("consent_contract_delete")

        ap.add_cliq_action(self, "delete consent contract by id")

        ap.add_chain_arg(self)
        ap.add_system_wallet_id_arg(self)
        ap.add_arg(self, "--id", "-i", "id", "sdo id")

    def run(
        self, props: CliqProperties, opts: argparse.Namespace, gc: GraphChainClient
    ):
        gc.delete_sdo(opts.chain, opts.id, opts.system_wallet_id)
