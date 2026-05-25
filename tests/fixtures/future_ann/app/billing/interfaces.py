from __future__ import annotations

from abc import abstractmethod

from archtool.layers.default_layer_interfaces import ABCService, ABCRepo


class BillingRepoABC(ABCRepo):
    @abstractmethod
    def get_balance(self) -> float: ...


class BillingServiceABC(ABCService):
    @abstractmethod
    def total(self) -> float: ...
