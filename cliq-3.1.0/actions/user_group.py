import argparse

from arg_parse import ArgParse
from cliq_action_base import CliqActionBase
from cliq_properties import CliqProperties
from graphchain_client.graphchain_client import GraphChainClient
from util import Util


def _add_group_arg(
    action: CliqActionBase,
    ap: ArgParse,
    desc: str = "list of user wallet ids for the group",
):
    ap.add_list_arg(
        action,
        "--group",
        "-g",
        "group",
        desc,
    )


class UserGroupList(CliqActionBase):
    def __init__(self, ap: ArgParse):
        super().__init__("user_group_list")

        ap.add_cliq_action(self, "list the user groups")

        ap.add_name_arg(self, "by user group name", False)
        ap.add_description_arg(self, "by user group description", False)

    def run(
        self, props: CliqProperties, opts: argparse.Namespace, gc: GraphChainClient
    ):
        Util.pretty_print_json(gc.list_user_groups(opts.name, opts.description))


class UserGroupGet(CliqActionBase):
    def __init__(self, ap: ArgParse):
        super().__init__("user_group_get")

        ap.add_cliq_action(self, "get user group by id")

        ap.add_id_arg(self, "user group id")

    def run(
        self, props: CliqProperties, opts: argparse.Namespace, gc: GraphChainClient
    ):
        Util.pretty_print_json(gc.get_user_group(opts.id))


class UserGroupCreate(CliqActionBase):
    def __init__(self, ap: ArgParse):
        super().__init__("user_group_create")

        ap.add_cliq_action(self, "create user group")

        ap.add_name_arg(self, "name for user group")
        ap.add_description_arg(self, "description for user group", False)
        _add_group_arg(self, ap)

    def run(
        self, props: CliqProperties, opts: argparse.Namespace, gc: GraphChainClient
    ):
        Util.pretty_print_json(
            gc.create_user_group(opts.name, opts.group, opts.description)
        )


class UserGroupUpdate(CliqActionBase):
    def __init__(self, ap: ArgParse):
        super().__init__("user_group_update")

        ap.add_cliq_action(self, "update user group")

        ap.add_id_arg(self, "id of existing user group")
        ap.add_name_arg(self, "name for user group")
        ap.add_description_arg(self, "description for user group", False)
        _add_group_arg(self, ap)

    def run(
        self, props: CliqProperties, opts: argparse.Namespace, gc: GraphChainClient
    ):
        Util.pretty_print_json(
            gc.update_user_group(opts.id, opts.name, opts.group, opts.description)
        )


class UserGroupDelete(CliqActionBase):
    def __init__(self, ap: ArgParse):
        super().__init__("user_group_delete")

        ap.add_cliq_action(self, "delete user group by id")

        ap.add_id_arg(self, "user group id", True)

    def run(
        self, props: CliqProperties, opts: argparse.Namespace, gc: GraphChainClient
    ):
        gc.delete_user_group(opts.id)
