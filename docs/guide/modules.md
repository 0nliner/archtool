# Module Structure

archtool discovers dependencies by scanning a **predictable directory layout**. Follow this convention and zero manual registration is required.

## The layout

```
app/
└── <domain>/
    ├── __init__.py
    ├── interfaces.py   ← abstract classes (the "ports")
    ├── services.py     ← concrete service implementations
    └── repos.py        ← concrete repository implementations
```

### `interfaces.py`

Defines the **contracts** for this domain as abstract base classes:

```python
from abc import ABC, abstractmethod

class OrderRepoABC(ABC):
    @abstractmethod
    def save(self, order: dict) -> None: ...

class OrderServiceABC(ABC):
    repo: OrderRepoABC   # declared as a class annotation → archtool injects it

    @abstractmethod
    def place(self, items: list) -> None: ...
```

### `services.py` / `repos.py`

Concrete implementations that archtool auto-discovers and instantiates:

```python
# repos.py
from app.orders.interfaces import OrderRepoABC

class OrderRepo(OrderRepoABC):
    def save(self, order: dict) -> None:
        ...

# services.py
from app.orders.interfaces import OrderRepoABC, OrderServiceABC

class OrderService(OrderServiceABC):
    repo: OrderRepoABC   # archtool resolves this to OrderRepo

    def place(self, items: list) -> None:
        self.repo.save({"items": items})
```

---

## Declaring dependencies

Dependencies are declared as **class-level annotations** on abstract classes:

```python
class CheckoutServiceABC(ABC):
    order_service: OrderServiceABC
    payment_service: PaymentServiceABC
```

archtool reads these annotations, resolves each to its registered concrete implementation, and injects them.

!!! tip "Works with `from __future__ import annotations`"
    archtool uses `typing.get_type_hints()` internally, so stringified annotations (PEP 563) are fully supported.

---

## Nested modules

Bounded contexts can be nested to any depth:

```
app/
└── core/
    └── gateway/
        ├── interfaces.py
        ├── services.py
        └── repos.py
```

Register with the full dotted path:

```python
AppModule("app.core.gateway")
```

---

## Adding a module

Use the CLI instead of creating files by hand:

```bash
archtool add-module payments
```

This creates `app/payments/` with the correct layout and registers it in your `APPS` list.
