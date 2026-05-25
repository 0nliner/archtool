from abc import abstractmethod
from archtool.layers.default_layer_interfaces import ABCRepo, ABCService


class GatewayRepoABC(ABCRepo):
    @abstractmethod
    def ping(self) -> bool: ...


class GatewayServiceABC(ABCService):
    @abstractmethod
    def check(self) -> bool: ...
