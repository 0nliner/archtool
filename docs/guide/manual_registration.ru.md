# Ручная регистрация

archtool автоматически обнаруживает и связывает большинство зависимостей. Но некоторые объекты нельзя обнаружить автоматически: async-ресурсы, инициализируемые при старте; сторонние экземпляры; условно подменяемые реализации.

Для них используй `injector.register()` до вызова `inject()`.

---

## Паттерн

```python
injector = DependencyInjector(modules_list=[...], project_root=ROOT)

# Предварительная регистрация вручную
injector.register(key=SomeABC, value=some_instance)

# Затем разводка — ручные регистрации уважаются, авто-обнаружение пропускает их
injector.inject()
```

Параметры `register()`:

| Параметр | Описание |
|---|---|
| `key` | Класс интерфейса в качестве ключа поиска |
| `value` | Любой регистрируемый экземпляр |
| `inject_into` | При `True` (по умолчанию), второй проход разводит собственные аннотации этого экземпляра. Установи в `False` для сторонних объектов. |

---

## Async-ресурсы (пулы БД, HTTP-клиенты)

`inject()` в archtool синхронный — он запускается при старте до начала event loop. Async-ресурсы нужно создать вне `inject()` и передать через `register()`.

```python
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

async def create_app():
    engine = create_async_engine(DATABASE_URL, echo=False)
    session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    injector = DependencyInjector(modules_list=[...], project_root=ROOT)
    injector.register(key=async_sessionmaker, value=session_maker, inject_into=False)
    injector.inject()

    # Любой репо с аннотацией `session_maker: async_sessionmaker` получит его автоматически
    return injector
```

---

## Объекты конфигурации

Если сервисам или репозиториям нужна конфигурация, оберни её в простой класс и зарегистрируй:

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
    config: AppConfigABC   # archtool подключит предзарегистрированный AppConfig
```

---

## Заглушки в тестах

Предварительная регистрация — рекомендованный способ подменять реализации в тестах:

```python
# tests/test_order_service.py
def test_place_order():
    stub_repo = StubOrderRepo(returns=[...])

    injector = DependencyInjector(modules_list=[AppModule("app.orders")], project_root=ROOT)
    injector.register(key=OrderRepoABC, value=stub_repo)
    injector.inject()   # авто-обнаружение OrderRepo пропускается; используется заглушка

    svc = injector.get_dependency(OrderServiceABC)
    order = asyncio.run(svc.place(user_id=..., items=[...]))
    assert order.status == "pending"
```

---

## Условные реализации

Разные среды (прод, стейджинг, локал) могут требовать разных реализаций:

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

По умолчанию второй проход injeciton также запускается для вручную зарегистрированных объектов — их классовые аннотации тоже будут разведены. Установи `inject_into=False` при регистрации сторонних объектов без archtool-аннотаций:

```python
import httpx

http_client = httpx.AsyncClient(base_url=API_URL)
injector.register(key=httpx.AsyncClient, value=http_client, inject_into=False)
```

---

## Чтение реестра

После `inject()` `injector.dependencies` — это обычный dict. Можно его инспектировать или получать экземпляры напрямую:

```python
injector.inject()

# получить по интерфейсу
svc = injector.get_dependency(UserServiceABC)

# инспектировать всё зарегистрированное
for key, instance in injector.dependencies.items():
    print(key, "→", type(instance).__name__)
```
