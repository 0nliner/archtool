# Quickstart

Full working project from zero in five minutes.

## 0. Install

```bash
pip install archtool
```

Supports Python **3.10 · 3.11 · 3.12 · 3.13**.

---

## 1. Scaffold a new project

```bash
archtool init myapp
cd myapp
pip install -e ".[dev]"
```

This creates a complete layered-architecture skeleton with the first domain module (`users`) already wired:

```
myapp/
├── app/
│   ├── archtool_conf/
│   │   └── custom_layers.py   ← module list (APPS)
│   └── users/
│       ├── __init__.py
│       ├── interfaces.py      ← contracts (ABCs)
│       ├── services.py        ← business logic
│       └── repos.py           ← data access
├── entrypoints/
│   └── run.py
├── tests/
│   └── test_assembly.py
├── Dockerfile
├── Makefile
└── pyproject.toml
```

---

## 2. Add more modules with the CLI

Every new business domain is a new module. Use `archtool add-module` — it creates the full file structure and **registers the module automatically** in `custom_layers.py`:

```bash
archtool add-module orders
archtool add-module payments
archtool add-module notifications
```

Each command creates:

```
app/orders/
├── __init__.py
├── interfaces.py      ← OrderServiceABC, OrderRepoABC
├── services.py        ← OrderService (with repo: OrderRepoABC annotation)
├── repos.py           ← OrderRepo
└── tests/
    ├── conftest.py
    └── test_services.py
```

And appends to `custom_layers.py`:
```python
APPS = [
    AppModule("app.users"),
    AppModule("app.orders"),    # ← added automatically
    AppModule("app.payments"),  # ← added automatically
    AppModule("app.notifications"),
]
```

### Nested modules

Modules can be nested using dot notation — useful for grouping related subdomains:

```bash
archtool add-module payments.gateway
archtool add-module payments.billing
```

This creates `app/payments/gateway/` and `app/payments/billing/` as independent modules, each with their own `interfaces.py`, `services.py`, `repos.py`.

```python
APPS = [
    AppModule("app.payments.gateway"),
    AppModule("app.payments.billing"),
]
```

---

## 3. Define interfaces

Interfaces are **abstract classes** that inherit from archtool's layer markers. No implementation, just the contract.

```python
# app/orders/interfaces.py
from abc import abstractmethod
from archtool.layers.default_layer_interfaces import ABCService, ABCRepo


class OrderRepoABC(ABCRepo):
    @abstractmethod
    def find_all(self) -> list[dict]: ...


class OrderServiceABC(ABCService):
    @abstractmethod
    def place(self, user_id: str, items: list) -> dict: ...
```

This file is the **design document** for the Orders bounded context. Write docstrings here — they describe behaviour, not implementation.

---

## 4. Write concrete implementations

Concrete classes inherit from the interfaces. **No `__init__` parameters** — archtool instantiates them as `Class()`. Declare cross-cutting dependencies as class-level annotations.

```python
# app/orders/repos.py
from .interfaces import OrderRepoABC

class OrderRepo(OrderRepoABC):
    def find_all(self) -> list[dict]:
        return []  # swap with real DB call
```

```python
# app/orders/services.py
from app.users.interfaces import UserServiceABC   # cross-module dep
from .interfaces import OrderServiceABC, OrderRepoABC

class OrderService(OrderServiceABC):
    repo: OrderRepoABC         # archtool wires OrderRepo here
    user_svc: UserServiceABC   # archtool wires UserService here — from another module

    def place(self, user_id: str, items: list) -> dict:
        user = self.user_svc.get(user_id)
        return {"user": user, "items": items}
```

`repo: OrderRepoABC` is declared on `OrderService` (the concrete class). archtool reads annotations from concrete classes in the second injection pass and calls `setattr(instance, "repo", order_repo_instance)`.

---

## 5. Wire in the entrypoint

```python
# entrypoints/run.py
from pathlib import Path
from archtool.dependency_injector import DependencyInjector
from app.archtool_conf.custom_layers import APPS, app_layers

injector = DependencyInjector(
    modules_list=APPS,
    layers=app_layers,
    project_root=Path(__file__).parent.parent,
)
injector.inject()
```

`project_root` eliminates any `sys.path` manipulation. archtool uses this path for all module resolution.

---

## 6. Run the assembly test

```bash
make test
```

The scaffolded `tests/test_assembly.py` verifies that the injector assembles without errors — catches missing implementations or broken imports before they reach production.

---

## Reusing modules across projects

An `AppModule` is just a Python import path. Any importable module — whether in the same project or installed as a package — can be registered with archtool.

**Scenario: shared authentication module used in multiple services**

```bash
# In a shared package repo:
pip install myorg-auth
```

```python
# In any project that needs auth:
from archtool.global_types import AppModule

APPS = [
    AppModule("myorg_auth.users"),   # installed from pip
    AppModule("app.orders"),          # local module
    AppModule("app.payments"),
]
```

The shared module follows the same structure — `interfaces.py`, `services.py`, `repos.py` — and archtool discovers and wires it exactly like a local module. This lets you:

- Maintain a company-wide `auth` or `notifications` module in a separate repo
- Publish it to a private PyPI server
- Install it in every project that needs it — zero copy-paste

**Monorepo variant:** multiple services in one repo share modules via relative paths:

```
monorepo/
├── shared/
│   └── auth/
│       ├── interfaces.py
│       ├── services.py
│       └── repos.py
├── service_a/
└── service_b/
```

```python
# service_a/entrypoints/run.py
AppModule("shared.auth")   # works if monorepo root is on sys.path
```
