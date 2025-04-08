import argparse

from arg_parse import ArgParse
from cliq_action_base import CliqActionBase
from cliq_properties import CliqProperties
from graphchain_client.graphchain_client import GraphChainClient
from util import Util


class MessageCreate(CliqActionBase):
    def __init__(self, ap: ArgParse):
        super().__init__("message_create")

        ap.add_cliq_action(self, "create message for the message center")

        ap.add_file_arg(self)

        ap.add_arg(
            self,
            "--date",
            "-d",
            "date",
            "date of the message",
        )

        ap.add_arg(
            self,
            "--title",
            "-t",
            "title",
            "title for the message",
        )

        ap.add_arg(
            self,
            "--message_type",
            "-m",
            "message_type",
            "the type of message (GENERAL, ALERT, RELEASE_NOTES)",
        )

    def run(
        self, props: CliqProperties, opts: argparse.Namespace, gc: GraphChainClient
    ):
        gc.create_message(opts.file, opts.title, opts.message_type, opts.date)


class MessageDelete(CliqActionBase):
    def __init__(self, ap: ArgParse):
        super().__init__("message_delete")

        ap.add_cliq_action(self, "delete message for the message center")

        ap.add_id_arg(self, "message id", True)

    def run(
        self, props: CliqProperties, opts: argparse.Namespace, gc: GraphChainClient
    ):
        gc.delete_message(opts.id)


class MessageList(CliqActionBase):
    def __init__(self, ap: ArgParse):
        super().__init__("message_list")

        ap.add_cliq_action(self, "list messages in the message center")

        ap.add_arg(
            self,
            "--days",
            "-d",
            "days",
            "days of messages to return (15, 30, 60, 90, 180, ALL)",
            str,
            False,
            "ALL",
        )

    def run(
        self, props: CliqProperties, opts: argparse.Namespace, gc: GraphChainClient
    ):
        Util.pretty_print_json(gc.list_messages(opts.days))
