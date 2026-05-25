# Installation

## Requirements

- Python 3.10 or higher

## pip

```bash
pip install archtool
```

## In a virtual environment (recommended)

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install archtool
```

## Verify

```bash
archtool --version
```

---

## Development install

If you want to contribute or run the tests locally:

```bash
git clone https://github.com/0nliner/archtool
cd archtool
pip install -e ".[dev]"
make test
```
