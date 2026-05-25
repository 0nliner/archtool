# FastAPI + SQLAlchemy с web_fractal

[web_fractal](https://pypi.org/project/web_fractal/) — это batteries-included набор инструментов для бэкенда, построенный поверх archtool. Предоставляет:

- `UnitOfWork` — контекстный менеджер async SQLAlchemy-сессии
- `BaseRepo` — базовый класс для async SQLAlchemy-репозиториев
- `Base` — SQLAlchemy `DeclarativeBase` с async-атрибутами
- `initialize_controllers_api()` — регистрирует FastAPI-роутеры из всех найденных контроллеров
- `import_all_models()` — автоматически импортирует все ORM-модели, чтобы `Base.metadata` был полным до `create_all()`

---

## Структура проекта

```
myapp/
├── entrypoints/
│   └── run.py
├── app/
│   ├── archtool_conf/
│   │   ├── custom_layers.py    ← список модулей + слои
│   │   └── bundle_project.py   ← функция сборки DI
│   ├── users/
│   │   ├── interfaces.py
│   │   ├── repos.py
│   │   ├── services.py
│   │   ├── controllers.py
│   │   └── models.py
│   └── orders/
│       ├── interfaces.py
│       ├── repos.py
│       ├── services.py
│       └── models.py
└── pyproject.toml
```

---

## Список модулей

```python
# app/archtool_conf/custom_layers.py
from archtool.global_types import AppModule
from archtool.layers.default_layers import (
    ApplicationLayer,
    DomainLayer,
    InfrastructureLayer,
    PresentationLayer,
)

app_layers = frozenset([
    PresentationLayer,
    ApplicationLayer,
    DomainLayer,
    InfrastructureLayer,
])

APPS: list[AppModule] = [
    AppModule("app.users"),
    AppModule("app.orders"),
]
```

---

## Сборка DI

```python
# app/archtool_conf/bundle_project.py
import pathlib
from archtool.dependency_injector import DependencyInjector
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import (
    create_async_engine, async_sessionmaker, AsyncSession, AsyncEngine,
)
from sqlalchemy.pool import NullPool
from web_fractal.building_utils import import_all_models, initialize_controllers_api
from web_fractal.db import Base
from app.archtool_conf.custom_layers import APPS, app_layers
import app.config as settings


def bundle(app: FastAPI) -> DependencyInjector:
    backend_root = pathlib.Path(__file__).resolve().parents[2]

    # Создаём инжектор — модули + слои, без разводки
    injector = DependencyInjector(modules_list=APPS, layers=app_layers,
                                  project_root=backend_root)

    # Создаём async SQLAlchemy engine и session factory
    engine = create_async_engine(
        settings.DATABASE_URL_ASYNC, echo=False, poolclass=NullPool,
    )
    session_maker = async_sessionmaker(
        bind=engine, class_=AsyncSession, expire_on_commit=False,
    )

    # Предварительно регистрируем инфраструктурные объекты —
    # репозитории с аннотацией `session_maker: async_sessionmaker`
    # получат их автоматически во втором проходе
    injector.register(key=AsyncEngine, value=engine, inject_into=False)
    injector.register(key=async_sessionmaker, value=session_maker, inject_into=False)

    # Импортируем все ORM-модели чтобы Base.metadata был полным
    import_all_models(Base=Base)

    # Разводим всё
    injector.inject()

    # Прикрепляем инжектор к состоянию FastAPI
    app.state.injector = injector

    # Регистрируем HTTP-роутеры из всех найденных контроллеров
    initialize_controllers_api(injector=injector, app=app)

    @app.on_event("startup")
    async def _create_tables() -> None:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    return injector
```

---

## Точка входа

```python
# entrypoints/run.py
import pathlib, sys

BACKEND_ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_ROOT))

import uvicorn
from fastapi import FastAPI
from app.archtool_conf.bundle_project import bundle
from app.config import HOST, PORT


def create_app() -> FastAPI:
    application = FastAPI(title="My App")
    bundle(app=application)
    return application


app = create_app()

if __name__ == "__main__":
    uvicorn.run(app, host=HOST, port=PORT)
```

---

## Интерфейсы

```python
# app/users/interfaces.py
from abc import abstractmethod
from archtool.layers.default_layer_interfaces import ABCRepo, ABCService


class UserRepoABC(ABCRepo):
    @abstractmethod
    async def get_by_id(self, user_id: str) -> dict | None: ...

    @abstractmethod
    async def create(self, email: str, name: str) -> dict: ...


class UserServiceABC(ABCService):
    @abstractmethod
    async def get_user(self, user_id: str) -> dict: ...

    @abstractmethod
    async def register(self, email: str, name: str) -> dict: ...
```

---

## Репозиторий с SQLAlchemy-сессией

Сессия не является синглтоном — она открывается на каждый вызов метода через `UnitOfWork`. `session_maker` инжектируется archtool как классовая аннотация.

```python
# app/users/repos.py
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker
from web_fractal.db import UnitOfWork

from app.users.interfaces import UserRepoABC
from app.users.models import UserORM


class UserRepo(UserRepoABC):
    session_maker: async_sessionmaker   # archtool инжектирует предзарегистрированный экземпляр

    async def get_by_id(self, user_id: str) -> dict | None:
        async with UnitOfWork(self.session_maker) as uow:
            session = uow.get_session()
            user = await session.scalar(select(UserORM).where(UserORM.id == user_id))
            return {"id": user.id, "email": user.email} if user else None

    async def create(self, email: str, name: str) -> dict:
        async with UnitOfWork(self.session_maker) as uow:
            session = uow.get_session()
            user = UserORM(email=email, name=name)
            session.add(user)
            await session.flush()
            await session.refresh(user)
            return {"id": user.id, "email": user.email}
```

### Общие транзакции

Когда сервисный метод должен охватить несколько вызовов репозитория в одной транзакции, `UnitOfWork` передаётся аргументом:

```python
# app/orders/services.py
class OrderService(OrderServiceABC):
    user_repo: UserRepoABC
    order_repo: OrderRepoABC
    session_maker: async_sessionmaker

    async def place_order(self, user_id: str, items: list) -> dict:
        async with UnitOfWork(self.session_maker) as uow:
            user = await self.user_repo.get_by_id_in_uow(user_id, uow)
            order = await self.order_repo.create_in_uow(user["id"], items, uow)
            return order   # коммит происходит в __aexit__
```

---

## Сервис

```python
# app/users/services.py
from app.users.interfaces import UserRepoABC, UserServiceABC


class UserService(UserServiceABC):
    repo: UserRepoABC   # archtool подключает UserRepo

    async def get_user(self, user_id: str) -> dict:
        user = await self.repo.get_by_id(user_id)
        if not user:
            raise ValueError(f"Пользователь {user_id} не найден")
        return user

    async def register(self, email: str, name: str) -> dict:
        return await self.repo.create(email=email, name=name)
```

---

## Контроллер (FastAPI роутер)

web_fractal предоставляет `HttpControllerABC` — базовый класс, который подключает FastAPI `APIRouter` через `init_http_routes()`. `initialize_controllers_api()` вызывает это для каждого найденного контроллера.

```python
# app/users/controllers.py
from fastapi import APIRouter, HTTPException
from web_fractal.http.interfaces import HttpControllerABC

from app.users.interfaces import UserControllerABC, UserServiceABC


class UserController(UserControllerABC):
    router = APIRouter(prefix="/users", tags=["users"])
    user_service: UserServiceABC   # archtool подключает UserService

    def init_http_routes(self) -> None:
        self.router.add_api_route("/", self.list_users, methods=["GET"])
        self.router.add_api_route("/{user_id}", self.get_user, methods=["GET"])
        self.router.add_api_route("/", self.create_user, methods=["POST"])

    async def get_user(self, user_id: str) -> dict:
        try:
            return await self.user_service.get_user(user_id)
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e))

    async def create_user(self, email: str, name: str) -> dict:
        return await self.user_service.register(email=email, name=name)
```

---

## Установка

```bash
pip install archtool web_fractal
```

web_fractal требует `fastapi`, `sqlalchemy[asyncio]` и `pydantic`.
