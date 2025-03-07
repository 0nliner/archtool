![Frame 3(2)](https://github.com/user-attachments/assets/df1e1811-1dc9-4c73-8115-632487401af9)
# archtool documentation

## 🛠 Development Environment Setup

**Преимущества**:
✅ **Dependency Injection** - управление зависимостями между компонентами  
✅ **Контроль слоёв** - гарантия однонаправленных импортов  
✅ **ISP Compliance** - принудительное разделение интерфейсов  
✅ **Мультиархитектура** - поддержка Clean Architecture, ETL, микросервисов
✅ Чёткое разделение между API эндпоинтами и бизнес-логикой
✅ Автоматическая валидация зависимостей
✅ Поддержка async/await
✅ Интеграция с django и fast-api

---
## Установка
```bash
pip install archtool
```

---

## 🌐 Framework Integration
### Django Support
archtool помогает организовать Django-проекты в соответствии с Clean Architecture, упрощая:
- Постепенный переход от монолитной структуры
- Вынос бизнес-логики из views/forms
- Интеграцию с современными решениями (FastAPI, AIOHTTP)

**Пример структуры**:
```
myproject/
├── archtool_bundle/            # django app, отвечающий за совместимость с archtool 
│   ├── interfaces.py
│   ├── controllers.py
│   ├── services.py
│   └── repos.py
├── app2/
│   ├── interfaces.py
│   ├── controllers.py
│   ├── services.py
│   └── repos.py
├── entrypoints/                  # точки входа в приложение
│   └── fastapi_app.py
```

**Интеграция**:
документация в активной разработке 


### FastAPI Integration
Создавайте хорошо структурированные API с автоматическим DI:
Документация в активной разработке

---

## 📚 Examples

| Example Type       | Description                     |
|--------------------|---------------------------------|
| Django Migration   | `examples/django_migration/`   |
| FastAPI Microservice| `examples/fastapi_service/`    |
```



### Архитектурные слои
```python
# Clean Architecture (по Роберту Мартину)
class InfrastructureLayer(Layer):
    """Работа с БД, внешние API"""
    depends_on = None
    
    class Components:
        repos = ComponentPattern(
            module_name_regex="repos",
            superclass=ABCRepo
        )

class DomainLayer(Layer):
    """Ядро системы: модели и бизнес-логика"""
    depends_on = InfrastructureLayer
    
    class Components:
        services = ComponentPattern(
            module_name_regex="services",
            superclass=ABCService
        )

class ApplicationLayer(Layer):
    """Оркестрация workflow"""
    depends_on = DomainLayer
    
    class Components:
        controllers = ComponentPattern(
            module_name_regex="controllers",
            superclass=ABCController
        )

class PresentationLayer(Layer):
    """API и пользовательские интерфейсы"""
    depends_on = ApplicationLayer
    
    class Components:
        views = ComponentPattern(
            module_name_regex="views",
            superclass=ABCView
        )
```

---

### Преимущества подхода
1. **Снижение связанности**  
   Изоляция слоёв через strict import rules (DIP)

2. **Тестируемость**  
   Легкое мокирование через DI-контейнер

3. **Гибкость архитектуры**  
   Кастомные слои для любых сценариев

4. **Валидация**  
   Автоматическая проверка правил импортов

5. **Документирование**  
   Явная структура проекта = живая документация
