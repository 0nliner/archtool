from abc import abstractmethod, ABCMeta
from layers_interfaces import (ServiceInterface,
                               RepositoryInterface)


class TestService2Interface(ServiceInterface, metaclass=ABCMeta):
    @abstractmethod
    def some_buiness_logic(self):
        """
        какая-то бизнес логика, которая использует зависимости
        """


class TestRepo2Interface(RepositoryInterface, metaclass=ABCMeta):
    @abstractmethod
    def some_bd_logic(self):
        """
        какая-то бизнес логика, использующая базу данных и другой репозиторий
        """
