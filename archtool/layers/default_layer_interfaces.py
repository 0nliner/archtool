from abc import ABC


class ABCView(ABC):  # noqa: B024
    """
    Представление. Используйте для presentation layer
    """

    ...


class ABCController(ABC):  # noqa: B024
    ...


class ABCService(ABC):  # noqa: B024
    ...


class ABCRepo(ABC):  # noqa: B024
    ...


class ABCFacade(ABC):  # noqa: B024
    """
    Может быть использован для классов, реализующих паттерн фасад, например
    класс взаимодействующий со сторонним api
    """

    ...
