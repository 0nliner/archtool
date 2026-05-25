# FAQ

## Why does my entrypoint need a sys.path hack?

It doesn't, with archtool v2. Pass `project_root` explicitly:

```python
from pathlib import Path
from archtool.dependency_injector import DependencyInjector

ROOT = Path(__file__).parent.parent   # wherever your pyproject.toml lives

injector = DependencyInjector(
    modules_list=[...],
    project_root=ROOT,
)
```

archtool uses this path for all module resolution and never touches `sys.path[0]`.

---

## My annotations use `from __future__ import annotations`. Will it work?

Yes. archtool v2 uses `typing.get_type_hints()` to resolve annotations, which handles PEP 563 stringified annotations transparently.

---

## How do I register something archtool can't auto-discover?

Use `injector.register()` before calling `inject()`:

```python
# async resource, third-party object, or anything else
pool = await asyncpg.create_pool(DATABASE_URL)

injector = DependencyInjector(modules_list=APPS, project_root=ROOT)
injector.register(key=DBPoolABC, value=pool)
injector.inject()   # auto-discovers the rest; pool is already there
```

archtool respects pre-registered dependencies and skips auto-discovery for them. After `inject()`, the pool is injected into any component that declares `pool: DBPoolABC`.

You can also read `injector.dependencies` directly — it's a plain dict keyed by the serialised interface path.

---

## How do I swap an implementation conditionally (e.g. in tests)?

Pre-register the alternative before `inject()`:

```python
# in tests: swap out the real repo for a stub
injector = DependencyInjector(modules_list=APPS, project_root=ROOT)
injector.register(key=UserRepoABC, value=StubUserRepo())
injector.inject()   # finds the stub already registered, skips UserRepo auto-discovery
```

---

## Can I have more than one implementation of an interface?

No — archtool enforces **one implementation per interface per module**. If two concrete classes both inherit from the same ABC in the same module, `MultipleRealizationsException` is raised at assembly time. This is by design: the whole point is unambiguous wiring.

---

## What happens if there's a circular dependency?

Nothing breaks. In archtool's two-pass scheme all objects are instantiated in Pass 1 before any wiring happens in Pass 2, so `ServiceA.dep = service_b` and `ServiceB.dep = service_a` are valid `setattr` calls — both objects already exist.

archtool does log a `WARNING` once per `inject()` call to flag the cycle:

```
[archtool] WARNING Circular dependency detected: ServiceA → ServiceB → ServiceA.
Wiring will succeed because all objects are already instantiated, but mutual
method recursion may cause infinite loops at runtime.
```

This is a **design signal**: if `ServiceA.method()` calls `self.dep.method()` which in turn calls back into `ServiceA`, that will loop infinitely. The warning is there so you notice the cycle exists — not to block wiring.

Enable the warning with `verbose=True` or `ARCHTOOL_VERBOSE=1`.

---

## My class has constructor arguments — archtool can't instantiate it

archtool calls `Class()` with no arguments. If your class needs them, pre-register the fully constructed instance:

```python
repo = UserRepo(db_url=os.environ["DATABASE_URL"])

injector = DependencyInjector(modules_list=APPS, project_root=ROOT)
injector.register(key=UserRepoABC, value=repo)
injector.inject()  # skips auto-discovery for UserRepoABC, uses your instance
```

Without `register()`, archtool raises `InstantiationError` with a message that points you to this exact fix.

---

## How do I see what was injected?

After calling `inject()`, inspect `injector.dependencies`:

```python
injector.inject()
for key, obj in injector.dependencies.items():
    print(key, "→", type(obj).__name__)
```

Or use the CLI:

```bash
archtool graph
```

---

## How do I enable debug logging?

```bash
ARCHTOOL_VERBOSE=1 python entrypoints/run.py
```

Or:

```python
DependencyInjector(modules_list=[...], verbose=True)
```

archtool never calls `logging.basicConfig()` — it only adds a `StreamHandler` when verbose mode is explicitly requested, so it never floods your application's log output.

---

## Does archtool support async?

archtool is a DI wiring tool, not an async framework. It wires objects together at startup time. Whether those objects are async or not is entirely up to you — archtool doesn't care.
