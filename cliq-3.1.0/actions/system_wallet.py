import argparse

from arg_parse import ArgParse
from cliq_action_base import CliqActionBase
from cliq_properties import CliqProperties
from graphchain_client.graphchain_client import GraphChainClient
from util import Util


def _add_type_arg(action: CliqActionBase, ap: ArgParse, req: bool):
    ap.add_enum_arg(
        action,
        "--type",
        "-t",
        "type",
        "type of system wallet",
        [
            "CUSTODIAN_OWNER",
            "CUSTODIAN_LIMITED_OWNER",
            "TENANT_OWNER",
            "TENANT_LIMITED_OWNER",
        ],
        req,
        default=None,
    )


class SystemWalletList(CliqActionBase):
    def __init__(self, ap: ArgParse):
        super().__init__("system_wallet_list")

        ap.add_cliq_action(self, "list the system wallets")

        ap.add_description_arg(self, "by system wallet description", False)

        _add_type_arg(self, ap, False)

    def run(
        self, props: CliqProperties, opts: argparse.Namespace, gc: GraphChainClient
    ):
        Util.pretty_print_json(gc.list_system_wallets(opts.description, opts.type))


class SystemWalletGet(CliqActionBase):
    def __init__(self, ap: ArgParse):
        super().__init__("system_wallet_get")

        ap.add_cliq_action(self, "get system wallet by id")

        ap.add_id_arg(self, "system wallet id")

    def run(
        self, props: CliqProperties, opts: argparse.Namespace, gc: GraphChainClient
    ):
        Util.pretty_print_json(gc.get_system_wallet(opts.id))


class SystemWalletCreate(CliqActionBase):
    def __init__(self, ap: ArgParse):
        super().__init__("system_wallet_create")

        ap.add_cliq_action(self, "create system wallet")

        ap.add_description_arg(self, "full name for wallet")

        _add_type_arg(self, ap, True)

        ap.add_arg(
            self,
            "--acug",
            "-a",
            "acug",
            "access control user group id",
            str,
            True,
        )

        ap.add_arg(self, "--write", "-w", "write", "write user group id", str, False)

    def run(
        self, props: CliqProperties, opts: argparse.Namespace, gc: GraphChainClient
    ):
        Util.pretty_print_json(
            gc.create_system_wallet(opts.description, opts.type, opts.acug, opts.write)
        )


class SystemWalletDelete(CliqActionBase):
    def __init__(self, ap: ArgParse):
        super().__init__("system_wallet_delete")

        ap.add_cliq_action(self, "delete system wallet by id")

        ap.add_id_arg(self, "system wallet id", True)

    def run(
        self, props: CliqProperties, opts: argparse.Namespace, gc: GraphChainClient
    ):
        gc.delete_system_wallet(opts.id)
