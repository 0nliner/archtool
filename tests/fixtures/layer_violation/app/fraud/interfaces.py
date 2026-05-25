from abc import abstractmethod
from archtool.layers.default_layer_interfaces import ABCRepo, ABCService, ABCController


class FraudRepoABC(ABCRepo):
    @abstractmethod
    def find_suspicious(self) -> list[str]: ...


class FraudServiceABC(ABCService):
    @abstractmethod
    def check(self) -> bool: ...


class FraudControllerABC(ABCController):
    @abstractmethod
    def handle(self) -> str: ...
