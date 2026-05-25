# CLI reference

archtool ships with a CLI for scaffolding and inspecting projects.

```
archtool [OPTIONS] COMMAND [ARGS]...
```

---

## `archtool init`

Scaffold a new project.

```bash
archtool init <project-name>
```

Creates a complete project layout with:

- Domain module (`app/<project-name>/`)
- Entrypoint without sys.path hacks (`entrypoints/run.py`)
- Assembly test (`tests/test_assembly.py`)
- `Makefile` with common tasks
- `Dockerfile`
- `pyproject.toml`

**Example:**

```bash
archtool init myapp
cd myapp
pip install -e ".[dev]"
make test
```

---

## `archtool add-module`

Add a domain module to an existing project.

```bash
archtool add-module <module-name>
```

Creates `app/<module-name>/` with `interfaces.py`, `services.py`, `repos.py` stubs, and a matching `tests/` directory. Prints a reminder to register the module in your `APPS` list.

**Example:**

```bash
archtool add-module payments
```

---

## `archtool validate`

Validate that all registered modules follow the expected structure.

```bash
archtool validate
```

Checks each module for:

- Presence of `interfaces.py`
- Module importability

Displays results in a rich table. Exit code 0 = all OK, 1 = problems found.

---

## `archtool graph`

Print the dependency graph for the project.

```bash
archtool graph [--format tree|dot]
```

**Tree format** (default): rich tree in the terminal.

**Dot format**: GraphViz-compatible output for rendering:

```bash
archtool graph --format dot | dot -Tpng -o deps.png
```

---

## Verbose logging

Enable DI assembly logs without code changes:

```bash
ARCHTOOL_VERBOSE=1 python entrypoints/run.py
```

Or pass `verbose=True` to `DependencyInjector`:

```python
DependencyInjector(modules_list=[...], verbose=True)
```
