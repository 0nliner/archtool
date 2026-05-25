# Кастомные слои

archtool поставляется с четырьмя встроенными слоями Clean Architecture: `InfrastructureLayer`, `DomainLayer`, `ApplicationLayer`, `PresentationLayer`. Это отправная точка, а не обязательное условие.

Если ваша архитектура другая — гексагональная, луковая или полностью своя — вы определяете свои слои.

---

## Как устроены слои

Слой — это класс, наследующий `Layer`, который объявляет:

- `depends_on` — от какого слоя зависит текущий (или `None` для нижнего слоя)
- `Components` — внутренний класс со списком дескрипторов `ComponentPattern`

Каждый `ComponentPattern` связывает:

- `module_name_regex` — имя файла для сканирования (без `.py`)
- `superclass` — класс-маркер ABC, от которого должны наследоваться найденные классы

```python
from archtool.layers import Layer
from archtool.components.default_component import ComponentPattern
from abc import ABC


class ABCClient(ABC): ...  # ваш кастомный маркер


class IntegrationsLayer(Layer):
    depends_on = None   # нижний слой

    class Components:
        clients = ComponentPattern(
            module_name_regex="clients",
            superclass=ABCClient,
        )
```

С таким слоем archtool будет:

1. Сканировать `{module}/clients.py` в каждом `AppModule` на конкретные подклассы `ABCClient`
2. Ожидать интерфейсы в `{module}/interfaces.py` как абстрактные подклассы `ABCClient`
3. Инстанциировать и разводить их автоматически

---

## Несколько групп компонентов в одном слое

Слой может содержать несколько `ComponentPattern`. Например, слой интеграций, который охватывает и API-клиенты, и адаптеры очередей сообщений:

```python
class ABCAdapter(ABC): ...


class IntegrationsLayer(Layer):
    depends_on = None

    class Components:
        clients = ComponentPattern(module_name_regex="clients", superclass=ABCClient)
        adapters = ComponentPattern(module_name_regex="adapters", superclass=ABCAdapter)
```

archtool будет сканировать `clients.py` на подклассы `ABCClient` **и** `adapters.py` на подклассы `ABCAdapter` — в одном проходе слоя.

---

## Полная замена встроенных слоёв

Передайте собственный список слоёв в `DependencyInjector`:

```python
from archtool.dependency_injector import DependencyInjector
from archtool.global_types import AppModule

injector = DependencyInjector(
    modules_list=[AppModule("app.payments")],
    layers=[IntegrationsLayer, DomainLayer],  # только ваши слои, в порядке зависимостей
)
injector.inject()
```

---

## Расширение встроенных слоёв

Встроенные и кастомные слои можно свободно смешивать:

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

## Реальный пример

Кодовая база, где API-клиенты отделены от репозиториев базы данных:

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
        # вызов Stripe API
        return {"status": "ok"}
```

```python
# app/payments/services.py
class PaymentService(PaymentServiceABC):
    repo: PaymentRepoABC
    stripe: StripeClientABC   # archtool подключит StripeClient

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

## Игнорирование слоя для конкретного модуля

Если у модуля нет определённой группы компонентов, исключите её:

```python
AppModule(
    "app.notifications",
    ignore=[IntegrationsLayer.Components.clients],  # в этом модуле нет clients.py
)
```
