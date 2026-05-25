# Слои

archtool может принудительно применять **границы слоёв** — предотвращая импорт из более высоких слоёв в более низкие.

## Встроенные слои

| Слой | Сканируемый файл | Маркер | Зависит от |
|---|---|---|---|
| `InfrastructureLayer` | `repos.py` | `ABCRepo` | нет |
| `DomainLayer` | `services.py` | `ABCService` | InfrastructureLayer |
| `ApplicationLayer` | `controllers.py` | `ABCController` | DomainLayer |
| `PresentationLayer` | `views.py` | `ABCView` | ApplicationLayer |

## Использование слоёв

```python
from archtool.dependency_injector import DependencyInjector
from archtool.global_types import AppModule
from archtool.layers.default_layers import DomainLayer, InfrastructureLayer

injector = DependencyInjector(
    modules_list=[AppModule("app.users")],
    layers=[InfrastructureLayer, DomainLayer],
)
injector.inject()
```

Если не передать `layers`, используются все четыре стандартных слоя.

Если какой-либо класс нарушает правила слоёв, archtool бросает `TopLevelLayerUsingException` при сборке — не в рантайме когда нарушение превращается в загадочный `ImportError`.

## Кастомные слои

Унаследуйся от `Layer` чтобы определить собственную иерархию:

```python
from archtool.layers.di_basic_layer import Layer
from archtool.components.default_component import ComponentPattern
from archtool.layers.default_layer_interfaces import ABCService


class MyBusinessLayer(Layer):
    depends_on = None

    class Components:
        services = ComponentPattern(
            module_name_regex="services",
            superclass=ABCService,
        )
```

Каждый кастомный слой обязан:
- Объявить `depends_on` (другой слой или `None`)
- Иметь вложенный класс `Components` с хотя бы одним `ComponentPattern`

## Игнорирование компонентов для конкретного модуля

Иногда один модуль не следует стандартной структуре. Используй `ignore`:

```python
from archtool.layers.default_layers import InfrastructureLayer

AppModule(
    "app.notifications",
    ignore=[InfrastructureLayer.Components.repos],
)
```

archtool пропустит сканирование `repos.py` для этого модуля.
