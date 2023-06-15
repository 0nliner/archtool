from typing import List, Dict

from .exceptions import (DependecyDuplicate,
                         DependecyDoesNotRegistred
                         )

from .interfaces import (DependecyInjectorInterface,
                         LayerInterface,
                         DILayerInterface
                         )

from global_types import (AppModules,
                          ContainerT,
                          DEPENDENCY_KEY)

from utils import (get_dependencies,
                   serialize_dep_key)


# TODO: нахерачить документацию по тому как этим пользоваться


class DependecyInjector(DependecyInjectorInterface):
    def __init__(self,
                 modules_list: AppModules,
                 layers: List[LayerInterface]):

        self.modules_list = modules_list
        # TODO: при итерации слоёв, зависимость однонаправлена снизу вверх
        self.layers = layers
        self._dependencies: Dict[DEPENDENCY_KEY, object] = {}

    def inject(self):
        # TODO: проходимся по всем di слоям
        for layer in self.layers:
            if issubclass(type(layer), DILayerInterface):
                layer_deps = layer.get_all_interfaces_and_realizations(
                    app_modules=self.modules_list)

                # добавляем зависимости слоя в глобальные зависимости
                for dep_key, dep_class in layer_deps.items():
                    # инициализируем классы, подставляем как зависимость
                    dep_instance = dep_class()
                    self._reg_dependecy(key=dep_key,
                                        value=dep_instance)

        # инжектим
        for dep_interface, dep_instance in self._dependencies.items():
            self._inject_dependencies(container=dep_instance)

        # TODO: убрать при добавлении функционала слоёв
        # инжектим ссылку на инстанс инжектора во вьюхи
        # сейчас это нужно в рамках рефакторинга существующего легаси
        # for view in self.views:
            # view.injector = self

    def _inject_dependencies(self, container: ContainerT) -> None:
        """
        Внедряет зависимости

        ARGS:
        container - объект, в который встраиваем зависимости
        """
        deps = get_dependencies(container=container)
        for dep in deps:
            # TODO: проверки на уровни лучше выделить в отдельный метод
            # валидации
            # is_using_service_from_repo =\
            #       all([type(container) is RepositoryInterface,
            #            type(dep.asked) is ServiceInterface])

            # if is_using_service_from_repo:
            #     raise TopLevelLayerUsingException((f"{container:}\n",
            #                                        f"{dep:}"))

            # пытаемся найти зависимость
            try:
                dependency_to_inject = self.get_dependency(key=dep.asked)
                setattr(container, dep.name, dependency_to_inject)
            except KeyError:
                raise DependecyDoesNotRegistred(("Данная зависимость не",
                                                 " зарегистрирована в",
                                                 " инжекторе"))

    def _reg_dependecy(self,
                       key: DEPENDENCY_KEY,
                       value: object) -> None:
        """
        Проверяет существует ли зависимость.
        Если зависимости уже существует - возвращает ошибку DependecyDuplicate

        ARGS:
        key - ключ зависимости
        value - объект зависимости
        """
        serialized_key = serialize_dep_key(key)
        if serialized_key in self._dependencies:
            raise DependecyDuplicate(("Интерфейс зависимости должен быть",
                                      " уникальным.\n Зависимость с ключём",
                                      f" {key} уже зарегистрирована"))
        self._dependencies[serialized_key] = value

    def get_dependency(self,
                       key: str) -> object:
        try:
            instance = self._dependencies[key]
            return instance
        except KeyError:
            raise DependecyDoesNotRegistred(
                f'Зависимость не найдена {key:}')
