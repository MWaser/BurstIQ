import argparse
from abc import ABC, abstractmethod

from cliq_properties import CliqProperties
from graphchain_client.graphchain_client import GraphChainClient


class CliqActionBase(ABC):
    ARGUMENT_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def run(
        self,
        props: CliqProperties,
        opts: argparse.Namespace,
        gc: GraphChainClient,
    ):
        raise NotImplementedError()
