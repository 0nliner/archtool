# DependencyInjector

Главная точка входа для сборки зависимостей в archtool.

---

## Конструктор

```python
DependencyInjector(
    modules_list: list[AppModule],
    layers: list[type[Layer]] | None = None,
    project_root: Path | None = None,
    verbose: bool | None = None,
)
```

| Параметр | Тип | Значение по умолчанию | Описание |
|---|---|---|---|
| `modules_list` | `list[AppModule]` | обязательный | Модули ограниченных контекстов для сканирования. См. [AppModule](app_module.md). |
| `layers` | `list[type[Layer]] \| None` | `None` | Определения слоёв. `None` — используются четыре встроенных слоя Clean Architecture. |
| `project_root` | `Path \| None` | `None` | Абсолютный путь к корню проекта. При `None` archtool ищет `pyproject.toml` / `.git` / `setup.cfg` вверх по дереву от `cwd`. Лучше передавать явно из entrypoint. |
| `verbose` | `bool \| None` | `None` | Включить отладочный вывод в stderr. Управляется также через переменную окружения `ARCHTOOL_VERBOSE=1`. |
| `enforce_layers` | `bool` | `True` | При `True` (по умолчанию) archtool проверяет нарушения границ слоёв между проходами 1 и 2. Установите `False`, чтобы пропустить проверку. |

**Пример:**

```python
from pathlib import Path
from archtool.dependency_injector import DependencyInjector
from archtool.global_types import AppModule

ROOT = Path(__file__).parent.parent

injector = DependencyInjector(
    modules_list=[
        AppModule("app.users"),
        AppModule("app.orders"),
        AppModule("app.payments"),
    ],
    project_root=ROOT,
)
```

---

## Методы

### `inject()`

Сканирует все модули, инстанциирует компоненты и связывает зависимости. Вызывается один раз после создания инжектора (и после всех `register()`).

```python
injector.inject()
```

**Что происходит внутри:**

1. **Проход 1 — обнаружение и регистрация.** Для каждого слоя и каждого `ComponentPattern` archtool сканирует `interfaces.py` на абстрактные подклассы маркера слоя (например `ABCRepo`), затем находит конкретную реализацию в соответствующем файле (например `repos.py`). Каждый конкретный класс инстанциируется как `Class()` и сохраняется в `dependencies`. Бросает `InstantiationError`, если у класса нетривиальный `__init__`.

2. **Проверка слоёв** (при `enforce_layers=True`). После прохода 1 archtool проверяет, что ни один компонент не зависит от компонента из более высокого слоя. При нарушении бросает `TopLevelLayerUsingException`. Проверка выполняется до инъекции — контейнер остаётся чистым при ошибке.

3. **Топологическая сортировка.** До любого `setattr` archtool выполняет DFS-топологическую сортировку графа зависимостей для определения порядка инъекции. При обнаружении цикла выводится `WARNING` — циклы допустимы в двухпроходной схеме (все объекты уже существуют), но могут указывать на взаимную рекурсию методов в рантайме.

4. **Проход 2 — инъекция.** Компоненты обрабатываются в топологическом порядке (сначала самые глубокие зависимости). Для каждого экземпляра archtool читает классовые `__annotations__` и вызывает `setattr(instance, attr_name, dependency_instance)` для каждой аннотированной зависимости.

Ключи, предварительно зарегистрированные через `register()`, пропускаются в проходе 1 — используется предзарегистрированное значение.

---

### `register(key, value, inject_into=True)`

Вручную зарегистрировать зависимость **до** вызова `inject()`.

Используется для объектов, которые archtool не может обнаружить автоматически: async-ресурсы, инициализированные при старте; сторонние объекты; условно подменяемые реализации (например заглушки в тестах).

| Параметр | Тип | Значение по умолчанию | Описание |
|---|---|---|---|
| `key` | `type` | обязательный | Класс интерфейса в качестве ключа поиска — тот же класс, который вы объявляете в классовой аннотации. |
| `value` | `object` | обязательный | Регистрируемый экземпляр. |
| `inject_into` | `bool` | `True` | При `True` archtool также прокинет собственные зависимости этого экземпляра в проходе 2. Установите в `False` для сторонних объектов без аннотаций в стиле archtool. |

**Выбрасывает:** `DependencyDuplicate` — если для того же ключа уже зарегистрирован **другой** экземпляр.

**Пример — async SQLAlchemy session factory:**

```python
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

engine = create_async_engine(DATABASE_URL, echo=False)
session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

injector.register(key=async_sessionmaker, value=session_maker, inject_into=False)
injector.inject()
# репозитории с аннотацией `session_maker: async_sessionmaker` получат её автоматически
```

**Пример — заглушка в тестах:**

```python
stub_repo = StubUserRepo()
injector.register(key=UserRepoABC, value=stub_repo)
injector.inject()
# авто-обнаружение пропускает UserRepoABC — вместо неё используется stub_repo
```

---

### `get_dependency(key)`

Получить зарегистрированную зависимость по классу интерфейса или сериализованному строковому ключу.

```python
user_service = injector.get_dependency(UserServiceABC)
```

**Выбрасывает:** `DependencyDoesNotRegistred` — если ключ не найден в реестре.

---

## Атрибуты

### `dependencies: dict[str, object]`

Полный реестр зарегистрированных экземпляров после `inject()`. Ключи — сериализованные dotted пути импорта.

```python
injector.inject()

# прямой поиск по сериализованному ключу
key = "myproject.app.users.interfaces.UserRepoABC"
repo = injector.dependencies[key]

# перебор всех зарегистрированных компонентов
for key, instance in injector.dependencies.items():
    print(key, "→", type(instance).__name__)
```
