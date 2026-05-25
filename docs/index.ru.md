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
      Собирается как Lego.<br>
      Работает как молоток.<br>
      Держит как фундамент.
    </div>
  </div>
</div>

<p class="archtool-credit"><span class="archtool-credit-label">разработано</span><span class="archtool-credit-sep">·</span><a class="archtool-credit-name" href="https://github.com/0nliner" target="_blank">Чудайкин Александр</a><span class="archtool-credit-sep">·</span><a class="archtool-credit-org" href="https://github.com/0nliner" target="_blank">Бюро автоматизации процессов</a></p>

<p align="center">
  <a href="https://pypi.org/project/archtool"><img alt="PyPI" src="https://img.shields.io/pypi/v/archtool?color=3e9454"></a>
  <a href="https://github.com/0nliner/archtool/actions/workflows/ci.yml"><img alt="CI" src="https://github.com/0nliner/archtool/actions/workflows/ci.yml/badge.svg"></a>
  <a href="https://pypi.org/project/archtool"><img alt="Python" src="https://img.shields.io/pypi/pyversions/archtool?color=3e9454"></a>
  <a href="https://github.com/0nliner/archtool/blob/main/LICENSE"><img alt="MIT" src="https://img.shields.io/badge/license-MIT-3e9454"></a>
  <a href="https://codecov.io/gh/0nliner/archtool"><img alt="Coverage" src="https://img.shields.io/badge/coverage-coming%20soon-3e9454"></a>
  <a href="https://github.com/sponsors/0nliner"><img alt="Sponsor" src="https://img.shields.io/badge/sponsor-♥-ea4aaa"></a>
</p>

---

## Кто ты?

=== "Tech Lead"

    Команда растёт. Каждый сервис подключён по-своему. Новый разработчик изобретает колесо заново. Архитектурная документация давно не совпадает с кодом.

    archtool даёт всей команде **один стандарт**: объявляй интерфейс, пиши реализацию, archtool подключит сам. Нарушения слоёв ловятся при старте — не на разборе инцидента в три ночи. Архитектура становится чем-то, что можно проверить, а не просто задокументировать.

=== "Стартапер"

    Ты шипишь быстро. Но каждый срезанный угол в фундаменте обходится вдвое дороже на масштабе.

    archtool берёт на себя бойлерплейт — ты фокусируешься на продукте. Добавил модуль, зарегистрировал, готово. Архитектура растёт вместе с командой — никакого переписывания на десятом разработчике.

    → **fractal_chunks** *(в разработке)* — проверенные боем модули для auth, users, платежей, уведомлений. Подключаешь нужное; пропускаешь лишнее.

=== "Вайбкодер"

    Ты генерируешь код быстрее, чем интегрируешь его. Узкое место — разводка.

    archtool убирает этот шаг. ИИ пишет сервис, ты объявляешь интерфейс — archtool подключает всё при старте. Никакого бойлерплейта. Никаких цепочек импортов.

    → **fractal_chunks** *(в разработке)* — растущий каталог production-модулей, каждый как кубик Lego. Добавь `users`, `auth-jwt`, `notifications` в новый проект за минуты, а не дни.

=== "Архитектор"

    Ты уже чистил чужие service-locator'ы. Ты знаешь, что бывает, когда DI неформальный.

    archtool делает правильные паттерны единственным путём. Интерфейсы — единственный контракт. Реализации обнаруживаются, не регистрируются. Нарушения слоёв падают быстро при старте. Clean Architecture — без лишних церемоний.

---

## Проблема, которую рано или поздно встречает каждый Python-проект

Начинаешь чисто. Один сервис, один репозиторий, может быть контроллер. Проект растёт.

Где-то на пятом модуле появляется это:

```python
# entrypoints/run.py — кладбище благих намерений
import sys
sys.path.insert(0, "..")   # ← зачем это вообще здесь?

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
user_service.repo = user_repo                          # ← не забыть это
order_service = OrderService()
order_service.repo = order_repo
order_service.user_service = user_service              # ← и это
payment_service = PaymentService()
payment_service.repo = payment_repo
payment_service.order_service = order_service          # ← и это
notification_service = NotificationService()
notification_service.payment_service = payment_service # ← и это
# ... ещё 40 строк ...
```

Именно это archtool заменяет — полностью.

---

## Решение

```python
# entrypoints/run.py с archtool
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

archtool сканирует твои модули, обнаруживает каждую пару интерфейс–реализация, инстанциирует их в порядке зависимостей и связывает всё вместе. Никакого бойлерплейта регистрации. Никаких `sys.path`-хаков. Никаких скрытых багов проводки.

---

## Что ты получаешь

=== "Автоматическая разводка"

    Объяви зависимость как аннотацию класса на конкретном классе. archtool прочитает её и вызовет `setattr` при сборке.

    ```python
    # services.py
    class OrderService(OrderServiceABC):
        repo: OrderRepoABC             # archtool установит это
        user_service: UserServiceABC   # и это

        def place(self, items: list) -> None:
            user = self.user_service.get_current()
            self.repo.save({"user": user, "items": items})
    ```

=== "Контроль архитектуры"

    Нарушения границ слоёв — сервис импортирует напрямую из репо, контроллер лезет во внутренности домена — выявляются **при старте**, а не в продакшене в 3 ночи.

    ```python
    injector = DependencyInjector(
        modules_list=[...],
        layers=[InfrastructureLayer, DomainLayer, ApplicationLayer],
    )
    injector.inject()  # бросает TopLevelLayerUsingException при нарушении
    ```

=== "Кастомные слои"

    Встроенные слои следуют Clean Architecture. Но ты определяешь свои:

    ```python
    class IntegrationsLayer(Layer):
        depends_on = InfrastructureLayer
        class Components:
            clients = ComponentPattern("clients", superclass=ABCClient)
    ```

    Любое имя файла, любой базовый класс — archtool адаптируется к твоей архитектуре, а не наоборот.

=== "SOLID из коробки"

    - **S** — каждый `AppModule` владеет одним ограниченным контекстом
    - **O** — добавляешь модуль, ничего больше не меняется
    - **L** — заменяешь репо на заглушку, потребители не знают об этом
    - **I** — интерфейсы остаются минимальными и сфокусированными
    - **D** — всё зависит от абстракций, никогда от конкреций

---

## Посмотри как работает

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
    <span class="nb">repo</span>: <span class="an hl">UserRepoABC</span>  <span class="cm"># ← archtool подставит UserRepo сюда</span>

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

<span class="kw">from</span> app.users.interfaces <span class="kw">import</span> <span class="cn">UserServiceABC</span>  <span class="cm"># кросс-модульная зависимость</span>
<span class="kw">from</span> .interfaces <span class="kw">import</span> <span class="cn">OrderServiceABC</span>, <span class="cn">OrderRepoABC</span>

<span class="kw">class</span> <span class="cn">OrderService</span>(<span class="cn">OrderServiceABC</span>):
    <span class="nb">repo</span>:     <span class="an hl">OrderRepoABC</span>
    <span class="nb">user_svc</span>: <span class="an hl">UserServiceABC</span>  <span class="cm"># ← подтянется из app.users автоматически</span>

    <span class="kw">def</span> <span class="fn">place</span>(self, user_id: int, items: list) -> dict:
        user = self.user_svc.get_name()
        <span class="kw">return</span> {<span class="st">"user"</span>: user, <span class="st">"items"</span>: items, <span class="st">"status"</span>: <span class="st">"placed"</span>}


<span class="cm"># entrypoints/run.py</span>

injector = <span class="cn">DependencyInjector</span>(
    modules_list=[
        <span class="cn">AppModule</span>(<span class="st">"app.users"</span>),
        <span class="cn">AppModule</span>(<span class="st">"app.orders"</span>),  <span class="cm"># кросс-модульная зависимость резолвится</span>
    ],
    project_root=ROOT,
)
injector.inject()</pre></div>

      <div class="pg-pane" id="pg-pane-layer"><pre class="pg-pre"><span class="cm"># app/fraud/services.py  ←  Domain layer</span>

<span class="kw">from</span> .interfaces <span class="kw">import</span> <span class="cn">FraudServiceABC</span>, <span class="cn">FraudControllerABC</span>

<span class="kw">class</span> <span class="cn">FraudService</span>(<span class="cn">FraudServiceABC</span>):
    <span class="cm"># Domain зависит от Application — нарушение!</span>
    <span class="nb">controller</span>: <span class="an hl">FraudControllerABC</span>


<span class="cm"># entrypoints/run.py</span>

injector = <span class="cn">DependencyInjector</span>(
    modules_list=[<span class="cn">AppModule</span>(<span class="st">"app.fraud"</span>)],
    layers=default_layers,          <span class="cm"># контроль слоёв включён</span>
    project_root=ROOT,
)
injector.inject()  <span class="cm"># ← падает здесь, а не в 3 ночи в проде</span></pre></div>

    </div>
    <div class="pg-terminal">
      <div class="pg-terminal-bar">
        <span class="pg-terminal-title">output</span>
        <button class="pg-run" id="pg-run">▶ Run</button>
      </div>
      <div class="pg-output" id="pg-output">
        <div class="pg-hint">Нажми ▶ Run чтобы запустить</div>
      </div>
    </div>
  </div>
</div>

---

## Установка

```bash
pip install archtool
```

Поддерживается Python **3.10 · 3.11 · 3.12 · 3.13**.

---

## Старт за пять минут

→ **[Быстрый старт](guide/quickstart.md)** — рабочий проект с нуля.

→ **[Зачем archtool?](why.md)** — полное описание проблемы и как мы её решаем.

→ **[Как это работает](guide/concepts.md)** — алгоритм двухпроходной инъекции объяснён.

---

<div class="archtool-page-footer">
  <div class="archtool-page-footer-col">
    <strong>archtool</strong>
    <a href="https://github.com/0nliner/archtool">GitHub</a>
    <a href="https://pypi.org/project/archtool">PyPI</a>
    <a href="https://github.com/sponsors/0nliner">♥ Поддержать</a>
  </div>
  <div class="archtool-page-footer-col">
    <strong>Экосистема</strong>
    <a href="https://github.com/0nliner/web_fractal">web_fractal — FastAPI + SQLAlchemy</a>
    <a href="https://github.com/0nliner/fractal_chunks">fractal_chunks — готовые модули <em>(скоро)</em></a>
  </div>
  <div class="archtool-page-footer-col">
    <strong>Контакты</strong>
    <a href="mailto:aleksandrchudaikindev@gmail.com">aleksandrchudaikindev@gmail.com</a>
    <a href="https://github.com/0nliner" target="_blank">Бюро автоматизации процессов</a>
  </div>
</div>
