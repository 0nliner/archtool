# Layers

archtool can enforce **layer boundaries** across your modules, preventing lower-level layers from importing higher-level ones.

## Built-in layers

```python
from archtool.layers.default_layers import DomainLayer, ApplicationLayer, InfrastructureLayer
```

| Layer | Allowed to import from |
|---|---|
| `InfrastructureLayer` | `ApplicationLayer`, `DomainLayer` |
| `ApplicationLayer` | `DomainLayer` |
| `DomainLayer` | nothing above itself |

## Wiring with layers

```python
from archtool.dependency_injector import DependencyInjector
from archtool.global_types import AppModule
from archtool.layers.default_layers import DomainLayer

injector = DependencyInjector(
    modules_list=[AppModule("app.users")],
    layers=[DomainLayer],
)
injector.inject()
```

If any module violates the layer rules, archtool raises `TopLevelLayerUsingException` at assembly time — not at runtime when the bug causes an obscure traceback.

## Custom layers

Subclass `Layer` to define your own hierarchy:

```python
from archtool.interfaces.layer import Layer

class PresentationLayer(Layer):
    ...

class BusinessLayer(Layer):
    forbidden = [PresentationLayer]   # business must not import presentation
```
