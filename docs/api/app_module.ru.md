# AppModule

Дескриптор одного модуля ограниченного контекста, регистрируемого в archtool.

```python
from archtool.global_types import AppModule
```

---

## Конструктор

```python
AppModule(
    import_path: str,
    ignore: list[ComponentPattern] = [],
)
```

| Параметр | Тип | Значение по умолчанию | Описание |
|---|---|---|---|
| `import_path` | `str` | обязательный | Dotted-путь Python-импорта относительно корня проекта (например `"app.users"` или `"app.payments.gateway"`). |
| `ignore` | `list[ComponentPattern]` | `[]` | Паттерны компонентов слоёв, которые нужно пропустить для этого модуля. Полезно, когда модуль реализует только часть слоёв (например нет `controllers.py`). |

---

## Использование

### Базовая регистрация

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

### Вложенные модули

archtool поддерживает произвольно глубокие пути. Класс, определённый в `app.core.gateway.repos`, будет найден при модуле `app.core.gateway`:

```python
AppModule("app.core.gateway")   # найдёт app/core/gateway/repos.py, services.py и т.д.
```

### Игнорирование слоя для конкретного модуля

Если у модуля нет контроллеров (например, чистый доменный модуль), укажите archtool пропустить этот слой:

```python
from archtool.layers.default_layers import ApplicationLayer

AppModule("app.core", ignore=[ApplicationLayer.Components.controllers])
```

---

## Методы

### `validate() -> list[str]`

Проверяет, что модуль существует и содержит `interfaces.py`. Возвращает список строк с проблемами — пустой список означает валидный модуль.

Используется командой CLI `archtool validate`.

```python
module = AppModule("app.users")
problems = module.validate()
if problems:
    for p in problems:
        print("ОШИБКА:", p)
```
