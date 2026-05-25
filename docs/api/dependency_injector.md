# DependencyInjector

The main entry point for archtool's dependency injection assembly.

---

## Constructor

```python
DependencyInjector(
    modules_list: list[AppModule],
    layers: list[type[Layer]] | None = None,
    project_root: Path | None = None,
    verbose: bool | None = None,
)
```

| Parameter | Type | Default | Description |
|---|---|---|---|
| `modules_list` | `list[AppModule]` | required | Bounded-context modules to scan. See [AppModule](app_module.md). |
| `layers` | `list[type[Layer]] \| None` | `None` | Layer definitions. `None` uses the four built-in Clean Architecture layers. |
| `project_root` | `Path \| None` | `None` | Absolute path to the project root. When `None`, archtool walks up from `cwd` looking for `pyproject.toml` / `.git` / `setup.cfg`. Pass this explicitly from entrypoints. |
| `verbose` | `bool \| None` | `None` | Enable debug logging to stderr. Also controlled by the `ARCHTOOL_VERBOSE=1` environment variable. |
| `enforce_layers` | `bool` | `True` | When `True` (default), archtool checks layer boundary violations between Pass 1 and Pass 2. Set to `False` to skip the check. |

**Example:**

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

## Methods

### `inject()`

Scans all modules, instantiates components, and wires dependencies. Call once after constructing the injector (and after any `register()` calls).

```python
injector.inject()
```

**What happens internally:**

1. **Pass 1 — discovery and registration.** For each layer and each `ComponentPattern`, archtool scans `interfaces.py` for abstract subclasses of the layer marker (e.g. `ABCRepo`), then finds the concrete implementation in the matching file (e.g. `repos.py`). Each concrete class is instantiated as `Class()` and stored in `dependencies`. Raises `InstantiationError` if a class has a non-trivial `__init__`.

2. **Layer enforcement** (when `enforce_layers=True`). After Pass 1, archtool checks that no component depends on a component from a higher layer. Raises `TopLevelLayerUsingException` if a boundary is violated. This check runs before any injection, so the container is still clean on failure.

3. **Topological sort + cycle detection.** Before any `setattr` is called, archtool performs a DFS-based topological sort of the dependency graph to determine injection order. If a cycle is detected, raises `CircularDependencyError` immediately with the full cycle path.

4. **Pass 2 — injection.** Components are processed in topological order (deepest dependencies first). For each instance archtool reads class-level `__annotations__` and calls `setattr(instance, attr_name, dependency_instance)` for each annotated dependency.

Manually pre-registered keys (via `register()`) are skipped in pass 1 — their pre-registered value is used as-is.

---

### `register(key, value, inject_into=True)`

Manually register a dependency **before** calling `inject()`.

Use this for objects archtool cannot discover automatically: async resources initialised at startup, third-party objects, or conditionally-swapped implementations (e.g. stubs in tests).

| Parameter | Type | Default | Description |
|---|---|---|---|
| `key` | `type` | required | Interface class used as the lookup key — same class you would declare in a class-level annotation. |
| `value` | `object` | required | The instance to register. |
| `inject_into` | `bool` | `True` | When `True`, archtool wires this instance's own class-level dependencies in pass 2. Set to `False` for third-party objects that don't use archtool-style annotations. |

**Raises:** `DependencyDuplicate` — if a **different** instance is already registered for the same key.

**Example — async SQLAlchemy session factory:**

```python
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

engine = create_async_engine(DATABASE_URL, echo=False)
session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

injector.register(key=async_sessionmaker, value=session_maker, inject_into=False)
injector.inject()
# repos that declare `session_maker: async_sessionmaker` get it wired automatically
```

**Example — test stub:**

```python
stub_repo = StubUserRepo()
injector.register(key=UserRepoABC, value=stub_repo)
injector.inject()
# auto-discovery skips UserRepoABC — stub_repo is used instead
```

---

### `get_dependency(key)`

Retrieve a registered dependency by its interface class or serialised string key.

```python
user_service = injector.get_dependency(UserServiceABC)
```

**Raises:** `DependencyDoesNotRegistred` — if the key is not found in the registry.

---

## Attributes

### `dependencies: dict[str, object]`

The full registry of registered instances after `inject()`. Keys are serialised dotted import paths.

```python
injector.inject()

# direct lookup by serialised key
key = "myproject.app.users.interfaces.UserRepoABC"
repo = injector.dependencies[key]

# iterate all registered components
for key, instance in injector.dependencies.items():
    print(key, "→", type(instance).__name__)
```

---

## Auto-generated reference

::: archtool.dependency_injector.DependencyInjector
    options:
      show_source: false
      members:
        - inject
        - register
        - get_dependency
