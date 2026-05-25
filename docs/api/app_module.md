# AppModule

A descriptor for a single bounded-context module registered with archtool.

```python
from archtool.global_types import AppModule
```

---

## Constructor

```python
AppModule(
    import_path: str,
    ignore: list[ComponentPattern] = [],
)
```

| Parameter | Type | Default | Description |
|---|---|---|---|
| `import_path` | `str` | required | Dotted Python import path relative to the project root (e.g. `"app.users"` or `"app.payments.gateway"`). |
| `ignore` | `list[ComponentPattern]` | `[]` | Layer component patterns to skip for this module. Useful if a module implements only some layers (e.g. no `controllers.py`). |

---

## Usage

### Basic registration

```python
injector = DependencyInjector(
    modules_list=[
        AppModule("app.users"),
        AppModule("app.orders"),
        AppModule("app.payments"),
    ],
    project_root=ROOT,
)
```

### Nested modules

archtool supports arbitrarily deep module paths. A class defined in `app.core.gateway.repos` is still discovered when the module is `app.core.gateway`:

```python
AppModule("app.core.gateway")   # discovers app/core/gateway/repos.py, services.py, etc.
```

### Ignoring a layer for a specific module

If a module doesn't have controllers (e.g. a pure domain module), tell archtool to skip that layer:

```python
from archtool.layers.default_layers import ApplicationLayer

AppModule("app.core", ignore=[ApplicationLayer.Components.controllers])
```

---

## Methods

### `validate() -> list[str]`

Check that the module exists and has `interfaces.py`. Returns a list of problem strings — empty means valid.

Used by `archtool validate` CLI command.

```python
module = AppModule("app.users")
problems = module.validate()
if problems:
    for p in problems:
        print("ERROR:", p)
```

---

## Auto-generated reference

::: archtool.global_types.AppModule
    options:
      show_source: false
