from __future__ import annotations

from .interfaces import BillingServiceABC, BillingRepoABC


class BillingService(BillingServiceABC):
    # This annotation is a string at runtime due to __future__.
    # DI must still resolve and inject it correctly.
    repo: BillingRepoABC

    def total(self) -> float:
        return self.repo.get_balance()
