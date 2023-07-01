from abc import abstractmethod, ABCMeta
from archtool.layers.default_layer_interfaces import (ABCService,
                                                      ABCRepo)


class TestService2Interface(ABCService, metaclass=ABCMeta):
    @abstractmethod
    def some_buiness_logic(self):
        """
        какая-то бизнес логика, которая использует зависимости
        """


class TestRepo2Interface(ABCRepo, metaclass=ABCMeta):
    @abstractmethod
    def some_bd_logic(self):
        """
        какая-то бизнес логика, использующая базу данных и другой репозиторий
        """
