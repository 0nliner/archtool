# Basic project example

A minimal project with a single `users` domain module — everything auto-wired by archtool.

<a class="archtool-download" href="../assets/archtool-basic-example.zip" download>
  ↓ Download example (.zip)
</a>

## File layout

```
myapp/
├── app/
│   └── users/
│       ├── __init__.py
│       ├── interfaces.py
│       ├── services.py
│       └── repos.py
├── entrypoints/
│   └── run.py
└── pyproject.toml
```

---

## interfaces.py

Abstract classes inheriting archtool's layer markers. Contract only — no implementation.

```python
from abc import abstractmethod
from archtool.layers.default_layer_interfaces import ABCService, ABCRepo


class UserRepoABC(ABCRepo):
    @abstractmethod
    def find_all(self) -> list[str]: ...


class UserServiceABC(ABCService):
    @abstractmethod
    def get_name(self) -> str: ...
```

`ABCRepo` and `ABCService` are layer markers — they tell archtool which file to scan (`repos.py` vs `services.py`) and which layer each interface belongs to.

---

## repos.py

Concrete implementation. No `__init__` parameters — archtool instantiates it as `UserRepo()`.

```python
from .interfaces import UserRepoABC


class UserRepo(UserRepoABC):
    def find_all(self) -> list[str]:
        return ["alice", "bob"]
```

---

## services.py

The dependency `repo: UserRepoABC` is declared as a **class-level annotation on the concrete class**. archtool reads it in pass 2 and calls `setattr(instance, "repo", user_repo_instance)`.

```python
from .interfaces import UserServiceABC, UserRepoABC


class UserService(UserServiceABC):
    repo: UserRepoABC   # archtool sets this automatically

    def get_name(self) -> str:
        return self.repo.find_all()[0]
```

---

## entrypoints/run.py

```python
from pathlib import Path
from archtool.dependency_injector import DependencyInjector
from archtool.global_types import AppModule
from app.users.interfaces import UserServiceABC

ROOT = Path(__file__).parent.parent

injector = DependencyInjector(
    modules_list=[AppModule("app.users")],
    project_root=ROOT,
)
injector.inject()

service = injector.get_dependency(UserServiceABC)
print(service.get_name())
```

---

## Run it

```bash
pip install archtool
archtool init myapp
cd myapp && pip install -e ".[dev]"
python entrypoints/run.py
# alice
```

---

## What happened

1. archtool scanned `app/users/interfaces.py` → found `UserRepoABC`, `UserServiceABC`
2. Scanned `app/users/repos.py` → found `UserRepo(UserRepoABC)` → instantiated it
3. Scanned `app/users/services.py` → found `UserService(UserServiceABC)` → instantiated it
4. Read `UserService.__annotations__` → `{"repo": UserRepoABC}`
5. Looked up `UserRepoABC` in registry → found the `UserRepo` instance
6. Called `setattr(user_service, "repo", user_repo)`

Zero registration code. Zero wiring code. Zero `sys.path` manipulation.
