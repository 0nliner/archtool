from abc import ABC, abstractmethod
from global_types import AppModules


class BundlerInterface(ABC):
    """
    Производит сборку приложения.
    """
    @abstractmethod
    def __init__(self, app_modules: AppModules):
        """
        ARGS:
        app_modules - модули приложения
        """

    @abstractmethod
    def bundle(self):
        """
        Собирает приложение

        проходится по всем модулям.
        внутри модуля вызывает
        """
