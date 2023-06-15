# DEV

1. Добавить библиотеку в PYTHONPATH
```
export PYTHONPATH="${PYTHONPATH}:путь до injector"
```

2. Поставить зависимости
```
python3.10 -m virtualenv venv
source venv/bin/activate
pip install -r dev_requirements.txt
```

3. Собрать пакет 
```
python -m build
```
