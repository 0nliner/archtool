from abc import abstractmethod
from collections.abc import Generator
from inspect import isclass

from archtool.components.default_component import ComponentPatternBase


class ValidationError(Exception): ...


def is_component_pattern_base(obj):
    return isclass(obj) and issubclass(obj, ComponentPatternBase)


class ComponentsGroupBase:
    """
    Компоненты описаные в классе Layer наследованы от этого класса
    """

    @property
    def component_patterns(self) -> list[ComponentPatternBase]:
        child_objects = dir(self)
        child_objects.remove("component_patterns")

        component_patterns = [
            getattr(self, key)
            for key in child_objects
            if is_component_pattern_base(type(getattr(self, key)))
        ]
        return component_patterns

    def __iter__(self) -> Generator[ComponentPatternBase, None, None]:
        yield from self.component_patterns


class LayerBase(type):
    def __new__(cls, name, bases, attrs, **kwargs):
        super_new = super().__new__
        parents = [b for b in bases if isinstance(b, LayerBase)]
        if not parents:
            return super_new(cls, name, bases, attrs)

        # проверяем обязательные поля
        required_fields = {"depends_on"}
        attrs_set = set(attrs.keys())
        attrs_intersection = required_fields.intersection(attrs_set)
        is_all_decleared = attrs_intersection == required_fields
        err_msg = ""

        if not is_all_decleared:
            not_defined = required_fields.difference(attrs_intersection)
            err_msg = f"Fields {not_defined} does not decleared in {attrs['__qualname__']}"

        # проверяем есть ли класс Components
        if "Components" not in attrs:
            components_err_message = "\n\nComponents child class required, but not defined"
            err_msg += components_err_message

        if err_msg:
            raise ValidationError(err_msg)

        # подготавливаем атрибуты нового класса

        # создаём новый класс, наследуем от ComponentsGroupBase
        # и уже существующего в наследнике
        components_subclass = attrs.pop("Components")
        components_class = type(
            "ComponentsGroup", (ComponentsGroupBase, components_subclass, object), {}
        )
        components_instance = components_class()

        module = attrs.pop("__module__")
        depends_on = attrs.pop("depends_on")

        new_attrs = {
            "__module__": module,
            "component_groups": components_instance,
            "Components": components_class,
            "depends_on": depends_on,
        }

        new_layer_class = super_new(cls, name, bases, new_attrs)
        new_layer_class.__new__ = super(object).__new__
        return new_layer_class

    @classmethod
    def __or__(cls, other: "LayerBase") -> frozenset:  # type: ignore[override]
        return frozenset([cls, other])

    @property
    @abstractmethod
    def component_groups(self) -> list[ComponentsGroupBase]:
        """
        Возвращает список групп компонентов, инициализированные в рамках слоя
        """


# TODO: подумать над созданием файла base.py


class Layer(metaclass=LayerBase): ...
