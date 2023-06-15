from abc import ABCMeta
import sys
from inspect import isclass, isabstract, getfile, getmro
from importlib import import_module
from typing import List, Callable
from functools import singledispatch
from re import sub

from pathlib import Path
from bundler.exceptions import CheckFailedException
from global_types import (
        Dependecy,
        ContainerT,
        DependeciesT,
        AppModule,
        DEPENDENCY_KEY)


def string_to_snake_case(string: str):
    """
    Переводит любую строку в snake_case
    """
    string = sub('[<>]', '', string)
    return '_'.join(
        sub('([A-Z][a-z]+)', r' \1',
        sub('([A-Z]+)', r' \1',
        string.replace('-', ' '))).split()).lower()


@singledispatch
def resolve_import_path(obj: object) -> str:
    ...


@resolve_import_path.register
def _(obj: object) -> str:
    """
    """
    # TODO: docs
    base_dir = Path(sys.path[0]).parent
    file_path = getfile(obj)
    normailezed = file_path.replace(base_dir.as_posix(), "")
    normailezed = normailezed.replace("/", ".")[1:]
    normailezed = sub(r"\.py", "", normailezed)
    return normailezed


@resolve_import_path.register
def _(obj: str) -> str:
    # TODO: docs
    project_dir_name = Path(sys.path[0]).name
    if obj.startswith(project_dir_name):
        return obj
    absolute_path = f"{project_dir_name}.{obj}"
    return absolute_path


def inherits_from(child, parent_name):
    if isclass(child):
        if parent_name in [c.__name__ for c in getmro(child)[1:]]:
            return True
    return False


def get_subclasses_from_module(module_path: str,
                               superclass: type,
                               addiction_checks: List[Callable] = []
                               ) -> List[object]:
    """
    Достаёт классы-наследники из указанного модуля
    ARGS:
        module - модуль из которого тянем объекты
        superclass - класс-родитель, ищем его наследников
    """
    module_obj = import_module(module_path)
    app_module = AppModule(module_path)
    objects = []
    for key, obj in vars(module_obj).items():
        is_class = isclass(obj)
        # TODO: изменить механизм проверки
        buildin = key.startswith("__") and key.endswith("__")
        if any([buildin, not is_class]):
            continue

        # TODO:
        # из-за импорта id классов не совпадают, так что
        # inherits_from как временное решение.
        is_subclass = inherits_from(child=obj,
                                    parent_name=superclass.__name__)

        is_not_superclass = obj is not superclass
        module_absolute_path = resolve_import_path(app_module.import_path)
        imported_obj_absolute_path = resolve_import_path(obj)
        is_imported = imported_obj_absolute_path != module_absolute_path

        try:
            if all([is_subclass, is_not_superclass, not is_imported]):
                for check in addiction_checks:
                    check_result = check(obj)
                    if not check_result:
                        raise CheckFailedException(check)
                objects.append(obj)
        except CheckFailedException:
            continue
    return objects


def get_class_instances_from_module(module_path: str,
                                    cls: type,
                                    addiction_checks: List[Callable] = []
                                    ) -> List[object]:
    """
    Достаёт инстансы класса из указанного модуля
    ARGS:
        module - модуль из которого тянем объекты
        cls - класc, ищем его инстансы
    """
    module_obj = import_module(module_path)
    objects = []
    for key, obj in vars(module_obj).items():
        is_instance = type(obj) is cls

        try:
            if is_instance:
                for check in addiction_checks:
                    check_result = check(obj)
                    if not check_result:
                        raise CheckFailedException(check)
                objects.append(obj)
        except CheckFailedException:
            continue
    return objects


def check_is_not_interface(obj):
    return not isabstract(obj)


def serialize_dep_key(key: DEPENDENCY_KEY) -> str:
    return f"{resolve_import_path(key.__module__)}.{key.__name__}"


# TODO: мб перетащить в inspectors
def get_dependencies(container: ContainerT) -> DependeciesT:
    """
    Возвращает зависимости контейнера
    """
    dependencies: DependeciesT = []
    if not hasattr(container, "__annotations__"):
        return []

    for dependency_name, dependecy in container.__annotations__.items():
        # вытащить аннотацию
        # TODO: ёбнуть проверку на является ли дочерним классом 
        # какого-либо слоя
        is_type_and_subclass = (type(dependecy) in [type, ABCMeta])
        if all([is_type_and_subclass]):
            dep_key = serialize_dep_key(dependecy)
            new_dep = Dependecy(name=dependency_name, asked=dep_key)
            dependencies.append(new_dep)
    return dependencies
