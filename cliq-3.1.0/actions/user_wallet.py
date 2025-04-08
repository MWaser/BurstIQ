import argparse

from arg_parse import ArgParse
from cliq_action_base import CliqActionBase
from cliq_properties import CliqProperties
from graphchain_client.graphchain_client import GraphChainClient
from util import Util


class UserWalletList(CliqActionBase):
    def __init__(self, ap: ArgParse):
        super().__init__("user_wallet_list")

        ap.add_cliq_action(self, "list the dictionaries in the system")

        ap.add_email_arg(self, "email to search for", False)
        ap.add_name_arg(self, "full name to search for", False)

    def run(
        self, props: CliqProperties, opts: argparse.Namespace, gc: GraphChainClient
    ):
        Util.pretty_print_json(gc.list_user_wallets(opts.email, opts.name))


class UserWalletGet(CliqActionBase):
    def __init__(self, ap: ArgParse):
        super().__init__("user_wallet_get")

        ap.add_cliq_action(self, "get user wallet by id")

        ap.add_id_arg(self, "user wallet id")

    def run(
        self, props: CliqProperties, opts: argparse.Namespace, gc: GraphChainClient
    ):
        Util.pretty_print_json(gc.get_user_wallet(opts.id))


class UserWalletCreate(CliqActionBase):
    def __init__(self, ap: ArgParse):
        super().__init__("user_wallet_create")

        ap.add_cliq_action(self, "create user wallet")
        ap.add_email_arg(self, "email for wallet")
        ap.add_name_arg(self, "full name for wallet")

    def run(
        self, props: CliqProperties, opts: argparse.Namespace, gc: GraphChainClient
    ):
        Util.pretty_print_json(gc.create_user_wallet(opts.email, opts.name))


class UserWalletDelete(CliqActionBase):
    def __init__(self, ap: ArgParse):
        super().__init__("user_wallet_delete")

        ap.add_cliq_action(self, "delete user wallet by id")

        ap.add_arg(
            self,
            "--id",
            "-i",
            "id",
            "user wallet id",
            str,
            True,
        )

    def run(
        self, props: CliqProperties, opts: argparse.Namespace, gc: GraphChainClient
    ):
        gc.delete_user_wallet(opts.id)
