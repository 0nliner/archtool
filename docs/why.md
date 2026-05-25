# Why archtool?

## The architecture debt cycle

Every backend project starts with good intentions. Interfaces, clean layers, no circular imports. Then deadlines hit, and the "temporary" workarounds multiply.

Six months in, you have:

- A 200-line entrypoint that manually wires 30 objects in the exact right order
- A `sys.path.insert(0, "..")` at the top of every entry file because nobody fixed the import paths
- A "service" that imports directly from another module's repo file because "it was faster"
- Tests that break when you add a new dependency because you forgot to update the mock tree
- A new developer who spent two days just understanding how the app boots

This is not a skill problem. It's a structural problem. **Manual wiring doesn't scale.**

---

## Why other DI solutions don't fix it

Most Python DI libraries solve the wrong problem. They replace manual wiring with... manual registration:

```python
# dependency-injector
class Container(containers.DeclarativeContainer):
    user_repo = providers.Singleton(UserRepo)
    user_service = providers.Factory(UserService, repo=user_repo)
    order_repo = providers.Singleton(OrderRepo)
    order_service = providers.Factory(OrderService, repo=order_repo, user_service=user_service)
    # ... 50 more providers ...
```

You still write every connection by hand. You still forget to update the container when you add a dependency. The container becomes a second codebase that must be kept in sync with the first.

They also do nothing about architecture: nothing stops a service from importing a repo directly, or a controller from calling the database. The violations are invisible until they cause a bug.

---

## What archtool does differently

**Convention replaces registration.**

If your class is in `app/users/repos.py` and inherits from `ABCRepo`, archtool finds it. If `UserService` has `repo: UserRepoABC` as a class annotation, archtool wires it. No container. No registration call. No sync problem.

**Architecture is enforced, not hoped for.**

You declare layers. archtool verifies at startup that no class crosses a forbidden boundary. The violation is an exception on boot, not a subtle bug three months later.

**The structure is the documentation.**

When every project uses the same layout — `interfaces.py`, `services.py`, `repos.py` — a new developer knows where to look immediately. The interfaces file is literally the design document for that bounded context.

---

## SOLID, enforced by structure

archtool doesn't just *allow* SOLID — it makes violations harder than compliance.

**Single Responsibility** — each `AppModule` is one bounded context. Users, Orders, Payments are separate. They can't accidentally bleed into each other.

**Open/Closed** — adding a new module requires zero changes to existing code. The injector picks it up from the `modules_list`. Existing modules are untouched.

**Liskov Substitution** — swap `UserRepo` for `StubUserRepo` (pre-register before `inject()`), and every consumer gets the stub. The consumers never knew they were talking to a specific class.

**Interface Segregation** — your interfaces live in one focused file. Nothing forces you to cram unrelated methods into one interface. Small, focused ABCs are the natural pattern.

**Dependency Inversion** — the entire framework is built on this. Nothing depends on concrete classes. Services depend on `UserRepoABC`. Controllers depend on `UserServiceABC`. Concretions are a runtime detail.

---

## Interface-first design

The right way to design a system is to start with the interfaces, not the implementations.

Your `interfaces.py` is the **design document** for that bounded context:

```python
# app/orders/interfaces.py
class OrderRepoABC(ABCRepo):
    @abstractmethod
    async def get(self, order_id: UUID) -> Order: ...

    @abstractmethod
    async def save(self, order: Order) -> None: ...


class OrderServiceABC(ABCService):
    @abstractmethod
    async def place(self, user_id: UUID, items: list[Item]) -> Order: ...

    @abstractmethod
    async def cancel(self, order_id: UUID) -> None: ...
```

Reading this file, you know exactly what the orders bounded context does. No implementation details. No framework noise. Just the contract.

When you write the docstrings here, you're documenting the behaviour — not the code. This is where architectural decisions live. The implementation files are just the fulfilment of this contract.

---

## Any project can use this

You don't need to start fresh. You can introduce archtool into an existing project module by module:

1. Pick one bounded context
2. Extract its interfaces into `interfaces.py` inheriting from the archtool markers
3. Move the concrete classes to `services.py` / `repos.py`
4. Add the `AppModule` to the injector

The rest of the codebase doesn't change. You migrate at your own pace.

---

## Custom layers for custom architectures

archtool ships with four built-in layers (Infrastructure, Domain, Application, Presentation) that follow Clean Architecture. But if your architecture is different — hexagonal, onion, something entirely bespoke — you define your own layers:

```python
class IntegrationsLayer(Layer):
    depends_on = InfrastructureLayer
    class Components:
        clients = ComponentPattern("clients", superclass=ABCClient)
        adapters = ComponentPattern("adapters", superclass=ABCAdapter)
```

archtool then scans `clients.py` for `ABCClient` subclasses and `adapters.py` for `ABCAdapter` subclasses, and wires them automatically. **The framework adapts to your architecture, not the other way around.**
