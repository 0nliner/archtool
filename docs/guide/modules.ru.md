# Структура модулей

archtool обнаруживает зависимости, сканируя **предсказуемую структуру директорий**. Следуйте этой конвенции — и ручная регистрация не понадобится.

## Структура

```
app/
└── <domain>/
    ├── __init__.py
    ├── interfaces.py   ← абстрактные классы («порты»)
    ├── services.py     ← конкретные реализации сервисов
    └── repos.py        ← конкретные реализации репозиториев
```

### `interfaces.py`

Определяет **контракты** домена в виде абстрактных базовых классов:

```python
from abc import ABC, abstractmethod

class OrderRepoABC(ABC):
    @abstractmethod
    def save(self, order: dict) -> None: ...

class OrderServiceABC(ABC):
    repo: OrderRepoABC   # аннотация класса → archtool внедрит его

    @abstractmethod
    def place(self, items: list) -> None: ...
```

### `services.py` / `repos.py`

Конкретные реализации, которые archtool авто-обнаруживает и инстанциирует:

```python
# repos.py
from app.orders.interfaces import OrderRepoABC

class OrderRepo(OrderRepoABC):
    def save(self, order: dict) -> None:
        ...

# services.py
from app.orders.interfaces import OrderRepoABC, OrderServiceABC

class OrderService(OrderServiceABC):
    repo: OrderRepoABC   # archtool разрешит в OrderRepo

    def place(self, items: list) -> None:
        self.repo.save({"items": items})
```

---

## Объявление зависимостей

Зависимости объявляются как **аннотации на уровне класса** на абстрактных классах:

```python
class CheckoutServiceABC(ABC):
    order_service: OrderServiceABC
    payment_service: PaymentServiceABC
```

archtool читает эти аннотации, разрешает каждую в зарегистрированную конкретную реализацию и внедряет её.

!!! tip "Работает с `from __future__ import annotations`"
    archtool использует `typing.get_type_hints()` внутри, поэтому строковые аннотации (PEP 563) поддерживаются полностью.

---

## Вложенные модули

Ограниченные контексты могут быть вложены на любую глубину:

```
app/
└── core/
    └── gateway/
        ├── interfaces.py
        ├── services.py
        └── repos.py
```

Регистрируем по полному пути с точками:

```python
AppModule("app.core.gateway")
```

---

## Добавить модуль

Используйте CLI вместо ручного создания файлов:

```bash
archtool add-module payments
```

Создаёт `app/payments/` с правильной структурой и директорией `tests/`.
