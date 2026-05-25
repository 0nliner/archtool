from .interfaces import UserRepoABC


class UserRepo(UserRepoABC):
    def find_all(self) -> list[str]:
        return ["alice", "bob"]
