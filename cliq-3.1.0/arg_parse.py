import argparse
import typing
from argparse import Namespace
from typing import Type, List, Callable, Any, Optional

from cliq_action_base import CliqActionBase


class ArgParse:
    def __init__(self, app_name: str, desc: str, epilog: str):
        # create the top-level parser
        self._parser = argparse.ArgumentParser(
            prog=app_name, description=desc, epilog=epilog
        )

        # add the top-level arguments
        self._parser.add_argument(
            "-p",
            "--props",
            dest="props_file",
            help=f"filename of properties file; default: {app_name}.yml",
            required=False,
            default=f"{app_name}.yml",
        )

        self._parser.add_argument(
            "-u", "--username", dest="username", help="username", required=False
        )
        self._parser.add_argument(
            "-w", "--password", dest="password", help="password", required=False
        )
        self._parser.add_argument(
            "-c",
            "--customer",
            dest="customer",
            help="customer short name",
            required=False,
        )
        self._parser.add_argument(
            "-s",
            "--sdz",
            dest="sdz",
            help="name of the Secure Data Zone (sdz)",
            required=False,
        )

        # create the sub-parser
        self._subparsers = self._parser.add_subparsers(
            dest="action",
            help="type '<cmd> --help' for help on specific command",
        )

        self._actions = {}
        self._parsers = {}

    def parse_args(self) -> (CliqActionBase, Namespace):
        opts = self._parser.parse_args()

        if opts.action is None:
            print("--help or <action> is required\n")
            self._parser.print_help()
            exit(-1)

        if opts.action not in self._actions:
            raise RuntimeError(f"the action {opts.action} is not supported")

        # cleanup all the "Any" types so that None checks work as expected
        # repackage the scrubbed options back into a Namespace
        args_dict = vars(opts)
        for k, v in args_dict.items():
            if type(v) == typing._AnyMeta:
                args_dict[k] = None
        opts = Namespace(**args_dict)

        return self._actions[opts.action], opts

    def add_cliq_action(self, action: CliqActionBase, help_text: str):
        p = self._subparsers.add_parser(action.name, help=help_text)

        self._actions[action.name] = action
        self._parsers[action.name] = p

    def add_arg(
        self,
        action: CliqActionBase,
        long_name: str,
        short_name: Optional[str],
        dest: str,
        desc: str,
        arg_type: Callable[[str], Any] | argparse.FileType | Type = str,
        req: bool = True,
        default=Any,
    ):
        """
        the standard argument adder - use this function do not add directly!
        """
        p = self._parsers[action.name]
        if p is None:
            raise RuntimeError(f"unknown action: {action.name} to add argument")

        if short_name is None:
            p.add_argument(
                long_name,
                dest=dest,
                help=desc,
                type=arg_type,
                required=req,
                default=default,
            )
        else:
            p.add_argument(
                long_name,
                short_name,
                dest=dest,
                help=desc,
                type=arg_type,
                required=req,
                default=default,
            )

    def add_enum_arg(
        self,
        action: CliqActionBase,
        long_name: str,
        short_name: str,
        dest: str,
        desc: str,
        choices: List[str],
        req: bool = True,
        default=None,
    ):
        """
        the standard argument adder - use this function do not add directly!
        """
        p = self._parsers[action.name]
        if p is None:
            raise RuntimeError(f"unknown action: {action.name} to add argument")

        p.add_argument(
            long_name,
            short_name,
            dest=dest,
            help=desc,
            type=str,
            choices=choices,
            required=req,
            default=default,
        )

    def add_flag_arg(
        self,
        action: CliqActionBase,
        long_name: str,
        dest: str,
        desc: str,
        default: bool = False,
    ):
        p = self._parsers[action.name]
        if p is None:
            raise RuntimeError(f"unknown action: {action.name} to add argument")

        p.add_argument(
            long_name,
            dest=dest,
            help=desc,
            action=argparse.BooleanOptionalAction,
            type=bool,
            default=default,
        )

    def add_list_arg(
        self,
        action: CliqActionBase,
        long_name: str,
        short_name: str,
        dest: str,
        desc: str,
        nargs: str = "+",
    ):
        p = self._parsers[action.name]
        if p is None:
            raise RuntimeError(f"unknown action: {action.name} to add argument")

        p.add_argument(
            long_name, short_name, dest=dest, help=desc, nargs=nargs, type=str
        )

    def add_name_arg(
        self,
        action: CliqActionBase,
        desc: str = "the short name of the customer",
        req: bool = True,
    ):
        self.add_arg(action, "--name", "-n", "name", desc, str, req)

    def add_id_arg(
        self,
        action: CliqActionBase,
        desc: str = "the id of the SDZ",
        req: bool = True,
    ):
        self.add_arg(action, "--id", "-i", "id", desc, str, req)

    def add_system_wallet_id_arg(
        self,
        action: CliqActionBase,
        desc: str = "the id of the SDZ",
        req: bool = False,
    ):
        self.add_arg(
            action, "--system_wallet_id", "-sw", "system_wallet_id", desc, str, req
        )

    def add_sdz_arg(
        self, action: CliqActionBase, desc: str = "the short name of the sdz"
    ):
        self.add_arg(action, "--sdz", "-s", "sdz", desc, str, True)

    def add_chain_arg(
        self, action: CliqActionBase, desc: str = "the chain name for the data"
    ):
        self.add_arg(action, "--chain", "-c", "chain", desc, str, True)

    def add_threads_arg(
        self,
        action: CliqActionBase,
        desc: str = "the number of threads",
        req: bool = False,
    ):
        self.add_arg(action, "--threads", "-n", "threads", desc, int, req, 1)

    def add_file_arg(
        self,
        action: CliqActionBase,
        desc: str = "the file path for the input",
        req: bool = True,
    ):
        self.add_arg(action, "--file", "-f", "file", desc, str, req)

    def add_output_arg(
        self,
        action: CliqActionBase,
        desc: str = "the output path; optional, default is stdout",
        req: bool = False,
    ):
        self.add_arg(action, "--output", "-o", "output", desc, str, req)

    def add_email_arg(
        self,
        action: CliqActionBase,
        desc: str = "the email to send the results of the job to",
        req: bool = True,
    ):
        self.add_arg(action, "--email", "-e", "email", desc, str, req)

    def add_description_arg(
        self,
        action: CliqActionBase,
        desc: str = "the description",
        req: bool = True,
    ):
        self.add_arg(action, "--description", "-d", "description", desc, str, req)

    def add_sheet_arg(
        self,
        action: CliqActionBase,
        desc: str = "the sheet name or number (applies to Excel files only; 0-based number)",
        req: bool = False,
    ):
        self.add_arg(action, "--sheet", "-s", "sheet", desc, str, req)

    def add_wait_arg(
        self,
        action: CliqActionBase,
        desc: str = "should the tool wait (and poll) for the results of the async job; default --no-wait",
    ):
        self.add_flag_arg(
            action,
            "--wait",
            "wait",
            desc,
        )
