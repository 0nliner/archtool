# Interface-first Design

The conventional way to build a module is to write implementation first and extract interfaces afterward, when "it gets complicated enough." archtool inverts this: **write the interface first, then the implementation.**

This isn't a style preference. It changes how you think about the system.

---

## `interfaces.py` is your design document

Every archtool module has an `interfaces.py`. This file is not boilerplate — it is the **architecture spec** for that bounded context.

```python
# app/orders/interfaces.py
from abc import abstractmethod
from archtool.layers.default_layer_interfaces import ABCRepo, ABCService


class OrderRepoABC(ABCRepo):
    """Persistence for Order aggregates."""

    @abstractmethod
    async def get(self, order_id: UUID) -> Order:
        """Load an order by ID. Raises OrderNotFound if absent."""

    @abstractmethod
    async def save(self, order: Order) -> None:
        """Persist a new or updated order."""

    @abstractmethod
    async def list_by_user(self, user_id: UUID) -> list[Order]:
        """Return all orders placed by a given user."""


class OrderServiceABC(ABCService):
    """Business rules for the Orders bounded context."""

    @abstractmethod
    async def place(self, user_id: UUID, items: list[Item]) -> Order:
        """Validate items, deduct inventory, create order, emit OrderPlaced event."""

    @abstractmethod
    async def cancel(self, order_id: UUID) -> None:
        """Cancel an order if it hasn't shipped yet."""
```

Reading this file, a new developer knows:
- **What the bounded context does** — without reading a single line of implementation
- **What operations are possible** — the public contract
- **What the invariants are** — documented in docstrings, not scattered across implementation files

The implementation files (`repos.py`, `services.py`) are just the fulfilment of this contract.

---

## Design decisions belong in interfaces

When you write the interface, you make decisions:

- `get()` raises `OrderNotFound` vs. returns `None` — pick one, document it
- `place()` is async — is the downstream call I/O-bound? Yes. Document why.
- `cancel()` takes just an `order_id` — the caller never needs the full object

These decisions don't belong in a PR description that nobody reads six months later. They belong in the interface docstring, **where they live next to the contract they describe**.

---

## Write the interface before you write tests

Interface-first naturally leads to test-first:

1. Write `OrderServiceABC` — decide what `place()` and `cancel()` mean
2. Write `StubOrderRepo` that returns fixed data
3. Write tests against `OrderServiceABC` using the stub
4. Write `OrderService` and `OrderRepo` to make the tests pass

At every step, the interface is the source of truth — not the implementation.

---

## The new developer experience

When every project uses the same layout, a new developer knows exactly where to look:

```
app/
├── users/interfaces.py      ← start here, understand the Users context
├── orders/interfaces.py     ← start here, understand the Orders context
└── payments/interfaces.py   ← start here, understand the Payments context
```

No README. No architecture diagram. No digging through implementation files. The `interfaces.py` files **are** the architecture.

---

## Bounded contexts stay bounded

Because interfaces live in separate modules, cross-context dependencies are explicit:

```python
# app/orders/services.py
class OrderService(OrderServiceABC):
    repo: OrderRepoABC
    user_service: UserServiceABC   # cross-context dependency — declared explicitly
```

If `OrderService` needs something from Users, it declares it via an interface annotation. There is no way to accidentally import a concrete class from another module and bypass the contract — archtool would catch the layer violation at startup.

---

## Incremental adoption

You don't need to redesign the whole project. Pick one module, extract its interfaces:

1. Create `app/users/interfaces.py` with `UserRepoABC` and `UserServiceABC`
2. Make the existing classes inherit from them
3. Add `AppModule("app.users")` to the injector

The rest of the codebase is untouched. Migrate bounded context by bounded context, at your own pace.
