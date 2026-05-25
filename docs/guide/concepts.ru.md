# Концепции

Для понимания archtool достаточно двух вещей: **как он обнаруживает и связывает** классы, и **зачем нужна слоистая архитектура**.

---

## Как archtool обнаруживает и связывает зависимости

### Контракт: interfaces.py

В каждом доменном модуле есть `interfaces.py` с **абстрактными классами**, наследующими маркеры слоёв archtool — `ABCRepo`, `ABCService`, `ABCController`. Эти абстрактные классы описывают контракт (какие методы есть), а не реализацию.

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

`ABCRepo` и `ABCService` — маркеры слоёв: пустые базовые классы, которые говорят archtool — «сканируй этот файл и считай эти классы интерфейсами репозиториев» vs «интерфейсами сервисов».

### Реализации: repos.py / services.py

Конкретные классы живут в отдельных файлах и наследуются от абстрактных интерфейсов. У них **нет параметров в `__init__`** — archtool инстанциирует их как `ConcreteClass()` без аргументов.

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
    repo: UserRepoABC   # зависимость объявлена здесь, на конкретном классе

    def get_name(self) -> str:
        return self.repo.find_all()[0]
```

`repo: UserRepoABC` — это **всё объявление зависимости**. archtool читает эту аннотацию с `UserService` (не с `UserServiceABC`) и понимает: «этому сервису нужен зарегистрированный экземпляр `UserRepoABC`, установить его в `.repo`».

### Двухпроходная инъекция

При вызове `injector.inject()`:

**Проход 1 — обнаружение и регистрация:**

archtool обходит `ComponentPattern` каждого слоя. Например, `InfrastructureLayer` имеет `ComponentPattern("repos", superclass=ABCRepo)`. Для каждого `AppModule`:

1. Сканирует `app.users.interfaces` → ищет абстрактные подклассы `ABCRepo` → `UserRepoABC`
2. Сканирует `app.users.repos` → ищет неабстрактные подклассы `UserRepoABC` → `UserRepo`
3. Инстанциирует: `instance = UserRepo()`
4. Регистрирует по ключу = полный dotted-путь до класса интерфейса:
   `"myproject.app.users.interfaces.UserRepoABC" → UserRepo()`

Затем `DomainLayer` делает то же самое для `ABCService` / `services.py`.

**Между проходами — топологическая сортировка и обнаружение циклов:**

До того как вызвать хоть один `setattr`, archtool сортирует зарегистрированные компоненты так, чтобы каждая зависимость всегда проводилась раньше компонента, который её использует. Это DFS-based топологическая сортировка по графу зависимостей.

Если граф содержит цикл (`ServiceA` нужен `ServiceB`, а `ServiceB` нужен `ServiceA`), archtool немедленно бросает `CircularDependencyError` — до того как тронуть какой-либо объект — с полным путём цикла в сообщении:

```
CircularDependencyError: Circular dependency detected:
ServiceA → ServiceB → ServiceA
```

**Проход 2 — внедрение:**

Компоненты обрабатываются в топологическом порядке (сначала самые глубокие зависимости). Для каждого экземпляра archtool читает аннотации его класса. Для `UserService`:

```
vars(UserService).__annotations__ == {"repo": UserRepoABC}
```

archtool ищет `"myproject.app.users.interfaces.UserRepoABC"` в реестре, находит экземпляр `UserRepo` и вызывает:

```python
setattr(user_service_instance, "repo", user_repo_instance)
```

Результат: `user_service.repo` — полностью проинициализированный `UserRepo`. Никакого бойлерплейта в твоём коде.

### Сборка всего вместе

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
print(service.get_name())   # "alice" — repo был внедрён автоматически
```

---

## Слоистая архитектура

Дефолтные слои archtool напрямую соответствуют Clean Architecture:

| Слой | Сканируемый файл | Суперкласс-маркер |
|---|---|---|
| `InfrastructureLayer` | `repos.py` | `ABCRepo` |
| `DomainLayer` | `services.py` | `ABCService` |
| `ApplicationLayer` | `controllers.py` | `ABCController` |
| `PresentationLayer` | `views.py` | `ABCView` |

Слои собираются в порядке зависимостей: сначала репозитории, затем сервисы (которые зависят от репо), затем контроллеры (которые зависят от сервисов). Второй проход связывает их вместе.

Правило: **внутренние слои не импортируют из внешних**. Domain (сервисы) не должен напрямую импортировать Infrastructure (репо) — они общаются только через объявленный интерфейс. archtool принудительно проверяет это при старте, если передать `layers=[...]` в инжектор.

### Ограниченные контексты

Каждый `AppModule` — это один **ограниченный контекст**: вертикальный срез домена со своими интерфейсами, сервисами и репозиториями:

```
app/
├── users/      ← AppModule("app.users")
├── orders/     ← AppModule("app.orders")
└── payments/   ← AppModule("app.payments")
```

Сервис из `orders` может объявить зависимость на интерфейс из `users` — archtool разрешит её по ключу между модулями.

---

## Паттерн «тест сборки»

```python
def test_di_assembles():
    injector = DependencyInjector(modules_list=APPS, project_root=ROOT)
    injector.inject()   # бросает исключение при любой ошибке разводки
```

Один быстрый тест ловит: пропущенный конкретный класс, неправильное наследование, сломанные аннотации из-за `from __future__ import annotations`, битые импорты — до того как они попадут в продакшен.
