from .interfaces import FraudRepoABC


class FraudRepo(FraudRepoABC):
    def find_suspicious(self) -> list[str]:
        return ["tx_001"]
