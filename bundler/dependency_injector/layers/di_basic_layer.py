from typing import List
from inspect import isabstract

from ..interfaces.di_layer import DILayerInterface
from global_types import InterfaceT, AppModule, AppModules
from utils import get_subclasses_from_module, check_is_not_interface

from ..exceptions import (MultipleRealizationsException,
                          RealizationNotFount)


class DILayer(DILayerInterface):
    def get_module_interfaces(self, module: AppModule) -> List[InterfaceT]:
        layer_module_path = f"{module.import_path}.interfaces"
        results = get_subclasses_from_module(module_path=layer_module_path,
                                             superclass=self.superclass,
                                             addiction_checks=[isabstract])

        return results

    def get_interface_realization(self,
                                  module: AppModule,
                                  interface: InterfaceT) -> type:
        """
        Достаёт реализацию интерфейса в рамках модуля слоя
        """
        module_path = f"{module.import_path}.{self.module_name_pattern}"
        module_layer_objects = get_subclasses_from_module(
            module_path=module_path,
            superclass=interface,
            addiction_checks=[check_is_not_interface])

        realizations_found = len(module_layer_objects)
        if realizations_found > 1:
            raise MultipleRealizationsException(str(f"{module:}\n\n",
                                                    f"{interface:}\n\n",
                                                    f"{module_layer_objects:}"))

        elif not realizations_found:
            raise RealizationNotFount((f"{module:}\n",
                                       f"{interface:}\n"))

        interface_realization = module_layer_objects[0]
        return interface_realization

    def get_all_interfaces(self, app_modules: AppModules):
        """
        Достаёт все интерфейсы слоя из перечисленных модулей
        """
        interfaces = []
        for module in app_modules:
            module_interfaces = self.get_module_interfaces(module=module)
            interfaces.extend(module_interfaces)
        return interfaces

    def get_all_interfaces_and_realizations(self, app_modules
                                            ) -> dict[InterfaceT, type]:
        interfaces_to_realizations = {}
        for module in app_modules:
            interfaces = self.get_module_interfaces(module=module)
            for interface in interfaces:
                # TODO: добавить валидацию на отсутствие None значений выше

                # ошибки тут игнорить и пропускать говёные интерфейсы из 
                # других модулей

                # либо ещё поресёрчить как узнать модуль, где описан объект,
                # но сомнительно

                # ещё можно попробовать вытащить все импортированные объекы,
                # сделать diff, пройтись по всем объектам, которые
                # задекларированы в файле, а не импортнуты
                realization = self.get_interface_realization(module=module,
                                                             interface=interface)
                interfaces_to_realizations.update({interface: realization})

        return interfaces_to_realizations
