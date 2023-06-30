# DEV настройка среды

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
make sdist
```

</br>
</br>
</br>
</br>

# Установка injector
Пока injector лежит в приватной репе и отсутствует в pypi, так что ставим его ручками
Актуальный релиз на момент коммита с README 0.1.3.
</br>
</br>
[ссылка на скачивание injector](https://github.com/0nliner/injector/archive/refs/tags/0.1.3.tar.gz)
</br></br>
Перетащите архив в папку с проектом и установите:

```
pip install ./injector-0.1.3.tar.gz
```

Вы успешно установили библиотеку
</br>
</br>
