from .interfaces import FraudServiceABC, FraudControllerABC


class FraudService(FraudServiceABC):
    # VIOLATION: DomainLayer (service) depends on ApplicationLayer (controller)
    controller: FraudControllerABC

    def check(self) -> bool:
        return bool(self.controller.handle())
