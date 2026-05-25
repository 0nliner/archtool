from archtool.components.default_component import ComponentPattern
from archtool.layers import Layer
from archtool.layers.default_layer_interfaces import ABCController, ABCRepo, ABCService, ABCView

# TODO:
# class ComponentsModule:
#     """
#     Импортируемый объект хранит внутри себя только интерфейсы и их
#     реализации. Нужен для работы с фасадами апишки
#     """
#     def __init__(self, module_import_path: str):
#         self.module_import_path = module_import_path


class InfrastructureLayer(Layer):
    """
    Слой инфраструктуры
    """

    depends_on = None

    class Components:
        repos = ComponentPattern(module_name_regex="repos", superclass=ABCRepo)

        #  TODO:
        # integrations = ComponentsModule(module_import_path=)


class DomainLayer(Layer):
    """
    Слой бизнеслогики
    """

    depends_on = InfrastructureLayer

    class Components:
        services = ComponentPattern(module_name_regex="services", superclass=ABCService)


class ApplicationLayer(Layer):
    """
    Слой приложения
    """

    depends_on = DomainLayer

    class Components:
        controllers = ComponentPattern(module_name_regex="controllers", superclass=ABCController)


class PresentationLayer(Layer):
    """
    Слой отображения
    """

    depends_on = ApplicationLayer

    class Components:
        views = ComponentPattern(module_name_regex="views", superclass=ABCView)


# Ordered from outermost to innermost so inject() processes them top-down.
# Must be a list (not frozenset) to guarantee stable iteration order.
default_layers = [
    PresentationLayer,
    ApplicationLayer,
    DomainLayer,
    InfrastructureLayer,
]
