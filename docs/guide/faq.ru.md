# FAQ

## Почему в точке входа нужны танцы с sys.path?

В archtool v2 не нужны. Передай `project_root` явно:

```python
from pathlib import Path
from archtool.dependency_injector import DependencyInjector

ROOT = Path(__file__).parent.parent   # где лежит pyproject.toml

injector = DependencyInjector(
    modules_list=[...],
    project_root=ROOT,
)
```

archtool использует этот путь для всего разрешения модулей и не трогает `sys.path[0]`.

---

## Аннотации через `from __future__ import annotations` работают?

Да. archtool v2 использует `typing.get_type_hints()` для разрешения аннотаций — строковые аннотации (PEP 563) обрабатываются прозрачно.

---

## Где объявлять зависимость — на абстрактном классе или на конкретном?

На **конкретном**. archtool читает аннотации через `vars(ConcreteClass).__annotations__` — только те что объявлены непосредственно на данном классе. Аннотации с базового класса не подхватываются.

```python
# ✅ правильно
class UserService(UserServiceABC):
    repo: UserRepoABC   # archtool найдёт это

# ❌ неправильно — archtool не подхватит аннотацию из ABC
class UserServiceABC(ABCService):
    repo: UserRepoABC
```

---

## Нужен ли `__init__` с параметрами?

Нет. archtool вызывает `ConcreteClass()` без аргументов. Если у конкретного класса есть required параметры в конструкторе — сборка упадёт с `TypeError`.

Если тебе нужно проинициализировать объект с параметрами (например, строкой подключения к базе), установи их отдельно после `inject()`, или используй переменные окружения/конфиг, которые класс читает сам при инициализации.

---

## Как зарегистрировать то, что archtool не может авто-обнаружить?

Используй `injector.register()` до вызова `inject()`:

```python
# async-ресурс, сторонний объект или что угодно другое
pool = await asyncpg.create_pool(DATABASE_URL)

injector = DependencyInjector(modules_list=APPS, project_root=ROOT)
injector.register(key=DBPoolABC, value=pool)
injector.inject()   # авто-обнаруживает остальное; пул уже зарегистрирован
```

archtool уважает предзарегистрированные зависимости и пропускает авто-обнаружение для них. После `inject()` пул внедряется в любой компонент, объявивший `pool: DBPoolABC`.

Словарь `injector.dependencies` тоже доступен напрямую — это обычный dict с ключами в виде полного dotted-пути до класса интерфейса.

---

## Как условно подменить реализацию (например, в тестах)?

Предзарегистрируй альтернативу до `inject()`:

```python
# в тестах: меняем реальный репо на заглушку
injector = DependencyInjector(modules_list=APPS, project_root=ROOT)
injector.register(key=UserRepoABC, value=StubUserRepo())
injector.inject()   # находит заглушку уже зарегистрированной, пропускает UserRepo
```

---

## Можно иметь несколько реализаций одного интерфейса?

Нет — archtool требует **одну реализацию на интерфейс на модуль**. Если два конкретных класса наследуют один ABC в одном модуле, при сборке бросается `MultipleRealizationsException`.

---

## Как посмотреть что было внедрено?

После `inject()` проверь `injector._dependencies`:

```python
injector.inject()
for key, obj in injector._dependencies.items():
    print(key, "→", type(obj).__name__)
```

Или через CLI:

```bash
archtool graph
```

---

## Как включить логи сборки?

```bash
ARCHTOOL_VERBOSE=1 python entrypoints/run.py
```

Или:

```python
DependencyInjector(modules_list=[...], verbose=True)
```

archtool никогда не вызывает `logging.basicConfig()` — добавляет `StreamHandler` только когда verbose-режим явно запрошен.

---

## Поддерживается ли async?

archtool — инструмент разводки DI, не async-фреймворк. Он связывает объекты синхронно при старте. Являются ли эти объекты async или нет — твой выбор, archtool не знает и не заботится об этом.
