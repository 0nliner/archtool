from .interfaces import UserServiceABC, UserRepoABC


class UserService(UserServiceABC):
    repo: UserRepoABC

    def get_name(self) -> str:
        names = self.repo.find_all()
        return names[0] if names else ""
