from injector.layers import DILayer

from layers_interfaces import (
    ServiceInterface,
    RepositoryInterface)


class ServicesLayer(DILayer):
    def __init__(self,
                 module_name_pattern: str = "services"):
        super(ServicesLayer, self).__init__(
            module_name_pattern=module_name_pattern,
            superclass=ServiceInterface)

        self.depends_on = ReposLayer


class ReposLayer(DILayer):
    def __init__(self, module_name_pattern: str = "repos"):
        super(ReposLayer, self).__init__(
            module_name_pattern=module_name_pattern,
            superclass=RepositoryInterface)


class ModelsLayer(DILayer):
    def __init__(self, module_name_pattern: str = "models"):
        ...
