from __future__ import annotations

from .interfaces import BillingRepoABC


class BillingRepo(BillingRepoABC):
    def get_balance(self) -> float:
        return 100.0
