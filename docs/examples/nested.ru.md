# Пример с вложенными модулями

Доменные модули могут быть вложены на любую глубину. В этом примере контекст `gateway` находится внутри `core`.

## Структура файлов

```
app/
└── core/
    └── gateway/
        ├── __init__.py
        ├── interfaces.py
        ├── services.py
        └── repos.py
```

## Регистрация с полным путём

```python
from archtool.dependency_injector import DependencyInjector
from archtool.global_types import AppModule
from pathlib import Path

injector = DependencyInjector(
    modules_list=[AppModule("app.core.gateway")],
    project_root=Path(__file__).parent.parent,
)
injector.inject()
```

archtool трактует `app.core.gateway` как ограниченный контекст и автоматически сканирует `app.core.gateway.interfaces`, `app.core.gateway.services` и `app.core.gateway.repos`.

## interfaces.py

```python
from abc import abstractmethod
from archtool.layers.default_layer_interfaces import ABCService, ABCRepo


class GatewayRepoABC(ABCRepo):
    @abstractmethod
    def ping(self) -> bool: ...


class GatewayServiceABC(ABCService):
    @abstractmethod
    def check(self) -> bool: ...
```

## repos.py

```python
from .interfaces import GatewayRepoABC


class GatewayRepo(GatewayRepoABC):
    def ping(self) -> bool:
        return True
```

## services.py

Зависимость объявлена на конкретном классе `GatewayService`, а не на `GatewayServiceABC`.

```python
from .interfaces import GatewayServiceABC, GatewayRepoABC


class GatewayService(GatewayServiceABC):
    repo: GatewayRepoABC   # archtool установит экземпляр GatewayRepo

    def check(self) -> bool:
        return self.repo.ping()
```
