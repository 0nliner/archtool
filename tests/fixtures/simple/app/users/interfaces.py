from abc import abstractmethod
from archtool.layers.default_layer_interfaces import ABCService, ABCRepo


class UserServiceABC(ABCService):
    @abstractmethod
    def get_name(self) -> str: ...


class UserRepoABC(ABCRepo):
    @abstractmethod
    def find_all(self) -> list[str]: ...
