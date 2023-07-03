# DEV настройка среды

1. Добавить библиотеку в PYTHONPATH
``` bash
export PYTHONPATH="${PYTHONPATH}:путь до archtool"
```
2. Поставить зависимости
``` bash
python3.10 -m virtualenv venv
source venv/bin/activate
pip install -r dev_requirements.txt
```
3. Собрать пакет 
``` bash
make sdist
```

</br>
</br>

# Установка
</br>

```
pip install archtool
```


</br></br>
# Введение в библиотеку archtool


### Фичи
* Реализует паттерн Dependency Injection
* Следит за тем, чтобы импорт в рамках слоёв был однонаправленным
* Обязывает разработчиков соблюдать принцип сегрегации интерфейсов




</br>

### Примеры
* Пример монолита
* Пример микросервиса
* Пример ETL приложения
* Пример бота

</br>

### Что такое слой
Разделение приложения на слои позволяет достичь более высокой степени модульности и улучшить его поддержку, расширяемость и добиться низкой связанности в коде. Каждый слой выполняет определенную функцию и имеет свои собственные интерфейсы, что упрощает работу над отдельными компонентами приложения и позволяет изменять их без влияния на другие части системы. 





Библиотека предоставляет вам стандартные слои и интерфейсы в соответствии с чистой архитектурой Мартина Фаулера.



```python

class InfrastructureLayer(Layer):
    """
    Слой инфраструктуры
    """
    depends_on = None


    class Components:
        repos = ComponentPattern(module_name_regex="repos",
                                 superclass=ABCRepo)


class DomainLayer(Layer):
    """
    Слой бизнеслогики
    """
    depends_on = InfrastructureLayer


    class Components:
        services = ComponentPattern(module_name_regex="services",
                                    superclass=ABCService)


class ApplicationLayer(Layer):
    """
    Слой приложения
    """
    depends_on = DomainLayer


    class Components:
        controllers = ComponentPattern(module_name_regex="controllers",
                                       superclass=ABCController)


class PresentationLayer(Layer):
    """
    Слой отображения
    """
    depends_on = ApplicationLayer or DomainLayer


    class Components:
        views = ComponentPattern(module_name_regex="views",
                                 superclass=ABCView)

```

В данном случае определяются 4 слоя:

* Infrastructure
* Domain
* Application (необязательный слой)
* Presentation


Библиотека не ограничивает вас только чистой архитектурой, к примеру вы можете реализовать ETL архитектуру



#### Преимущества использования слоёв


* Уменьшает связанность между компонентами системы
* Способствует повышению безопасности приложения, поскольку каждый слой может иметь свои собственные механизмы защиты.
* Упрощает тестируемость, за счёт возможности изолированно тестировать логику.
* Повышает читаемость и простоту написания кода, методы становятся меньше по объёму, т.к логика разделена.
* Способствует соблюдению принципа DRY за счёт чёткой структуры приложения

