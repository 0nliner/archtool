# Справочник CLI

archtool поставляется с CLI для скаффолдинга и инспекции проектов.

```
archtool [OPTIONS] COMMAND [ARGS]...
```

---

## `archtool init`

Создать каркас нового проекта.

```bash
archtool init <project-name>
```

Создаёт полную структуру проекта:

- Доменный модуль (`app/<project-name>/`)
- Точку входа без sys.path-хаков (`entrypoints/run.py`)
- Тест сборки (`tests/test_assembly.py`)
- `Makefile` с типовыми командами
- `Dockerfile`
- `pyproject.toml`

**Пример:**

```bash
archtool init myapp
cd myapp
pip install -e ".[dev]"
make test
```

---

## `archtool add-module`

Добавить доменный модуль в существующий проект.

```bash
archtool add-module <module-name>
```

Создаёт `app/<module-name>/` с заглушками `interfaces.py`, `services.py`, `repos.py` и директорией `tests/`. Выводит напоминание зарегистрировать модуль в списке `APPS`.

**Пример:**

```bash
archtool add-module payments
```

---

## `archtool validate`

Проверить, что все зарегистрированные модули соответствуют ожидаемой структуре.

```bash
archtool validate
```

Для каждого модуля проверяет:

- Наличие `interfaces.py`
- Импортируемость модуля

Выводит результат в виде rich-таблицы. Код выхода 0 = всё ОК, 1 = найдены проблемы.

---

## `archtool graph`

Вывести граф зависимостей проекта.

```bash
archtool graph [--format tree|dot]
```

**Формат tree** (по умолчанию): rich-дерево в терминале.

**Формат dot**: вывод, совместимый с GraphViz:

```bash
archtool graph --format dot | dot -Tpng -o deps.png
```

---

## Подробное логирование

Включить логи сборки DI без изменения кода:

```bash
ARCHTOOL_VERBOSE=1 python entrypoints/run.py
```

Или передать `verbose=True` в `DependencyInjector`:

```python
DependencyInjector(modules_list=[...], verbose=True)
```
