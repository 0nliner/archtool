from abc import ABC, abstractmethod
from .layer import LayerInterface
from global_types import AppModule, DEPENDENCY_KEY


class DILayerInterface(LayerInterface, ABC):
    def __init__(self,
                 superclass,
                 module_name_pattern: str):

        self.superclass = superclass
        self.module_name_pattern = module_name_pattern
        # self.dependencies: dict[DEPENDENCY_KEY, object] = {}

    # @abstractmethod
    # def collect_interfaces_from_module(self, app_module: AppModule):
    #     """
    #     Собирает интерфейсы, относящиеся к данному слою приложения в модуле
    #     """

    # @abstractmethod
    # def collect_classes_from_module(self, app_module: AppModule):
    #     """
    #     Собирает классы с модуля
    #     """
