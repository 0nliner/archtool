# Custom Layers

archtool ships with four built-in layers that follow Clean Architecture: `InfrastructureLayer`, `DomainLayer`, `ApplicationLayer`, `PresentationLayer`. These are a starting point, not a requirement.

If your architecture is different — hexagonal, onion, or something entirely bespoke — you define your own layers.

---

## How layers work

A layer is a class that inherits from `Layer` and declares:

- `depends_on` — which layer this one depends on (or `None` for the bottom layer)
- `Components` — an inner class listing `ComponentPattern` descriptors

Each `ComponentPattern` binds:

- `module_name_regex` — the filename to scan (without `.py`)
- `superclass` — the ABC marker class that inhabitants must inherit from

```python
from archtool.layers import Layer
from archtool.components.default_component import ComponentPattern
from abc import ABC


class ABCClient(ABC): ...  # your custom marker


class IntegrationsLayer(Layer):
    depends_on = None   # bottom layer

    class Components:
        clients = ComponentPattern(
            module_name_regex="clients",
            superclass=ABCClient,
        )
```

With this layer defined, archtool will:

1. Scan `{module}/clients.py` in each `AppModule` for concrete subclasses of `ABCClient`
2. Expect their interfaces in `{module}/interfaces.py` as abstract subclasses of `ABCClient`
3. Instantiate and wire them automatically

---

## Multiple component groups per layer

A layer can have more than one `ComponentPattern`. For example, an integrations layer that covers both API clients and message queue adapters:

```python
class ABCAdapter(ABC): ...


class IntegrationsLayer(Layer):
    depends_on = None

    class Components:
        clients = ComponentPattern(module_name_regex="clients", superclass=ABCClient)
        adapters = ComponentPattern(module_name_regex="adapters", superclass=ABCAdapter)
```

archtool will scan `clients.py` for `ABCClient` subclasses **and** `adapters.py` for `ABCAdapter` subclasses — in the same layer pass.

---

## Replacing the built-in layers entirely

Pass your own layer list to `DependencyInjector`:

```python
from archtool.dependency_injector import DependencyInjector
from archtool.global_types import AppModule

injector = DependencyInjector(
    modules_list=[AppModule("app.payments")],
    layers=[IntegrationsLayer, DomainLayer],  # only your layers, in dependency order
)
injector.inject()
```

---

## Extending the built-in layers

You can mix built-in and custom layers freely:

```python
from archtool.layers.default_layers import InfrastructureLayer, DomainLayer

class IntegrationsLayer(Layer):
    depends_on = InfrastructureLayer

    class Components:
        clients = ComponentPattern(module_name_regex="clients", superclass=ABCClient)


injector = DependencyInjector(
    modules_list=[...],
    layers=[InfrastructureLayer, IntegrationsLayer, DomainLayer],
)
```

---

## Real-world example

A codebase that separates API clients from database repos:

```
app/
└── payments/
    ├── interfaces.py      ← PaymentRepoABC(ABCRepo), StripeClientABC(ABCClient)
    ├── repos.py           ← PaymentRepo(PaymentRepoABC)
    ├── clients.py         ← StripeClient(StripeClientABC)
    └── services.py        ← PaymentService(PaymentServiceABC)
```

```python
# app/payments/interfaces.py
from abc import abstractmethod
from archtool.layers.default_layer_interfaces import ABCRepo, ABCService

class ABCClient(ABC): ...

class PaymentRepoABC(ABCRepo):
    @abstractmethod
    async def save(self, payment: dict) -> None: ...

class StripeClientABC(ABCClient):
    @abstractmethod
    async def charge(self, amount: int, currency: str) -> dict: ...

class PaymentServiceABC(ABCService):
    @abstractmethod
    async def process(self, amount: int) -> dict: ...
```

```python
# app/payments/clients.py
class StripeClient(StripeClientABC):
    async def charge(self, amount: int, currency: str) -> dict:
        # call Stripe API
        return {"status": "ok"}
```

```python
# app/payments/services.py
class PaymentService(PaymentServiceABC):
    repo: PaymentRepoABC
    stripe: StripeClientABC   # archtool wires StripeClient here

    async def process(self, amount: int) -> dict:
        result = await self.stripe.charge(amount, "USD")
        await self.repo.save(result)
        return result
```

```python
# entrypoints/run.py
from archtool.layers.default_layers import InfrastructureLayer, DomainLayer

class IntegrationsLayer(Layer):
    depends_on = InfrastructureLayer
    class Components:
        clients = ComponentPattern(module_name_regex="clients", superclass=ABCClient)

injector = DependencyInjector(
    modules_list=[AppModule("app.payments")],
    layers=[InfrastructureLayer, IntegrationsLayer, DomainLayer],
    project_root=ROOT,
)
injector.inject()
```

---

## Ignoring a layer for a specific module

If a module doesn't use a particular component group, opt it out:

```python
AppModule(
    "app.notifications",
    ignore=[IntegrationsLayer.Components.clients],  # no clients.py in this module
)
```
