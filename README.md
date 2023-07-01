# DEV настройка среды

1. Добавить библиотеку в PYTHONPATH
```
export PYTHONPATH="${PYTHONPATH}:путь до archtool"
```
2. Поставить зависимости
```
python3.10 -m virtualenv venv
source venv/bin/activate
pip install -r dev_requirements.txt
```
3. Собрать пакет 
```
make sdist
```

</br>
</br>

# Установка
</br>

```
pip install archtool
```