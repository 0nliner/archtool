from .interfaces import GatewayRepoABC


class GatewayRepo(GatewayRepoABC):
    def ping(self) -> bool:
        return True
