# Manual Registration

archtool auto-discovers and wires the vast majority of dependencies. But some objects can't be auto-discovered: async resources initialised at startup, third-party instances, or conditionally-swapped implementations.

For these, use `injector.register()` before calling `inject()`.

---

## The pattern

```python
injector = DependencyInjector(modules_list=[...], project_root=ROOT)

# Pre-register manually
injector.register(key=SomeABC, value=some_instance)

# Then wire everything — manual registrations are respected, auto-discovery skips them
injector.inject()
```

`register()` parameters:

| Parameter | Description |
|---|---|
| `key` | Interface class used as the lookup key |
| `value` | Any instance to register |
| `inject_into` | When `True` (default), pass-2 wires this instance's own annotations. Set to `False` for third-party objects. |

---

## Async resources (database pools, HTTP clients)

archtool's `inject()` is synchronous — it runs at startup before the event loop starts. Async resources must be created outside `inject()` and handed in via `register()`.

```python
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

async def create_app():
    engine = create_async_engine(DATABASE_URL, echo=False)
    session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    injector = DependencyInjector(modules_list=[...], project_root=ROOT)
    injector.register(key=async_sessionmaker, value=session_maker, inject_into=False)
    injector.inject()

    # Any repo annotated `session_maker: async_sessionmaker` gets it automatically
    return injector
```

---

## Config objects

If your services or repos need configuration, wrap it in a simple class and register it:

```python
from dataclasses import dataclass

@dataclass
class AppConfig:
    stripe_key: str
    s3_bucket: str

class AppConfigABC(ABC): ...

config = AppConfig(
    stripe_key=os.environ["STRIPE_KEY"],
    s3_bucket=os.environ["S3_BUCKET"],
)

injector.register(key=AppConfigABC, value=config)
injector.inject()
```

```python
# app/payments/services.py
class PaymentService(PaymentServiceABC):
    config: AppConfigABC   # archtool wires the pre-registered AppConfig
```

---

## Test stubs

Pre-registration is the recommended way to swap in test doubles:

```python
# tests/test_order_service.py
def test_place_order():
    stub_repo = StubOrderRepo(returns=[...])

    injector = DependencyInjector(modules_list=[AppModule("app.orders")], project_root=ROOT)
    injector.register(key=OrderRepoABC, value=stub_repo)
    injector.inject()   # OrderRepo auto-discovery is skipped; stub is used instead

    svc = injector.get_dependency(OrderServiceABC)
    order = asyncio.run(svc.place(user_id=..., items=[...]))
    assert order.status == "pending"
```

---

## Conditional implementations

Different environments (production vs. staging vs. local) may need different implementations:

```python
import os

if os.getenv("USE_S3") == "1":
    storage = S3Storage(bucket=os.environ["S3_BUCKET"])
else:
    storage = LocalStorage(base_path="/tmp/files")

injector.register(key=StorageABC, value=storage)
injector.inject()
```

---

## inject_into=False

By default, archtool's pass-2 injection also runs on manually registered objects — it will wire their own class-level annotations too. Set `inject_into=False` when registering third-party objects that don't use archtool annotations:

```python
import httpx

http_client = httpx.AsyncClient(base_url=API_URL)
injector.register(key=httpx.AsyncClient, value=http_client, inject_into=False)
```

---

## Reading the registry

After `inject()`, `injector.dependencies` is a plain dict. You can inspect it or retrieve instances directly:

```python
injector.inject()

# retrieve by interface
svc = injector.get_dependency(UserServiceABC)

# inspect everything registered
for key, instance in injector.dependencies.items():
    print(key, "→", type(instance).__name__)
```
