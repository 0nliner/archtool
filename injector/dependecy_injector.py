from typing import List, Dict

from .exceptions import (DependecyDuplicate,
                         DependecyDoesNotRegistred
                         )

from .interfaces import (DependecyInjectorInterface,
                         LayerInterface
                         )

from injector.layers.default_layers import default_layers
from injector.layers import Layer
from injector.global_types import (AppModules,
                                   ContainerT,
                                   DEPENDENCY_KEY)

from injector.utils import (get_dependencies,
                            serialize_dep_key,
                            get_all_interfaces_and_realizations)


# TODO: нахерачить документацию по тому как этим пользоваться
# TODO: валидации:
#       однонаправленность импортов

class DependecyInjector(DependecyInjectorInterface):
    def __init__(self,
                 modules_list: AppModules,
                 layers: List[LayerInterface] = None):

        self.modules_list = modules_list
        self.layers = layers if layers else default_layers
        # инициализируем классы слоёв
        # TODO: позже нужно вынести инициализацию.
        #       Это должен делать пользователь
        self.layers = [layer() for layer in self.layers]
        self._dependencies: Dict[DEPENDENCY_KEY, object] = {}

    def inject(self):
        for layer in self.layers:
            if issubclass(type(layer), Layer):
                # TODO: сделать аннотирование на components
                # TODO: добавить __iter__ на Components класс
                for component_group in layer.component_groups:
                    component_group_deps = get_all_interfaces_and_realizations(
                        app_modules=self.modules_list,
                        name_pattern=component_group.module_name_regex,
                        superclass=component_group.superclass)

                    # добавляем зависимости слоя в глобальные зависимости
                    for dep_key, dep_class in component_group_deps.items():
                        # инициализируем классы, подставляем как зависимость
                        dep_instance = dep_class()
                        self._reg_dependecy(key=dep_key,
                                            value=dep_instance)

        # инжектим
        for dep_interface, dep_instance in self._dependencies.items():
            self._inject_dependencies(container=dep_instance)

    def _inject_dependencies(self, container: ContainerT) -> None:
        """
        Внедряет зависимости

        ARGS:
        container - объект, в который встраиваем зависимости
        """
        deps = get_dependencies(container=container)
        for dep in deps:
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
