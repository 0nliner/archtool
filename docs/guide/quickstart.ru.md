# Быстрый старт

Полноценный рабочий проект с нуля за пять минут.

## 0. Установка

```bash
pip install archtool
```

Поддерживается Python **3.10 · 3.11 · 3.12 · 3.13**.

---

## 1. Создать каркас проекта

```bash
archtool init myapp
cd myapp
pip install -e ".[dev]"
```

Это создаёт полный каркас со слоистой архитектурой — первый доменный модуль (`users`) уже подключён:

```
myapp/
├── app/
│   ├── archtool_conf/
│   │   └── custom_layers.py   ← список модулей (APPS)
│   └── users/
│       ├── __init__.py
│       ├── interfaces.py      ← контракты (ABCs)
│       ├── services.py        ← бизнес-логика
│       └── repos.py           ← доступ к данным
├── entrypoints/
│   └── run.py
├── tests/
│   └── test_assembly.py
├── Dockerfile
├── Makefile
└── pyproject.toml
```

---

## 2. Добавлять модули через CLI

Каждый новый бизнес-домен — это новый модуль. Используй `archtool add-module` — он создаёт всю структуру файлов и **автоматически регистрирует модуль** в `custom_layers.py`:

```bash
archtool add-module orders
archtool add-module payments
archtool add-module notifications
```

Каждая команда создаёт:

```
app/orders/
├── __init__.py
├── interfaces.py      ← OrderServiceABC, OrderRepoABC
├── services.py        ← OrderService (с аннотацией repo: OrderRepoABC)
├── repos.py           ← OrderRepo
└── tests/
    ├── conftest.py
    └── test_services.py
```

И добавляет в `custom_layers.py`:
```python
APPS = [
    AppModule("app.users"),
    AppModule("app.orders"),         # ← добавлено автоматически
    AppModule("app.payments"),       # ← добавлено автоматически
    AppModule("app.notifications"),
]
```

### Вложенные модули

Модули можно вкладывать через dot-нотацию — удобно для группировки связанных субдоменов:

```bash
archtool add-module payments.gateway
archtool add-module payments.billing
```

Это создаёт `app/payments/gateway/` и `app/payments/billing/` как самостоятельные модули, каждый со своим `interfaces.py`, `services.py`, `repos.py`.

```python
APPS = [
    AppModule("app.payments.gateway"),
    AppModule("app.payments.billing"),
]
```

---

## 3. Определить интерфейсы

Интерфейсы — это **абстрактные классы**, наследующие маркеры слоёв archtool. Только контракт, никакой реализации.

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

Этот файл — **проектный документ** ограниченного контекста Orders. Пиши docstring'и здесь — они описывают поведение, а не реализацию.

---

## 4. Написать конкретные реализации

Конкретные классы наследуются от интерфейсов. **Никаких параметров в `__init__`** — archtool инстанциирует их как `Class()`. Межмодульные зависимости объявляются как классовые аннотации.

```python
# app/orders/repos.py
from .interfaces import OrderRepoABC

class OrderRepo(OrderRepoABC):
    def find_all(self) -> list[dict]:
        return []  # замени реальным вызовом БД
```

```python
# app/orders/services.py
from app.users.interfaces import UserServiceABC   # кросс-модульная зависимость
from .interfaces import OrderServiceABC, OrderRepoABC

class OrderService(OrderServiceABC):
    repo: OrderRepoABC         # archtool подключит OrderRepo
    user_svc: UserServiceABC   # archtool подключит UserService из другого модуля

    def place(self, user_id: str, items: list) -> dict:
        user = self.user_svc.get(user_id)
        return {"user": user, "items": items}
```

`repo: OrderRepoABC` объявляется на `OrderService` (конкретном классе). archtool читает аннотации во втором проходе и вызывает `setattr(instance, "repo", order_repo_instance)`.

---

## 5. Собрать в точке входа

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

`project_root` убирает любые манипуляции с `sys.path`. archtool использует этот путь для всего разрешения модулей.

---

## 6. Запустить тест сборки

```bash
make test
```

Сгенерированный `tests/test_assembly.py` проверяет, что инжектор собирается без ошибок — ловит пропущенные реализации или сломанные импорты до продакшена.

---

## Переиспользование модулей между проектами

`AppModule` — это просто Python import path. Любой импортируемый модуль — хоть в том же проекте, хоть установленный через pip — можно зарегистрировать в archtool.

**Сценарий: общий модуль авторизации, используемый в нескольких сервисах**

```bash
# В репозитории общих пакетов:
pip install myorg-auth
```

```python
# В любом проекте, которому нужна авторизация:
from archtool.global_types import AppModule

APPS = [
    AppModule("myorg_auth.users"),   # установлен через pip
    AppModule("app.orders"),          # локальный модуль
    AppModule("app.payments"),
]
```

Общий модуль следует той же структуре — `interfaces.py`, `services.py`, `repos.py` — и archtool обнаруживает и разводит его точно так же, как локальный. Это позволяет:

- Поддерживать общекорпоративные модули `auth` или `notifications` в отдельном репо
- Публиковать их на приватный PyPI-сервер
- Устанавливать в каждый проект — никакого copy-paste

**Монорепо:** несколько сервисов в одном репо разделяют модули через относительные пути:

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
AppModule("shared.auth")   # работает если корень монорепо в sys.path
```
