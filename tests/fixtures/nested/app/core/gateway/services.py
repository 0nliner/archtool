from .interfaces import GatewayServiceABC, GatewayRepoABC


class GatewayService(GatewayServiceABC):
    repo: GatewayRepoABC

    def check(self) -> bool:
        return self.repo.ping()
