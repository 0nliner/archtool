---
title: archtool
---

<div class="archtool-banner">
  <div class="archtool-banner-glow"></div>
  <div class="archtool-banner-icon">
    <svg viewBox="0 0 80 80" fill="none" xmlns="http://www.w3.org/2000/svg">
      <rect x="21" y="4" width="38" height="16" rx="4" fill="#3e9454"/>
      <line x1="40" y1="20" x2="40" y2="30" stroke="#3e9454" stroke-width="2.5" stroke-linecap="round"/>
      <line x1="17" y1="30" x2="63" y2="30" stroke="#3e9454" stroke-width="2.5" stroke-linecap="round"/>
      <line x1="17" y1="30" x2="17" y2="44" stroke="#3e9454" stroke-width="2.5" stroke-linecap="round"/>
      <line x1="63" y1="30" x2="63" y2="44" stroke="#3e9454" stroke-width="2.5" stroke-linecap="round"/>
      <circle cx="40" cy="30" r="3" fill="#3e9454"/>
      <circle cx="17" cy="30" r="3" fill="#3e9454"/>
      <circle cx="63" cy="30" r="3" fill="#3e9454"/>
      <rect x="4"  y="44" width="26" height="14" rx="4" fill="#3e9454"/>
      <rect x="50" y="44" width="26" height="14" rx="4" fill="#3e9454"/>
      <line x1="17" y1="58" x2="17" y2="65" stroke="#3e9454" stroke-width="2" stroke-linecap="round" opacity="0.4"/>
      <line x1="63" y1="58" x2="63" y2="65" stroke="#3e9454" stroke-width="2" stroke-linecap="round" opacity="0.4"/>
      <rect x="7"  y="65" width="20" height="11" rx="3" fill="#3e9454" opacity="0.3"/>
      <rect x="53" y="65" width="20" height="11" rx="3" fill="#3e9454" opacity="0.3"/>
    </svg>
  </div>
  <div>
    <div class="archtool-banner-title">archtool</div>
    <div class="archtool-banner-tagline">
      Assembles like Lego.<br>
      Works like a hammer.<br>
      Holds like a foundation.
    </div>
  </div>
</div>

<p class="archtool-credit"><span class="archtool-credit-label">developed by</span><span class="archtool-credit-sep">·</span><a class="archtool-credit-name" href="https://github.com/0nliner" target="_blank">Чудайкин Александр</a><span class="archtool-credit-sep">·</span><a class="archtool-credit-org" href="https://github.com/0nliner" target="_blank">Бюро автоматизации процессов</a></p>

<p align="center">
  <a href="https://pypi.org/project/archtool"><img alt="PyPI" src="https://img.shields.io/pypi/v/archtool?color=3e9454"></a>
  <a href="https://github.com/0nliner/archtool/actions/workflows/ci.yml"><img alt="CI" src="https://github.com/0nliner/archtool/actions/workflows/ci.yml/badge.svg"></a>
  <a href="https://pypi.org/project/archtool"><img alt="Python" src="https://img.shields.io/pypi/pyversions/archtool?color=3e9454"></a>
  <a href="https://github.com/0nliner/archtool/blob/main/LICENSE"><img alt="MIT" src="https://img.shields.io/badge/license-MIT-3e9454"></a>
  <a href="https://codecov.io/gh/0nliner/archtool"><img alt="Coverage" src="https://img.shields.io/badge/coverage-coming%20soon-3e9454"></a>
  <a href="https://github.com/sponsors/0nliner"><img alt="Sponsor" src="https://img.shields.io/badge/sponsor-♥-ea4aaa"></a>
</p>

---

## Who are you?

=== "Tech lead"

    Your team grows. Each new service is wired differently. Every new hire reinvents the plumbing. Architecture docs drift from reality.

    archtool gives the whole team **one standard**: declare an interface, write a concrete class, archtool wires it. Layer violations are caught at startup — not in a 3 AM incident. Architecture becomes something you can actually enforce, not just document.

=== "Startup"

    You ship fast. But every shortcut in the foundation costs twice as much when you scale.

    archtool handles the boilerplate so you focus on the product. Add a module, register it, done. The architecture scales with you — no rewrite when you hire engineer #10.

    → **fractal_chunks** *(coming soon)* — battle-tested modules for auth, users, payments, notifications. Plug in what you need; skip what you don't.

=== "Vibe coder"

    You generate code faster than you integrate it. The bottleneck is wiring.

    archtool removes that step. AI writes the service, you declare the interface — archtool connects everything at startup. No boilerplate. No import chains to untangle.

    → **fractal_chunks** *(coming soon)* — a growing catalog of production-grade modules, each a Lego brick. Drop `users`, `auth-jwt`, `notifications` into a new project in minutes, not days.

=== "Architect"

    You've cleaned up enough service-locator messes. You know what happens when DI is informal.

    archtool makes the right patterns the only path. Interfaces are the only contract. Implementations are discovered, not registered. Layer violations fail fast at startup. Clean Architecture — without the ceremony.

---

## The problem every Python project hits

You start clean. A service, a repo, maybe a controller. Then the project grows.

Somewhere around module 5, this happens:

```python
# entrypoints/run.py — the graveyard of good intentions
import sys
sys.path.insert(0, "..")   # ← why is this here again?

from app.users.repos import UserRepo
from app.users.services import UserService
from app.orders.repos import OrderRepo
from app.orders.services import OrderService
from app.payments.repos import PaymentRepo
from app.payments.services import PaymentService
from app.notifications.services import NotificationService

user_repo = UserRepo()
order_repo = OrderRepo()
payment_repo = PaymentRepo()
user_service = UserService()
user_service.repo = user_repo                          # ← don't forget this
order_service = OrderService()
order_service.repo = order_repo
order_service.user_service = user_service              # ← or this
payment_service = PaymentService()
payment_service.repo = payment_repo
payment_service.order_service = order_service          # ← or this
notification_service = NotificationService()
notification_service.payment_service = payment_service # ← or this
# ... 40 more lines ...
```

This is what archtool replaces — entirely.

---

## The solution

```python
# entrypoints/run.py with archtool
from pathlib import Path
from archtool.dependency_injector import DependencyInjector
from archtool.global_types import AppModule

injector = DependencyInjector(
    modules_list=[
        AppModule("app.users"),
        AppModule("app.orders"),
        AppModule("app.payments"),
        AppModule("app.notifications"),
    ],
    project_root=Path(__file__).parent.parent,
)
injector.inject()
```

archtool scans your modules, discovers every interface–implementation pair, instantiates them in dependency order, and wires everything together. No registration boilerplate. No `sys.path` hacks. No hidden wiring bugs.

---

## What you get

=== "Automatic wiring"

    Declare a dependency as a class annotation on your concrete class. archtool reads it and calls `setattr` at assembly time.

    ```python
    # services.py
    class OrderService(OrderServiceABC):
        repo: OrderRepoABC          # archtool sets this
        user_service: UserServiceABC  # and this

        def place(self, items: list) -> None:
            user = self.user_service.get_current()
            self.repo.save({"user": user, "items": items})
    ```

=== "Architecture enforcement"

    Layer violations — a service depending on a controller, a controller reaching into domain internals — are caught **at startup**, not in production at 3 AM.

    ```python
    injector = DependencyInjector(
        modules_list=[...],
        layers=[InfrastructureLayer, DomainLayer, ApplicationLayer],
    )
    injector.inject()  # raises TopLevelLayerUsingException if boundaries are crossed
    ```

=== "Custom layers"

    The built-in layers follow Clean Architecture. But you define your own:

    ```python
    class IntegrationsLayer(Layer):
        depends_on = InfrastructureLayer
        class Components:
            clients = ComponentPattern("clients", superclass=ABCClient)
    ```

    Any filename, any base class — archtool adapts to your architecture, not the other way around.

=== "SOLID out of the box"

    - **S** — each `AppModule` owns one bounded context
    - **O** — add a module, nothing else changes
    - **L** — swap a repo for a stub, consumers don't know
    - **I** — interfaces stay minimal and focused
    - **D** — everything depends on abstractions, never concretions

---

## See it in action

<div class="archtool-playground">
  <div class="pg-tabs">
    <button class="pg-tab pg-tab--active" data-tab="basic">basic_di.py</button>
    <button class="pg-tab" data-tab="multi">multi_module.py</button>
    <button class="pg-tab" data-tab="layer">layer_guard.py</button>
  </div>
  <div class="pg-body">
    <div class="pg-code">

      <div class="pg-pane pg-pane--active" id="pg-pane-basic"><pre class="pg-pre"><span class="cm"># app/users/services.py</span>

<span class="kw">from</span> .interfaces <span class="kw">import</span> <span class="cn">UserServiceABC</span>, <span class="cn">UserRepoABC</span>

<span class="kw">class</span> <span class="cn">UserService</span>(<span class="cn">UserServiceABC</span>):
    <span class="nb">repo</span>: <span class="an hl">UserRepoABC</span>  <span class="cm"># ← archtool injects UserRepo here</span>

    <span class="kw">def</span> <span class="fn">get_name</span>(self) -> str:
        <span class="kw">return</span> self.repo.find_all()[<span class="nb">0</span>]


<span class="cm"># entrypoints/run.py</span>

injector = <span class="cn">DependencyInjector</span>(
    modules_list=[<span class="cn">AppModule</span>(<span class="st">"app.users"</span>)],
    project_root=<span class="cn">Path</span>(__file__).parent.parent,
)
injector.inject()

svc = injector.get_dependency(<span class="cn">UserServiceABC</span>)
<span class="kw">print</span>(svc.get_name())  <span class="cm"># → "alice"</span></pre></div>

      <div class="pg-pane" id="pg-pane-multi"><pre class="pg-pre"><span class="cm"># app/orders/services.py</span>

<span class="kw">from</span> app.users.interfaces <span class="kw">import</span> <span class="cn">UserServiceABC</span>  <span class="cm"># cross-module</span>
<span class="kw">from</span> .interfaces <span class="kw">import</span> <span class="cn">OrderServiceABC</span>, <span class="cn">OrderRepoABC</span>

<span class="kw">class</span> <span class="cn">OrderService</span>(<span class="cn">OrderServiceABC</span>):
    <span class="nb">repo</span>:     <span class="an hl">OrderRepoABC</span>
    <span class="nb">user_svc</span>: <span class="an hl">UserServiceABC</span>  <span class="cm"># ← wired from app.users automatically</span>

    <span class="kw">def</span> <span class="fn">place</span>(self, user_id: int, items: list) -> dict:
        user = self.user_svc.get_name()
        <span class="kw">return</span> {<span class="st">"user"</span>: user, <span class="st">"items"</span>: items, <span class="st">"status"</span>: <span class="st">"placed"</span>}


<span class="cm"># entrypoints/run.py</span>

injector = <span class="cn">DependencyInjector</span>(
    modules_list=[
        <span class="cn">AppModule</span>(<span class="st">"app.users"</span>),
        <span class="cn">AppModule</span>(<span class="st">"app.orders"</span>),  <span class="cm"># cross-module dep resolved</span>
    ],
    project_root=ROOT,
)
injector.inject()</pre></div>

      <div class="pg-pane" id="pg-pane-layer"><pre class="pg-pre"><span class="cm"># app/fraud/services.py  ←  Domain layer</span>

<span class="kw">from</span> .interfaces <span class="kw">import</span> <span class="cn">FraudServiceABC</span>, <span class="cn">FraudControllerABC</span>

<span class="kw">class</span> <span class="cn">FraudService</span>(<span class="cn">FraudServiceABC</span>):
    <span class="cm"># Domain depending on Application layer — violation!</span>
    <span class="nb">controller</span>: <span class="an hl">FraudControllerABC</span>


<span class="cm"># entrypoints/run.py</span>

injector = <span class="cn">DependencyInjector</span>(
    modules_list=[<span class="cn">AppModule</span>(<span class="st">"app.fraud"</span>)],
    layers=default_layers,          <span class="cm"># enforcement enabled</span>
    project_root=ROOT,
)
injector.inject()  <span class="cm"># ← raises here, not at 3 AM in production</span></pre></div>

    </div>
    <div class="pg-terminal">
      <div class="pg-terminal-bar">
        <span class="pg-terminal-title">output</span>
        <button class="pg-run" id="pg-run">▶ Run</button>
      </div>
      <div class="pg-output" id="pg-output">
        <div class="pg-hint">Click ▶ Run to execute</div>
      </div>
    </div>
  </div>
</div>

---

## Install

```bash
pip install archtool
```

Supports Python **3.10 · 3.11 · 3.12 · 3.13**.

---

## Five-minute start

→ **[Quickstart](guide/quickstart.md)** — working project from scratch.

→ **[Why archtool?](why.md)** — the full problem statement and how we address it.

→ **[How it works](guide/concepts.md)** — the two-pass injection algorithm explained.

---

<div class="archtool-page-footer">
  <div class="archtool-page-footer-col">
    <strong>archtool</strong>
    <a href="https://github.com/0nliner/archtool">GitHub</a>
    <a href="https://pypi.org/project/archtool">PyPI</a>
    <a href="https://github.com/sponsors/0nliner">♥ Sponsor</a>
  </div>
  <div class="archtool-page-footer-col">
    <strong>Ecosystem</strong>
    <a href="https://github.com/0nliner/web_fractal">web_fractal — FastAPI + SQLAlchemy kit</a>
    <a href="https://github.com/0nliner/fractal_chunks">fractal_chunks — reusable modules <em>(coming soon)</em></a>
  </div>
  <div class="archtool-page-footer-col">
    <strong>Contact</strong>
    <a href="mailto:aleksandrchudaikindev@gmail.com">aleksandrchudaikindev@gmail.com</a>
    <a href="https://github.com/0nliner" target="_blank">Бюро автоматизации процессов</a>
  </div>
</div>
