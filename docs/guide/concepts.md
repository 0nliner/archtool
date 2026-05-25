# Concepts

Two ideas make archtool immediately obvious: **how it discovers and wires** classes, and **why layered architecture matters**.

---

## How archtool discovers and wires dependencies

### The contract: interfaces.py

Every domain module has an `interfaces.py` with **abstract classes** that inherit from archtool's layer markers — `ABCRepo`, `ABCService`, `ABCController`. These abstract classes define the contract (what methods exist), not the implementation.

```python
# app/users/interfaces.py
from abc import abstractmethod
from archtool.layers.default_layer_interfaces import ABCService, ABCRepo


class UserRepoABC(ABCRepo):
    @abstractmethod
    def find_all(self) -> list[str]: ...


class UserServiceABC(ABCService):
    @abstractmethod
    def get_name(self) -> str: ...
```

`ABCRepo` and `ABCService` are layer markers — empty base classes that tell archtool "scan this file and treat these as repo interfaces" vs "service interfaces".

### The implementations: repos.py / services.py

Concrete classes live in separate files and inherit from the abstract interfaces. They have **no `__init__` parameters** — archtool instantiates them as `ConcreteClass()` with no arguments.

```python
# app/users/repos.py
from .interfaces import UserRepoABC

class UserRepo(UserRepoABC):
    def find_all(self) -> list[str]:
        return ["alice", "bob"]
```

```python
# app/users/services.py
from .interfaces import UserServiceABC, UserRepoABC

class UserService(UserServiceABC):
    repo: UserRepoABC   # dependency declared here, on the concrete class

    def get_name(self) -> str:
        return self.repo.find_all()[0]
```

`repo: UserRepoABC` is the **entire dependency declaration**. archtool reads this annotation from `UserService` (not from `UserServiceABC`) and knows: "this service needs a registered `UserRepoABC` instance, set it as `.repo`".

### The two-pass injection

When you call `injector.inject()`:

**Pass 1 — discover and register:**

archtool walks every layer's `ComponentPattern`. For example, `InfrastructureLayer` has `ComponentPattern("repos", superclass=ABCRepo)`. For each `AppModule`:

1. Scan `app.users.interfaces` → find abstract subclasses of `ABCRepo` → `UserRepoABC`
2. Scan `app.users.repos` → find non-abstract subclasses of `UserRepoABC` → `UserRepo`
3. Instantiate: `instance = UserRepo()`
4. Register with key = full dotted path to the interface class:
   `"myproject.app.users.interfaces.UserRepoABC" → UserRepo()`

Then `DomainLayer` repeats the same for `ABCService` / `services.py`.

**Between passes — topological sort and cycle detection:**

Before any `setattr` is called, archtool sorts registered components so that each dependency is always wired before the component that uses it. This is a DFS-based topological sort over the dependency graph.

If the graph contains a cycle (`ServiceA` needs `ServiceB` needs `ServiceA`), archtool raises `CircularDependencyError` immediately — before touching any object — with the full cycle path in the message:

```
CircularDependencyError: Circular dependency detected:
ServiceA → ServiceB → ServiceA
```

**Pass 2 — inject:**

Components are processed in topological order (deepest dependencies first). For each instance archtool reads its class-level annotations. For `UserService`:

```
vars(UserService).__annotations__ == {"repo": UserRepoABC}
```

archtool looks up `"myproject.app.users.interfaces.UserRepoABC"` in the registry, finds the `UserRepo` instance, and calls:

```python
setattr(user_service_instance, "repo", user_repo_instance)
```

The result: `user_service.repo` is the fully wired `UserRepo`, with no boilerplate in your code.

### Wiring the whole thing

```python
from pathlib import Path
from archtool.dependency_injector import DependencyInjector
from archtool.global_types import AppModule

injector = DependencyInjector(
    modules_list=[AppModule("app.users")],
    project_root=Path(__file__).parent.parent,
)
injector.inject()

service = injector.get_dependency(UserServiceABC)
print(service.get_name())   # "alice" — repo was injected automatically
```

---

## Layered architecture

The default layers in archtool map directly to Clean Architecture:

| Layer | File scanned | Marker superclass |
|---|---|---|
| `InfrastructureLayer` | `repos.py` | `ABCRepo` |
| `DomainLayer` | `services.py` | `ABCService` |
| `ApplicationLayer` | `controllers.py` | `ABCController` |
| `PresentationLayer` | `views.py` | `ABCView` |

Layers are assembled in dependency order: repos first, then services (which depend on repos), then controllers (which depend on services). The second injection pass wires them together.

The rule: **inner layers must not import from outer layers**. Domain (services) should not import infrastructure (repos) directly — they communicate only through the declared interface. archtool enforces this at startup if you pass `layers=[...]` to the injector.

### Bounded contexts

Each `AppModule` is one **bounded context** — a vertical slice of the domain with its own interfaces, services, and repos:

```
app/
├── users/      ← AppModule("app.users")
├── orders/     ← AppModule("app.orders")
└── payments/   ← AppModule("app.payments")
```

A service in `orders` can declare a dependency on an interface from `users` — archtool resolves it across module boundaries by key.

---

## The assembly test pattern

```python
def test_di_assembles():
    injector = DependencyInjector(modules_list=APPS, project_root=ROOT)
    injector.inject()   # raises on any wiring error
```

One fast test that catches: missing concrete class, wrong inheritance, `from __future__ import annotations` breaking type resolution, broken imports — before they reach production.
