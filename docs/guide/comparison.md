# Comparison with other frameworks

## Quick overview

| | archtool | dependency-injector | injector | Manual DI |
|---|---|---|---|---|
| Registration style | Convention (auto-scan) | Explicit providers | Decorator + module | Explicit |
| Boilerplate | Minimal | Medium–High | Medium | High |
| Layer enforcement | ✅ Built-in | ❌ | ❌ | ❌ |
| CLI scaffolding | ✅ | ❌ | ❌ | ❌ |
| `from __future__ import annotations` | ✅ | ✅ | Partial | — |
| Async-specific support | ❌ | ✅ | ❌ | Custom |
| Scopes / lifetimes | ❌ | ✅ | ✅ | Custom |
| Factories / providers | ❌ | ✅ | ✅ | Custom |
| Community / maturity | Small / new | Large / mature | Medium / stable | — |

---

## archtool

archtool uses **class-level annotations on concrete classes** to declare dependencies. No registration code, no decorators — if a class is in the right file and inherits the right base, it's picked up automatically.

```python
# interfaces.py
from archtool.layers.default_layer_interfaces import ABCService, ABCRepo

class UserRepoABC(ABCRepo):
    @abstractmethod
    def find_all(self) -> list[str]: ...

class UserServiceABC(ABCService):
    @abstractmethod
    def get_name(self) -> str: ...

# services.py — annotation on the concrete class, no __init__ needed
class UserService(UserServiceABC):
    repo: UserRepoABC   # archtool reads this, finds UserRepo, calls setattr

    def get_name(self) -> str:
        return self.repo.find_all()[0]
```

```python
injector = DependencyInjector(
    modules_list=[AppModule("app.users")],
    project_root=ROOT,
)
injector.inject()
```

---

## dependency-injector

[dependency-injector](https://python-dependency-injector.ets-labs.org/) by ets-labs — the most popular Python DI library. Uses explicit **providers** declared in a container class.

```python
from dependency_injector import containers, providers

class Container(containers.DeclarativeContainer):
    user_repo = providers.Singleton(UserRepo)
    user_service = providers.Factory(UserService, repo=user_repo)

container = Container()
service = container.user_service()
```

**Strengths:**
- Mature, battle-tested, large community
- Rich provider types: `Singleton`, `Factory`, `ThreadLocalSingleton`, `Resource`, `Coroutine`, …
- First-class async support (async providers, async `init_resources`)
- Scopes and lifetimes for every object
- Framework integrations out of the box (FastAPI, Flask, Django)

**Weaknesses:**
- Every dependency must be registered manually — dozens of lines for a large project
- No layer boundary enforcement
- No CLI tooling

**When to choose over archtool:** you need scopes, async resource management, or framework integrations.

---

## injector

[injector](https://github.com/python-injector/injector) by Alec Thomas — inspired by Google Guice. Uses **modules** and constructor injection via type annotations.

```python
from injector import Injector, Module, provider, singleton

class AppModule(Module):
    @singleton
    @provider
    def provide_repo(self) -> UserRepoABC:
        return UserRepo()

i = Injector([AppModule()])
service = i.get(UserService)   # constructor: def __init__(self, repo: UserRepoABC)
```

Note: `injector` uses **constructor injection** — the dependency is passed as a constructor parameter, not set as a class attribute. This is fundamentally different from archtool's annotation-on-concrete-class style.

**Strengths:**
- Clean Guice-style API
- Scopes: singleton, thread-local, custom
- Auto-binding — can often skip the module declaration entirely for simple cases

**Weaknesses:**
- Requires constructor parameters for every dependency
- Still needs explicit module wiring for non-trivial cases
- No architecture enforcement
- Limited async support

---

## Manual DI (pure Python)

For small projects, manual wiring is often the right answer:

```python
repo = UserRepo()
service = UserService()
service.repo = repo   # same style as archtool, just written by hand
```

**Strengths:**
- Zero dependencies
- No magic — every connection is explicit and debuggable
- Full control over object lifetimes

**Weaknesses:**
- Wiring code grows linearly with the codebase
- Must be maintained by hand as the graph deepens
- No architectural constraint enforcement

---

## Strengths and weaknesses of archtool

### Strengths

- **Zero boilerplate** — add a file in the right place, inherit the right base class, and archtool finds it. No registration calls.
- **Architecture enforcement** — layer boundary violations are caught at startup, not silently at runtime.
- **Works with `from __future__ import annotations`** — uses `typing.get_type_hints()` internally to resolve stringified annotations.
- **CLI scaffolding** — `archtool init` produces a full layered-architecture project skeleton in seconds.
- **Lightweight runtime** — only `click` and `rich` as runtime dependencies.
- **Assembly test** — one test exercises the entire wiring before anything reaches production.

### Things to know (not deal-breakers)

- **Sensible defaults, fully extensible** — the built-in layers (`repos.py`, `services.py`, etc.) follow Clean Architecture conventions. But layers are just classes: you can define your own `Layer` with any `ComponentPattern`, pointing at any filename and any superclass. The defaults are a starting point, not a cage.

- **No required constructor parameters** — concrete classes are instantiated as `Class()`. This is intentional: dependencies flow through DI annotations, not constructors. If an object needs configuration at startup, the cleanest options are:
  - Read it from env vars / config in the `__init__` body (no args needed)
  - Pre-register it via `injector.register(key=ConfigABC, value=my_config)` before calling `inject()` — archtool will inject it like any other dependency
  - After `inject()`, set it directly via `injector.dependencies["...key..."] = value`

- **One implementation per interface per module** — intentional. Conditional wiring (swap a repo in tests) is handled by pre-registering the test implementation before `inject()` runs. archtool respects manually pre-registered dependencies and skips auto-discovery for them.

- **Async resource initialisation** — archtool's job is structural wiring (what connects to what), not lifecycle management. Async resources (connection pools, clients) are initialised outside archtool, then handed in via `injector.register()`:
  ```python
  pool = await asyncpg.create_pool(DATABASE_URL)
  injector.register(key=DBPoolABC, value=pool)
  injector.inject()   # structural wiring still sync; pool is already available
  ```

---

## When to use archtool

**Good fit:**

- Greenfield project following clean/layered architecture
- Team wants zero DI boilerplate: add a module, it's discovered automatically
- Architectural constraints enforced at startup matter
- Need to pre-register async resources or custom objects alongside auto-wired components

**Less suited if:**

- Your domain layout fundamentally doesn't map to the service/repo/controller split and you don't want to define custom layers
- **SQLAlchemy `Session` per request** — archtool does not manage session lifecycles. The idiomatic pattern is to inject `async_sessionmaker` into repos as a regular DI dependency, then open a session per method via a `UnitOfWork` context manager:

  ```python
  class UserRepo(UserRepoABC):
      session_maker: async_sessionmaker  # archtool injects this

      async def get_user(self, user_id: str) -> UserDM:
          async with UnitOfWork(self.session_maker) as uow:
              session = uow.get_session()
              return await session.get(UserORM, user_id)
  ```

  The session lives exactly as long as the method needs it. If a service method must span several repo calls inside one transaction, pass the `UnitOfWork` (or the session itself) as a method argument — explicit and straightforward, unlike React props-drilling.
