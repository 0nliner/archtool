# archtool

### 📖 [Full documentation → 0nliner.github.io/archtool](https://0nliner.github.io/archtool)

**Auto-wiring dependency injection and layer enforcement for Python.**  
Define interfaces. Write implementations. archtool assembles everything at startup — zero registration code, zero wiring boilerplate.

[![PyPI](https://img.shields.io/pypi/v/archtool?color=3e9454)](https://pypi.org/project/archtool)
[![CI](https://github.com/0nliner/archtool/actions/workflows/ci.yml/badge.svg)](https://github.com/0nliner/archtool/actions/workflows/ci.yml)
[![Python](https://img.shields.io/pypi/pyversions/archtool?color=3e9454)](https://pypi.org/project/archtool)
[![MIT](https://img.shields.io/badge/license-MIT-3e9454)](https://github.com/0nliner/archtool/blob/main/LICENSE)

---

## The problem

Every Python backend eventually grows into this:

```python
# entrypoints/run.py
user_repo = UserRepo()
order_repo = OrderRepo()
user_service = UserService()
user_service.repo = user_repo          # don't forget this
order_service = OrderService()
order_service.repo = order_repo
order_service.user_service = user_service  # or this
# ... 40 more lines
```

Manual wiring doesn't scale. Every new dependency means touching the entrypoint. Every new dev breaks it.

## The solution

```python
from pathlib import Path
from archtool.dependency_injector import DependencyInjector
from archtool.global_types import AppModule

injector = DependencyInjector(
    modules_list=[
        AppModule("app.users"),
        AppModule("app.orders"),
        AppModule("app.payments"),
    ],
    project_root=Path(__file__).parent.parent,
)
injector.inject()
```

archtool scans your modules, discovers every interface–implementation pair, instantiates them in dependency order, and wires everything together.

---

## How it works

**Declare the dependency as a class annotation on the concrete class:**

```python
# app/orders/services.py
from app.users.interfaces import UserServiceABC   # cross-module dep
from .interfaces import OrderServiceABC, OrderRepoABC

class OrderService(OrderServiceABC):
    repo: OrderRepoABC        # archtool sets this
    user_svc: UserServiceABC  # and this — from another module

    def place(self, user_id: str, items: list) -> dict:
        user = self.user_svc.get(user_id)
        return {"user": user, "items": items}
```

**Two-pass injection algorithm:**

1. **Pass 1** — scans `interfaces.py` in each module, finds abstract/concrete pairs, instantiates concretions, builds the registry
2. **Pass 2** — reads class-level annotations from each instance, looks up the registry, calls `setattr`

No container class. No decorator. No `__init__` parameters. If the class is in the right file and inherits the right base — it's wired.

---

## Layer enforcement

Declare your layers and archtool enforces boundaries **at startup**:

```python
injector = DependencyInjector(
    modules_list=[...],
    layers=default_layers,  # Infrastructure → Domain → Application → Presentation
)
injector.inject()  # raises TopLevelLayerUsingException if a boundary is crossed
```

A service depending on a controller, a domain class importing infrastructure directly — caught before they reach production.

---

## Install

```bash
pip install archtool
```

Supports Python **3.10 · 3.11 · 3.12 · 3.13**.

---

## Quickstart

```bash
archtool init myapp
cd myapp
pip install -e ".[dev]"
archtool add-module orders
archtool add-module payments
python entrypoints/run.py
```

`archtool init` scaffolds a full layered-architecture project. `archtool add-module` creates the module files and auto-registers it — no manual edits required.

---

## Documentation

**[0nliner.github.io/archtool](https://0nliner.github.io/archtool)**

- [Quickstart](https://0nliner.github.io/archtool/guide/quickstart/) — working project in 5 minutes
- [How it works](https://0nliner.github.io/archtool/guide/concepts/) — two-pass injection explained
- [Layer enforcement](https://0nliner.github.io/archtool/guide/layers/) — clean architecture built in
- [Comparison](https://0nliner.github.io/archtool/guide/comparison/) — vs dependency-injector, injector, manual DI

---

## License

MIT — [Чудайкин Александр](https://github.com/0nliner) · Бюро автоматизации процессов
