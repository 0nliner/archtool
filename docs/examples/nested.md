# Nested modules example

Domain modules can be nested to any depth. This example shows a `gateway` context inside `core`.

## File layout

```
app/
└── core/
    └── gateway/
        ├── __init__.py
        ├── interfaces.py
        ├── services.py
        └── repos.py
```

## Register with the full path

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

archtool treats `app.core.gateway` as the bounded context and scans `app.core.gateway.interfaces`, `app.core.gateway.services`, and `app.core.gateway.repos` automatically.

## interfaces.py

```python
from abc import ABC, abstractmethod


class GatewayRepoABC(ABC):
    @abstractmethod
    def ping(self) -> bool:
        ...


class GatewayServiceABC(ABC):
    repo: GatewayRepoABC

    @abstractmethod
    def check(self) -> bool:
        ...
```

## repos.py

```python
from app.core.gateway.interfaces import GatewayRepoABC


class GatewayRepo(GatewayRepoABC):
    def ping(self) -> bool:
        return True
```

## services.py

```python
from app.core.gateway.interfaces import GatewayRepoABC, GatewayServiceABC


class GatewayService(GatewayServiceABC):
    repo: GatewayRepoABC

    def check(self) -> bool:
        return self.repo.ping()
```
