# Exceptions

All archtool exceptions inherit from `ArchToolError`.

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

## Reference

### `ArchToolError`

Base class for all archtool exceptions.

---

### `DependencyDuplicate`

Raised when `register()` is called with a different instance for an already-registered key.

```python
injector.register(key=UserRepoABC, value=repo_a)
injector.register(key=UserRepoABC, value=repo_b)  # raises DependencyDuplicate
```

**Not raised** when the same instance is registered twice — that call is silently ignored.

---

### `DependencyDoesNotRegistred`

Raised by `get_dependency()` and during pass-2 injection when a required dependency has no registered implementation.

The exception message includes a list of all currently registered keys to help diagnose the issue.

```
DependencyDoesNotRegistred: Dependency 'myproject.app.orders.interfaces.OrderRepoABC'
is not registered in the DI container.

Registered dependencies:
  • myproject.app.users.interfaces.UserRepoABC
  • myproject.app.users.interfaces.UserServiceABC
```

**Common causes:**
- The module owning the interface is not in `modules_list`
- The concrete implementation class is missing from the expected layer file
- The interface does not inherit from the correct layer marker (`ABCRepo`, `ABCService`, etc.)

---

### `TopLevelLayerUsingException`

Raised when a class in a lower layer imports directly from a higher layer, violating Clean Architecture boundaries.

This is caught **at startup** during `inject()`, not at runtime.

---

### `MultipleRealizationsException`

Raised when more than one concrete class implements the same interface in a single module.

archtool enforces one implementation per interface per module. For conditional wiring (e.g. a prod vs. stub implementation), use `register()` before `inject()`.

---

### `RealizationNotFound`

Raised when an interface is declared in `interfaces.py` but no concrete implementation is found in the expected layer file.

---

### `ModuleValidationError`

Raised by the `archtool validate` CLI command when an `AppModule` fails structural checks (e.g. missing `interfaces.py`).

---

### `CircularDependencyError`

Available as a public exception class for use in custom tooling or framework extensions. archtool itself **does not raise** this during normal `inject()` — cycles are tolerated and produce a `WARNING` log instead (see [FAQ](../guide/faq.md#what-happens-if-theres-a-circular-dependency)).

```python
from archtool.exceptions import CircularDependencyError

raise CircularDependencyError(["key.A", "key.B", "key.A"])
```

---

### `InstantiationError`

Raised when archtool cannot call `impl_class()` with no arguments during Pass 1.

archtool always instantiates concrete classes as `Class()`. If the constructor requires positional arguments it will fail with `TypeError`, which is re-raised as `InstantiationError` with a clear message:

```
InstantiationError: Cannot instantiate 'UserRepo': __init__() missing 1
required positional argument: 'db_url'

archtool requires a no-argument __init__. Use injector.register(InterfaceABC,
your_instance) before inject() to provide instances that need constructor arguments.
```

**Fix:** pre-register the instance via `register()` before calling `inject()`.

---

### `AnnotationsNotResolvableError`

Raised when class annotations cannot be resolved — most commonly when `from __future__ import annotations` is combined with a forward reference that doesn't exist at DI assembly time.

---

## Auto-generated reference

::: archtool.exceptions
    options:
      show_source: false
