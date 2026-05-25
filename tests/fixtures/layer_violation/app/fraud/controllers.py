from .interfaces import FraudControllerABC


class FraudController(FraudControllerABC):
    def handle(self) -> str:
        return "fraud_handled"
