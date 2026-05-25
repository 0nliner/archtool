# Установка

## Требования

- Python 3.10 или выше

## pip

```bash
pip install archtool
```

## В виртуальном окружении (рекомендуется)

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install archtool
```

## Проверка

```bash
archtool --version
```

---

## Установка для разработки

Для контрибьютинга или локального запуска тестов:

```bash
git clone https://github.com/0nliner/archtool
cd archtool
pip install -e ".[dev]"
make test
```
