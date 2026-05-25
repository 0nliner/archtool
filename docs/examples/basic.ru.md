# Базовый пример проекта

Минимальный проект с одним доменным модулем `users`.

<a class="archtool-download" href="../assets/archtool-basic-example.zip" download>
  ↓ Скачать пример (.zip)
</a>

## Структура файлов

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

## interfaces.py

Абстрактные классы, наследующие маркеры слоёв archtool. Только контракт — методов нет.

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

## repos.py

Конкретная реализация. Никакого `__init__` с параметрами — archtool инстанциирует как `UserRepo()`.

```python
from .interfaces import UserRepoABC


class UserRepo(UserRepoABC):
    def find_all(self) -> list[str]:
        return ["alice", "bob"]
```

## services.py

Конкретная реализация. Зависимость `repo: UserRepoABC` объявлена на конкретном классе — archtool прочитает её и установит атрибут.

```python
from .interfaces import UserServiceABC, UserRepoABC


class UserService(UserServiceABC):
    repo: UserRepoABC   # archtool сделает: setattr(instance, "repo", UserRepo())

    def get_name(self) -> str:
        return self.repo.find_all()[0]
```

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

## Запуск

```bash
python entrypoints/run.py
# alice
```
