# Исключения

Все исключения archtool наследуются от `ArchToolError`.

```python
from archtool.exceptions import (
    ArchToolError,
    CircularDependencyError,
    DependencyDuplicate,
    DependencyDoesNotRegistred,
    InstantiationError,
    TopLevelLayerUsingException,
    MultipleRealizationsException,
    RealizationNotFound,
    ModuleValidationError,
    AnnotationsNotResolvableError,
)
```

---

## Справочник

### `ArchToolError`

Базовый класс для всех исключений archtool.

---

### `DependencyDuplicate`

Выбрасывается при вызове `register()` с другим экземпляром для уже зарегистрированного ключа.

```python
injector.register(key=UserRepoABC, value=repo_a)
injector.register(key=UserRepoABC, value=repo_b)  # выбросит DependencyDuplicate
```

**Не выбрасывается**, если один и тот же экземпляр регистрируется дважды — этот вызов молча игнорируется.

---

### `DependencyDoesNotRegistred`

Выбрасывается в `get_dependency()` и во время второго прохода инъекции, когда обязательная зависимость не имеет зарегистрированной реализации.

Сообщение об исключении включает список всех текущих ключей реестра для диагностики:

```
DependencyDoesNotRegistred: Dependency 'myproject.app.orders.interfaces.OrderRepoABC'
is not registered in the DI container.

Registered dependencies:
  • myproject.app.users.interfaces.UserRepoABC
  • myproject.app.users.interfaces.UserServiceABC
```

**Частые причины:**
- Модуль, владеющий интерфейсом, не указан в `modules_list`
- Конкретный класс реализации отсутствует в ожидаемом файле слоя
- Интерфейс не наследует нужный маркер слоя (`ABCRepo`, `ABCService` и т.д.)

---

### `TopLevelLayerUsingException`

Выбрасывается, когда класс в нижнем слое напрямую импортирует из верхнего, нарушая границы Clean Architecture.

Ловится **при старте** во время `inject()`, а не в рантайме.

---

### `MultipleRealizationsException`

Выбрасывается, когда более одного конкретного класса реализует один и тот же интерфейс в одном модуле.

archtool принудительно требует одну реализацию на интерфейс на модуль. Для условной разводки (prod vs. заглушка) используйте `register()` до `inject()`.

---

### `RealizationNotFound`

Выбрасывается, когда интерфейс объявлен в `interfaces.py`, но в ожидаемом файле слоя не найдена конкретная реализация.

---

### `ModuleValidationError`

Выбрасывается командой CLI `archtool validate`, когда `AppModule` не проходит структурные проверки (например, отсутствует `interfaces.py`).

---

### `CircularDependencyError`

Выбрасывается во время `inject()`, когда граф зависимостей содержит цикл. archtool выполняет топологическую сортировку (DFS) перед проходом 2. При обнаружении обратного ребра сортировка немедленно прерывается — **до любого вызова `setattr`** — контейнер остаётся в чистом состоянии.

Сообщение исключения содержит полный путь цикла с короткими именами классов и полными сериализованными ключами:

```
CircularDependencyError: Circular dependency detected:
OrderService → PaymentService → OrderService

Full keys: ['myproject.app.orders.interfaces.OrderServiceABC',
            'myproject.app.payments.interfaces.PaymentServiceABC',
            'myproject.app.orders.interfaces.OrderServiceABC']
```

**Решение:** разорвать цикл через общий интерфейс, от которого зависит одна из сторон, или предварительно зарегистрировать один из компонентов через `injector.register()` до `inject()`.

---

### `InstantiationError`

Выбрасывается, когда archtool не может вызвать `impl_class()` без аргументов в проходе 1.

archtool всегда инстанциирует конкретные классы как `Class()`. Если конструктор требует позиционные аргументы — вызов упадёт с `TypeError`, который перебрасывается как `InstantiationError` с понятным сообщением:

```
InstantiationError: Cannot instantiate 'UserRepo': __init__() missing 1
required positional argument: 'db_url'

archtool requires a no-argument __init__. Use injector.register(InterfaceABC,
your_instance) before inject() to provide instances that need constructor arguments.
```

**Решение:** предварительно зарегистрировать экземпляр через `register()` до вызова `inject()`.

---

### `AnnotationsNotResolvableError`

Выбрасывается, когда аннотации класса не удаётся разрешить — чаще всего при использовании `from __future__ import annotations` с forward-ссылкой, которой не существует во время сборки DI.
